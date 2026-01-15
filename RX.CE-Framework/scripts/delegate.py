#!/usr/bin/env python3
"""
Delegation Wrapper - MANDATORY for all Hub Agent -> Subagent delegations.

This wrapper enforces state machine protocol and prevents Hub Agent from
bypassing the workflow engine. All subagent calls MUST go through these functions.
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from workflow_engine import WorkflowEngine


def delegate_to_agent(story_id: str, agent: str, task_description: str,
                      lane_name: str = 'main') -> Dict:
    """
    Start delegation and prepare for subagent invocation.

    Args:
        story_id: Story ID (e.g., "story-001")
        agent: Agent name (e.g., "backend-agent", "frontend-agent")
        task_description: Brief description of task for logging
        lane_name: Lane name for parallel work (default: 'main')

    Returns:
        dict with success, txn_id (if success), error (if failure)
    """
    engine = WorkflowEngine()

    print(f"\n{'='*60}")
    print(f"[DELEGATION START] {story_id} -> {agent}")
    print(f"{'='*60}")

    # 1. Check if story exists
    story_status = engine.get_story_status(story_id)
    if not story_status:
        print(f"[ERROR] Story {story_id} not found in state machine")
        return {
            "success": False,
            "error": f"Story {story_id} not found in state machine. Register it first."
        }

    current_phase = story_status['phase']
    print(f"   Current phase: [{current_phase}]")

    # 2. Check dependencies
    conn = engine._get_conn()
    try:
        blocked = not engine._check_dependencies(conn, story_id)
        if blocked:
            blockers = engine._get_blocking_stories(conn, story_id)
            print(f"[ERROR] Story blocked by: {', '.join(blockers)}")
            return {
                "success": False,
                "error": f"Story {story_id} blocked by: {', '.join(blockers)}"
            }
    finally:
        conn.close()

    print(f"   Dependencies: OK")

    # 3. Start delegation transaction (workflow engine determines target phase)
    result = engine.hub_start_delegation(
        story_id=story_id,
        to_agent=agent,
        lane_name=lane_name
    )

    if not result.success:
        print(f"[ERROR] Delegation failed: {result.error}")
        return {
            "success": False,
            "error": result.error
        }

    txn_id = result.txn_id

    # 4. Get the to_phase from the delegation we just created
    conn = engine._get_conn()
    try:
        delegation = conn.execute("""
            SELECT to_phase FROM delegations WHERE txn_id = ?
        """, (txn_id,)).fetchone()
        to_phase = delegation['to_phase'] if delegation else 'Unknown'
    finally:
        conn.close()

    print(f"[OK] Delegation transaction opened: {txn_id}")
    print(f"   From: [{current_phase}] -> To: [{to_phase}]")
    print(f"   Agent: {agent}")
    print(f"   Lane: {lane_name}")

    # 5. Write delegation marker to story file
    _write_delegation_marker(story_id, txn_id, agent, current_phase, to_phase)

    print(f"\n[READY] Call Task tool with subagent_type='{agent}'")
    print(f"{'='*60}\n")

    return {
        "success": True,
        "txn_id": txn_id,
        "agent": agent,
        "from_phase": current_phase,
        "to_phase": to_phase,
        "story_id": story_id,
        "lane_name": lane_name
    }


def complete_delegation(txn_id: str, story_id: str, agent: str) -> Dict:
    """
    Complete delegation after subagent finishes work.
    Verifies evidence, context feedback, and advances story phase.

    Args:
        txn_id: Transaction ID from delegate_to_agent()
        story_id: Story ID
        agent: Agent name

    Returns:
        dict with success, message (if success), error (if failure)
    """
    engine = WorkflowEngine()

    print(f"\n{'='*60}")
    print(f"[DELEGATION COMPLETE] {story_id} <- {agent}")
    print(f"{'='*60}")

    # 1. Verify agent evidence in story file
    print("1. Verifying agent evidence...")
    found, evidence_hash, location = engine.verify_agent_evidence(story_id, agent)

    if not found:
        print(f"[ERROR] No evidence found from {agent}")
        engine.hub_fail_delegation(txn_id, "No evidence found in story file")
        return {
            "success": False,
            "error": "Agent did not provide evidence section in story file"
        }

    print(f"   [OK] Evidence found: {location}")
    print(f"   Hash: {evidence_hash}")

    # 2. Verify Context Feedback section exists
    print("2. Verifying Context Feedback...")
    story_path = Path(f"stories/{story_id}.md")

    if not story_path.exists():
        engine.hub_fail_delegation(txn_id, "Story file not found")
        return {
            "success": False,
            "error": f"Story file not found: {story_path}"
        }

    story_content = story_path.read_text()

    if '## Context Feedback' not in story_content:
        print(f"[ERROR] Missing Context Feedback section")
        engine.hub_fail_delegation(txn_id, "Missing required Context Feedback section")
        return {
            "success": False,
            "error": "Agent must provide Context Feedback section"
        }

    print("   [OK] Context Feedback section found")

    # 3. Parse and validate feedback structure
    print("3. Parsing Context Feedback...")
    feedback = engine.parse_context_feedback(story_id)

    if not feedback:
        print(f"[ERROR] Context Feedback section malformed")
        engine.hub_fail_delegation(txn_id, "Malformed Context Feedback section")
        return {
            "success": False,
            "error": "Context Feedback section exists but is malformed"
        }

    print(f"   [OK] Feedback parsed successfully")

    # 4. Store feedback in database
    print("4. Storing feedback in database...")
    result = engine.store_context_feedback(story_id=story_id, agent=agent)

    if not result.success:
        print(f"   [WARN] Failed to store feedback: {result.error}")
        # Continue anyway - feedback is in story file
    else:
        print("   [OK] Feedback stored")

    # 5. Store issues encountered (optional)
    issues_result = engine.store_issues_encountered(story_id=story_id, agent=agent)
    if issues_result.metadata and issues_result.metadata.get('issue_count', 0) > 0:
        print(f"   [OK] Stored {issues_result.metadata['issue_count']} issues for learning")

    # 6. Complete delegation (advances phase)
    print("5. Completing delegation transaction...")
    result = engine.hub_complete_delegation(
        txn_id=txn_id,
        evidence_hash=evidence_hash,
        evidence_location=location
    )

    if not result.success:
        print(f"[ERROR] Failed to complete delegation: {result.error}")
        return {
            "success": False,
            "error": result.error
        }

    # 7. Update delegation marker in story file
    _update_delegation_marker(story_id, txn_id, evidence_hash)

    print(f"[OK] Delegation completed successfully")
    print(f"   {result.message}")
    print(f"{'='*60}\n")

    return {
        "success": True,
        "message": result.message,
        "txn_id": txn_id
    }


def _write_delegation_marker(story_id: str, txn_id: str, agent: str,
                             from_phase: str, to_phase: str):
    """Write delegation marker to story file for subagent validation."""
    story_path = Path(f"stories/{story_id}.md")
    if not story_path.exists():
        print(f"   [WARN] Story file not found: {story_path}")
        return

    content = story_path.read_text()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Check if Delegation History section exists
    if "## Delegation History" not in content:
        # Add section after story header
        marker = f"""
## Delegation History

- [ ] [{from_phase}] -> [{to_phase}]: `{txn_id}` by {agent} ({timestamp}) IN PROGRESS
  - Status: PENDING_COMPLETION
  - Evidence: NOT YET PROVIDED

"""
        # Insert after first heading
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('#'):
                insert_pos = i + 1
                break

        lines.insert(insert_pos, marker)
        content = '\n'.join(lines)
    else:
        # Append to existing section
        marker = f"- [ ] [{from_phase}] -> [{to_phase}]: `{txn_id}` by {agent} ({timestamp}) IN PROGRESS\n  - Status: PENDING_COMPLETION\n  - Evidence: NOT YET PROVIDED\n"

        # Find Delegation History section and append
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('## Delegation History'):
                # Insert after this line (skip empty line)
                lines.insert(i + 2, marker)
                break

        content = '\n'.join(lines)

    story_path.write_text(content)
    print(f"   [OK] Delegation marker written to story file")


def _update_delegation_marker(story_id: str, txn_id: str, evidence_hash: str):
    """Update delegation marker to show completion."""
    story_path = Path(f"stories/{story_id}.md")
    if not story_path.exists():
        return

    content = story_path.read_text()

    # Find and update the delegation marker
    if txn_id in content:
        content = content.replace(
            f"`{txn_id}` by",
            f"`{txn_id}` [COMPLETED] by"
        )
        content = content.replace(
            "IN PROGRESS\n  - Status: PENDING_COMPLETION\n  - Evidence: NOT YET PROVIDED",
            f"COMPLETED\n  - Status: COMPLETED\n  - Evidence: {evidence_hash}"
        )
        # Change checkbox to checked
        content = content.replace(f"- [ ] ", "- [x] ", 1) if f"`{txn_id}`" in content else content

        story_path.write_text(content)


if __name__ == "__main__":
    # CLI interface for testing
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python delegate.py start <story_id> <agent> <description>")
        print("  python delegate.py complete <txn_id> <story_id> <agent>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        if len(sys.argv) < 5:
            print("Usage: python delegate.py start <story_id> <agent> <description>")
            sys.exit(1)
        result = delegate_to_agent(sys.argv[2], sys.argv[3], sys.argv[4])
        print(result)
    elif command == "complete":
        if len(sys.argv) < 5:
            print("Usage: python delegate.py complete <txn_id> <story_id> <agent>")
            sys.exit(1)
        result = complete_delegation(sys.argv[2], sys.argv[3], sys.argv[4])
        print(result)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
