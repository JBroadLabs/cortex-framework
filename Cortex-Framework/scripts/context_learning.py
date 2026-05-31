#!/usr/bin/env python3
"""
Context learning utilities for Hub Agent.
Handles automatic triggering of Reflector Agent every 10 stories.
"""

import sys
import hashlib
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from workflow_engine import WorkflowEngine


def check_and_trigger_reflector(story_id):
    """
    Check if reflector should be triggered and trigger if needed.
    Called after any story reaches [Done] phase.

    Args:
        story_id: ID of story that just completed

    Returns:
        dict: Result with keys:
              - triggered: bool, whether reflector was triggered
              - batch_num: int, batch number if triggered
              - message: str, status message
    """
    engine = WorkflowEngine()

    # Record completion and check if reflector should trigger
    result = engine.record_story_completion(story_id)

    if not result.metadata or not result.metadata.get('should_trigger_reflector'):
        return {
            'triggered': False,
            'message': f"Story {story_id} completed, not yet time for reflection"
        }

    # Extract batch information
    batch_num = result.metadata['batch_number']
    start_story = result.metadata['story_range_start']
    end_story = result.metadata['story_range_end']

    # Start reflector delegation
    print("\n" + "="*60)
    print("CONTEXT LEARNING TRIGGERED")
    print("="*60)
    print(f"Batch #{batch_num}")
    print(f"Stories: story-{start_story:03d} through story-{end_story:03d}")
    print(f"Outputs:")
    print(f"  - docs/context-deltas-batch-{batch_num}.md")
    print(f"  - docs/troubleshooting-updates-batch-{batch_num}.md")
    print("="*60 + "\n")

    # Delegate to reflector agent
    from delegate import delegate_to_agent

    reflector_story_id = f"reflector-batch-{batch_num}"

    # Start delegation
    delegation = delegate_to_agent(
        story_id=reflector_story_id,
        agent="reflector-agent",
        task_description=f"Analyze context feedback from stories {start_story}-{end_story}"
    )

    if not delegation["success"]:
        print(f"[X] Failed to start reflector delegation: {delegation['error']}")
        return {
            'triggered': False,
            'message': f"Failed to trigger reflector: {delegation['error']}"
        }

    txn_id = delegation["txn_id"]

    # Note: Hub Agent must call Task tool here to actually invoke reflector
    # Then after reflector completes, call complete_delegation()

    return {
        'triggered': True,
        'batch_num': batch_num,
        'txn_id': txn_id,
        'start_story': start_story,
        'end_story': end_story,
        'message': f"Reflector triggered for batch {batch_num}"
    }


def complete_reflector_workflow(txn_id, batch_num):
    """
    Complete reflector workflow after agent finishes.

    Args:
        txn_id: Transaction ID from check_and_trigger_reflector
        batch_num: Batch number being processed

    Returns:
        dict: Result of completion
    """
    from delegate import complete_delegation

    # Verify delta files exist
    context_delta_file = Path(f"docs/context-deltas-batch-{batch_num}.md")
    troubleshooting_delta_file = Path(f"docs/troubleshooting-updates-batch-{batch_num}.md")

    if not context_delta_file.exists():
        return {
            'success': False,
            'error': f"Context delta file not found: {context_delta_file}"
        }

    # Present deltas to user (HITL gate)
    context_content = context_delta_file.read_text(encoding='utf-8')
    context_delta_count = len(re.findall(r'\[ \] APPROVED', context_content))

    troubleshooting_delta_count = 0
    if troubleshooting_delta_file.exists():
        troubleshooting_content = troubleshooting_delta_file.read_text(encoding='utf-8')
        troubleshooting_delta_count = len(re.findall(r'\[ \] APPROVED', troubleshooting_content))

    print("\n" + "="*60)
    print("IMPROVEMENTS READY FOR REVIEW")
    print("="*60)
    print(f"\nDocumentation Improvements:")
    print(f"   File: docs/context-deltas-batch-{batch_num}.md")
    print(f"   Deltas: {context_delta_count} proposed")

    if troubleshooting_delta_count > 0:
        print(f"\nTroubleshooting Updates:")
        print(f"   File: docs/troubleshooting-updates-batch-{batch_num}.md")
        print(f"   Issues: {troubleshooting_delta_count} patterns documented")
    else:
        print(f"\nTroubleshooting Updates:")
        print(f"   No new issues this batch (all went smoothly!)")

    print("\nInstructions:")
    print("1. Open BOTH delta files in your editor")
    print("2. Review each proposed change carefully")
    print("3. Mark your decisions:")
    print("   [x] APPROVED  - Apply this change")
    print("   [ ] REJECTED  - Skip this change")
    print("4. Save both files")
    print("5. Run: python scripts/apply_deltas.py <file>")
    print("="*60 + "\n")

    # Complete reflector delegation
    reflector_story_id = f"reflector-batch-{batch_num}"

    result = complete_delegation(
        txn_id=txn_id,
        story_id=reflector_story_id,
        agent="reflector-agent"
    )

    return result


if __name__ == "__main__":
    # Test reflector check
    if len(sys.argv) < 2:
        print("Usage: python context_learning.py <story_id>")
        sys.exit(1)

    story_id = sys.argv[1]
    result = check_and_trigger_reflector(story_id)
    print(result)
