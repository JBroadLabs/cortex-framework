#!/usr/bin/env python3
"""
Mode detection and routing utilities for Hub Agent.
Determines workflow mode and routes to appropriate agents.
"""

import os
from pathlib import Path


def detect_mode(triggered_by):
    """
    Determine operating mode from command context.

    Args:
        triggered_by: Command that triggered Hub Agent
                     ('/greenfield', '/story', '/refactor', '/ask')

    Returns:
        tuple: (mode, workflow_doc_path) where mode is one of:
               'greenfield', 'incremental', 'refactor', 'advisory'
    """
    if triggered_by == '/greenfield':
        mode = 'greenfield'
        workflow_doc = 'RX.CE-Framework/modes/Greenfield.md'
        print("Mode: Greenfield (Full POC)")

    elif triggered_by == '/story':
        mode = 'incremental'
        workflow_doc = 'RX.CE-Framework/modes/Brownfield.md'
        print("Mode: Incremental (Feature addition)")

    elif triggered_by == '/refactor':
        mode = 'refactor'
        workflow_doc = 'RX.CE-Framework/modes/Brownfield.md'
        print("Mode: Refactor (Technical debt reduction)")

    elif triggered_by == '/ask':
        mode = 'advisory'
        workflow_doc = None
        print("Mode: Advisory (Read-only assistance)")
        return mode, workflow_doc

    else:
        raise ValueError(
            f"Unknown command: {triggered_by}. "
            "Use /greenfield, /story, /refactor, or /ask"
        )

    # Verify workflow document exists
    if workflow_doc and not Path(workflow_doc).exists():
        raise FileNotFoundError(f"Workflow document not found: {workflow_doc}")

    return mode, workflow_doc


def route_to_agent(mode, user_request=None):
    """
    Route to specialized agent based on mode and current project state.

    Args:
        mode: Operating mode ('greenfield', 'incremental', 'refactor', 'advisory')
        user_request: Optional user request text

    Returns:
        dict: Routing information with keys:
              - target_agent: Which agent to call
              - purpose: Why this agent
              - next_phase: What comes after
    """

    if mode == 'greenfield':
        # Full POC workflow - multi-phase

        # Phase 1: Design
        if not _design_docs_exist():
            return {
                'target_agent': 'system-design-agent',
                'purpose': 'Create design documents',
                'next_phase': 'HITL approval'
            }

        # Phase 2: After HITL approval, sharding done by System Design Agent
        if not _sharding_complete():
            return {
                'target_agent': 'system-design-agent',
                'purpose': 'Shard approved documents',
                'next_phase': 'Story creation'
            }

        # Phase 3: Story creation
        if not _stories_exist():
            return {
                'target_agent': 'story-composer-agent',
                'purpose': 'Create stories from approved design',
                'next_phase': 'Implementation'
            }

        # Phase 4: Implementation
        return {
            'target_agent': 'implementation-agents',
            'purpose': 'Implement stories',
            'next_phase': 'State machine execution'
        }

    elif mode == 'incremental':
        # Check for brownfield analysis first
        if not os.path.exists('analysis/brownfield-architecture.md'):
            return {
                'target_agent': 'brownfield-architect-agent',
                'purpose': 'Analysis-only mode (for Story Composer context)',
                'next_phase': 'Story Composer creates feature stories'
            }
        else:
            return {
                'target_agent': 'story-composer-agent',
                'purpose': 'Create feature stories using existing patterns',
                'next_phase': 'Story implementation'
            }

    elif mode == 'refactor':
        # Full refactoring workflow
        return {
            'target_agent': 'brownfield-architect-agent',
            'purpose': 'Full refactor mode (analysis + plan + stories)',
            'next_phase': 'HITL approval, then sharding, then implementation'
        }

    elif mode == 'advisory':
        return {
            'target_agent': 'ask-agent',
            'purpose': 'Read-only framework assistance',
            'next_phase': 'None (advisory only)'
        }

    else:
        raise ValueError(f"Unknown mode: {mode}")


def _design_docs_exist():
    """Check if design documents exist."""
    return (
        Path('docs/spec.md').exists() and
        Path('docs/architecture.md').exists()
    )


def _sharding_complete():
    """Check if design documents have been sharded."""
    return (
        Path('docs/shard-index.md').exists() and
        Path('docs/frontend/index.md').exists() and
        Path('docs/backend/index.md').exists()
    )


def _stories_exist():
    """Check if stories have been created."""
    stories_dir = Path('stories')
    if not stories_dir.exists():
        return False

    story_files = list(stories_dir.glob('story-*.md'))
    return len(story_files) > 0


if __name__ == "__main__":
    # Test mode detection
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mode_router.py <command>")
        print("Example: python mode_router.py /greenfield")
        sys.exit(1)

    command = sys.argv[1]
    mode, workflow_doc = detect_mode(command)
    routing = route_to_agent(mode)

    print(f"\nMode: {mode}")
    print(f"Workflow: {workflow_doc}")
    print(f"Route to: {routing['target_agent']}")
    print(f"Purpose: {routing['purpose']}")
