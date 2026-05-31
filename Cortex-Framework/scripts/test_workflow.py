#!/usr/bin/env python3
"""Test script for workflow engine"""

import sys
sys.path.insert(0, '.')

from scripts.workflow_engine import WorkflowEngine

def test_delegation_workflow():
    """Test the delegation workflow"""
    engine = WorkflowEngine()

    print("\n=== Testing Delegation Workflow ===\n")

    # Test 1: Start delegation for story-001
    print("1. Starting delegation to frontend-agent...")
    result = engine.hub_start_delegation("story-001", "frontend-agent")
    if result.success:
        print(f"   [OK] {result.message}")
        print(f"   Transaction ID: {result.txn_id}")
        txn_id = result.txn_id
    else:
        print(f"   [FAIL] {result.error}")
        return

    # Test 2: Try to start another delegation (should fail)
    print("\n2. Trying to start another delegation (should fail)...")
    result = engine.hub_start_delegation("story-001", "backend-agent")
    if not result.success:
        print(f"   [OK] Correctly rejected: {result.error}")
    else:
        print(f"   [FAIL] Should have been rejected!")

    # Test 3: Check pending delegations
    print("\n3. Checking pending delegations...")
    pending = engine.hub_get_pending_delegations()
    if len(pending) == 1:
        print(f"   [OK] Found 1 pending delegation")
        print(f"       Story: {pending[0].story_id}")
        print(f"       Agent: {pending[0].agent}")
    else:
        print(f"   [FAIL] Expected 1 pending, found {len(pending)}")

    # Test 4: Try to complete delegation without evidence (should fail)
    print("\n4. Trying to complete delegation without evidence (should fail)...")
    result = engine.hub_complete_delegation(txn_id, "")
    if not result.success:
        print(f"   [OK] Correctly rejected: {result.error}")
    else:
        print(f"   [FAIL] Should have been rejected!")

    # Test 5: Complete delegation with evidence
    print("\n5. Completing delegation with evidence...")
    result = engine.hub_complete_delegation(txn_id, "test_hash_123", "### Implementation Notes")
    if result.success:
        print(f"   [OK] {result.message}")
    else:
        print(f"   [FAIL] {result.error}")

    # Test 6: Check story status
    print("\n6. Checking story status...")
    status = engine.get_story_status("story-001")
    if status and status['phase'] == 'I':
        print(f"   [OK] Story is now in [{status['phase']}] phase")
    else:
        print(f"   [FAIL] Expected phase [I], got {status['phase'] if status else 'None'}")

    # Test 7: Check next actions
    print("\n7. Checking next actions...")
    action = engine.hub_get_next_action("story-001")
    if action and action.next_agent == 'code-review-agent':
        print(f"   [OK] Next agent is {action.next_agent}")
    else:
        print(f"   [FAIL] Expected code-review-agent, got {action.next_agent if action else 'None'}")

    # Test 8: View audit log
    print("\n8. Checking audit log...")
    audit = engine.get_audit_log("story-001", limit=10)
    print(f"   [OK] Found {len(audit)} audit entries:")
    for entry in audit:
        print(f"       - {entry['event_type']}: {entry['from_state']} -> {entry['to_state']}")

    print("\n=== All Tests Completed ===\n")

if __name__ == "__main__":
    test_delegation_workflow()
