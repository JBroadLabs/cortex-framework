#!/usr/bin/env python3
"""
Delegation validation for subagents.
Subagents call this to verify they were properly delegated.
"""

import sys
from pathlib import Path


def validate_delegation(story_id: str, agent_name: str) -> bool:
    """
    Validate that this agent was properly delegated for this story.

    Returns True if validation passes, False otherwise.
    Prints detailed error messages if validation fails.
    """
    print(f"\n{'='*60}")
    print(f"[PRE-FLIGHT CHECK] {agent_name} on {story_id}")
    print(f"{'='*60}")

    # 1. Check story file exists
    story_path = Path(f"stories/{story_id}.md")
    if not story_path.exists():
        print(f"[FATAL] Story file not found: {story_path}")
        print("   Hub Agent must register story before delegation")
        return False

    print(f"[OK] Story file exists: {story_path}")

    # 2. Read story content
    content = story_path.read_text()

    # 3. Check for Delegation History section
    if "## Delegation History" not in content:
        print("[FATAL] No Delegation History section found")
        print("   Hub Agent must use delegate_to_agent() before calling Task")
        print("   This story was not properly delegated")
        return False

    print("[OK] Delegation History section exists")

    # 4. Check for active delegation for this agent
    if agent_name not in content:
        print(f"[FATAL] No delegation found for {agent_name}")
        print("   Hub Agent must delegate to THIS agent specifically")
        return False

    if "IN PROGRESS" not in content:
        print("[FATAL] No active delegation in progress")
        print("   All delegations are either completed or failed")
        return False

    # 5. Verify this agent has an active delegation
    lines = content.split('\n')
    found_active = False

    for line in lines:
        if agent_name in line and "IN PROGRESS" in line:
            found_active = True
            print(f"[OK] Active delegation found for {agent_name}")
            break

    if not found_active:
        print(f"[FATAL] No active delegation for {agent_name}")
        print(f"   Found {agent_name} in history but not marked as IN PROGRESS")
        return False

    print(f"{'='*60}")
    print(f"[OK] PRE-FLIGHT CHECK PASSED")
    print(f"   {agent_name} is authorized to work on {story_id}")
    print(f"{'='*60}\n")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_delegation.py <story_id> <agent_name>")
        sys.exit(1)

    story_id = sys.argv[1]
    agent_name = sys.argv[2]

    if validate_delegation(story_id, agent_name):
        sys.exit(0)
    else:
        sys.exit(1)
