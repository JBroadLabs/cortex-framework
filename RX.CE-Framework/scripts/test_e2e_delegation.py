#!/usr/bin/env python3
"""End-to-end test of delegation wrapper with state machine."""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from delegate import delegate_to_agent, complete_delegation
from workflow_engine import WorkflowEngine


def setup_test_story():
    """Create a test story file."""
    story_path = Path("stories/story-e2e-test.md")
    story_path.parent.mkdir(exist_ok=True)

    content = """# E2E Test Story

**Status**: [Pending]
**Type**: [BE]
**Dependencies**: None

## Description
Test story for end-to-end delegation validation.

## Tasks / Subtasks
- [ ] Task 1
- [ ] Task 2

## Review & Testing Notes
(Will be updated by agents)
"""
    story_path.write_text(content, encoding='utf-8')
    print(f"   [OK] Story file created: {story_path}")

    # Register in state machine
    engine = WorkflowEngine()
    result = engine.register_story(
        story_id="story-e2e-test",
        title="E2E Test Story",
        story_file_path="stories/story-e2e-test.md"
    )

    if result.success:
        print(f"   [OK] Story registered in state machine")
    else:
        if "UNIQUE constraint failed" in str(result.error):
            print(f"   [~] Story already registered")
            return True
        print(f"   [ERROR] Registration failed: {result.error}")
        return False

    return True


def simulate_agent_work(story_id: str, agent: str):
    """Simulate agent completing work."""
    story_path = Path(f"stories/{story_id}.md")
    content = story_path.read_text(encoding='utf-8')

    # Add evidence section
    evidence = f"""

### Implementation Notes

**Implementer**: {agent}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: COMPLETED

**Summary**: Test implementation completed successfully

**Files Modified/Created**:
- test/file.py - Test file

**Key Changes**:
Test changes for delegation wrapper validation

**Next Steps**: Ready for Code Review [CR]
"""

    content += evidence

    # Add Context Feedback
    feedback = """

## Context Feedback

**Helpful**: docs/test.md
**Misleading**: None
**Missing**: None
"""

    content += feedback
    story_path.write_text(content, encoding='utf-8')
    print(f"   [OK] Simulated agent work complete")


def cleanup_test_story():
    """Remove test story file and database entry."""
    story_path = Path("stories/story-e2e-test.md")
    if story_path.exists():
        story_path.unlink()
        print(f"   [OK] Test story file removed")


def test_complete_flow():
    """Test complete delegation flow."""
    print("\n" + "="*60)
    print("E2E DELEGATION WRAPPER TEST")
    print("="*60 + "\n")

    # Setup
    print("1. Setting up test story...")
    if not setup_test_story():
        print("[ERROR] Failed to setup test story")
        return False
    print()

    # Test delegation start
    print("2. Starting delegation...")
    result = delegate_to_agent(
        story_id="story-e2e-test",
        agent="backend-agent",
        task_description="E2E test"
    )

    if not result["success"]:
        print(f"[ERROR] Delegation start failed: {result['error']}")
        return False

    txn_id = result["txn_id"]
    print(f"   [OK] Delegation started: {txn_id}\n")

    # Simulate agent work
    print("3. Simulating agent work...")
    simulate_agent_work("story-e2e-test", "backend-agent")
    print()

    # Complete delegation
    print("4. Completing delegation...")
    completion = complete_delegation(
        txn_id=txn_id,
        story_id="story-e2e-test",
        agent="backend-agent"
    )

    if not completion["success"]:
        print(f"[ERROR] Delegation completion failed: {completion['error']}")
        return False

    print(f"   [OK] Delegation completed: {completion['message']}\n")

    # Verify story phase advanced
    print("5. Verifying story phase...")
    engine = WorkflowEngine()
    status = engine.get_story_status("story-e2e-test")

    if status and status['phase'] == 'I':
        print(f"   [OK] Story phase advanced to [I]\n")
        print("="*60)
        print("E2E TEST PASSED")
        print("="*60 + "\n")
        return True
    else:
        print(f"[ERROR] Story phase incorrect: {status['phase'] if status else 'None'}")
        return False


def test_validation_script():
    """Test the validation script independently."""
    print("\n" + "="*60)
    print("VALIDATION SCRIPT TEST")
    print("="*60 + "\n")

    from validate_delegation import validate_delegation

    # First, create a story with delegation marker
    print("1. Creating test story with delegation marker...")
    story_path = Path("stories/story-validation-test.md")
    story_path.parent.mkdir(exist_ok=True)

    content = """# Validation Test Story

## Delegation History

- [ ] [Pending] -> [I]: `test-txn-123` by backend-agent (2024-01-15 10:00) IN PROGRESS
  - Status: PENDING_COMPLETION
  - Evidence: NOT YET PROVIDED

## Description
Test story for validation script.
"""
    story_path.write_text(content, encoding='utf-8')
    print(f"   [OK] Story created with delegation marker\n")

    # Test successful validation
    print("2. Testing successful validation...")
    result = validate_delegation("story-validation-test", "backend-agent")

    if result:
        print("   [OK] Validation passed as expected\n")
    else:
        print("   [ERROR] Validation failed unexpectedly\n")
        return False

    # Test failed validation (wrong agent)
    print("3. Testing failed validation (wrong agent)...")
    result = validate_delegation("story-validation-test", "frontend-agent")

    if not result:
        print("   [OK] Validation correctly rejected wrong agent\n")
    else:
        print("   [ERROR] Validation should have failed\n")
        return False

    # Cleanup
    story_path.unlink()
    print("4. Test cleanup complete\n")

    print("="*60)
    print("VALIDATION SCRIPT TEST PASSED")
    print("="*60 + "\n")

    return True


def test_delegation_without_story():
    """Test delegation fails gracefully without story."""
    print("\n" + "="*60)
    print("ERROR HANDLING TEST")
    print("="*60 + "\n")

    print("1. Testing delegation to non-existent story...")
    result = delegate_to_agent(
        story_id="story-nonexistent",
        agent="backend-agent",
        task_description="Should fail"
    )

    if not result["success"]:
        print(f"   [OK] Correctly rejected: {result['error']}\n")
        print("="*60)
        print("ERROR HANDLING TEST PASSED")
        print("="*60 + "\n")
        return True
    else:
        print("   [ERROR] Should have failed but succeeded\n")
        return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# DELEGATION WRAPPER E2E TEST SUITE")
    print("#"*60)

    all_passed = True

    # Test 1: Error handling
    if not test_delegation_without_story():
        all_passed = False

    # Test 2: Validation script
    if not test_validation_script():
        all_passed = False

    # Test 3: Complete flow
    if not test_complete_flow():
        all_passed = False

    print("\n" + "#"*60)
    if all_passed:
        print("# ALL TESTS PASSED")
        print("#"*60 + "\n")
        sys.exit(0)
    else:
        print("# SOME TESTS FAILED")
        print("#"*60 + "\n")
        sys.exit(1)
