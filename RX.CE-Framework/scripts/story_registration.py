#!/usr/bin/env python3
"""
Story registration utilities for Hub Agent.
Handles automatic registration of stories created by Story Composer.
"""

import re
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from workflow_engine import WorkflowEngine


def ensure_state_machine_initialized():
    """Initialize state machine if it doesn't exist."""
    db_path = Path('RX.CE-Framework/state/workflow.db')

    if not db_path.exists():
        print("[!] State machine not initialized, creating...")
        result = subprocess.run(
            ['python', 'RX.CE-Framework/scripts/workflow_engine.py', 'init'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[OK] State machine initialized")
        else:
            print(f"[X] Failed to initialize: {result.stderr}")
            raise RuntimeError("Cannot proceed without state machine")
    else:
        print("[OK] State machine exists")


def register_stories_from_composer():
    """
    Register all stories created by Story Composer into the state machine.
    Must be called immediately after Story Composer reports completion.

    Returns:
        int: Number of stories registered
    """
    engine = WorkflowEngine()
    stories_dir = Path('stories')

    if not stories_dir.exists():
        print("[!] No stories directory found")
        return 0

    registered_count = 0
    skipped_count = 0

    for story_file in sorted(stories_dir.glob('story-*.md')):
        story_id = story_file.stem

        # Check if already registered
        existing = engine.get_story_status(story_id)
        if existing:
            print(f"[~] {story_id} already registered (phase: {existing['phase']})")
            skipped_count += 1
            continue

        # Extract title from markdown
        content = story_file.read_text(encoding='utf-8')

        # Find first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Limit to 200 chars for database
            title = title[:200]
        else:
            title = story_id

        # Register in state machine
        result = engine.register_story(
            story_id=story_id,
            title=title,
            story_file_path=f"stories/{story_id}.md"
        )

        if result.success:
            print(f"[OK] Registered {story_id}: {title}")
            registered_count += 1
        else:
            print(f"[X] Failed to register {story_id}: {result.error}")

    print(f"\n[Summary] Registered: {registered_count}, Skipped: {skipped_count}")
    return registered_count


def parse_and_sync_dependencies():
    """
    Parse dependencies from story markdown files and sync to database.
    Handles both inline and detailed dependency formats.

    Returns:
        int: Number of dependencies synced
    """
    engine = WorkflowEngine()
    stories_dir = Path('stories')

    synced_count = 0

    for story_file in sorted(stories_dir.glob('story-*.md')):
        story_id = story_file.stem
        content = story_file.read_text(encoding='utf-8')

        # Parse inline dependencies: **Dependencies**: story-043, story-044
        deps_inline = re.search(r'\*\*Dependencies\*\*:\s*(.+)', content)

        if not deps_inline:
            continue

        deps_raw = deps_inline.group(1).strip()

        # Skip if no dependencies
        if deps_raw.lower() in ['none', 'n/a', '-']:
            continue

        # Parse dependency IDs (comma-separated)
        dep_ids = [d.strip() for d in deps_raw.split(',') if d.strip()]

        # Determine dependency type from detailed section
        dep_type = 'explicit'  # Default
        reason = "Documented in story file"

        # Check for detailed dependency section
        deps_section = re.search(
            r'## Dependencies\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if deps_section:
            detailed = deps_section.group(1).lower()

            # Determine type from reasoning/context
            if 'same module' in detailed or 'same component' in detailed:
                dep_type = 'same_module'
            elif 'different module' in detailed or 'cross-module' in detailed:
                dep_type = 'different_module'

            # Extract reasoning if present
            reasoning_match = re.search(
                r'\*\*Reasoning\*\*:\s*(.+?)(?=\n\*\*|\n-|\Z)',
                deps_section.group(1),
                re.DOTALL
            )
            if reasoning_match:
                reason = reasoning_match.group(1).strip()[:200]  # Limit length

        # Sync each dependency to database
        for dep_id in dep_ids:
            # Validate dependency exists
            dep_status = engine.get_story_status(dep_id)
            if not dep_status:
                print(f"[!] Warning: {story_id} depends on {dep_id} which doesn't exist yet")
                continue

            result = engine.add_dependency(
                story_id=story_id,
                depends_on=dep_id,
                dep_type=dep_type,
                reason=reason
            )

            if result.success:
                print(f"[OK] {story_id} -> {dep_id} ({dep_type})")
                synced_count += 1
            else:
                # Ignore duplicate dependency errors (already synced)
                if 'already exists' not in result.error.lower():
                    print(f"[X] Failed: {story_id} -> {dep_id}: {result.error}")

    print(f"\n[Summary] Synced {synced_count} dependencies")
    return synced_count


def complete_story_registration():
    """
    Complete workflow after Story Composer creates stories.
    This MUST be called before any story delegation begins.

    Returns:
        dict: Summary of registration results
    """
    print("\n=== Story Registration Workflow ===\n")

    # 1. Ensure database exists
    ensure_state_machine_initialized()

    # 2. Register all stories
    registered = register_stories_from_composer()

    # 3. Sync dependencies
    synced = parse_and_sync_dependencies()

    # 4. Verify registration
    print("\n=== Verification ===\n")
    subprocess.run([
        'python',
        'RX.CE-Framework/scripts/workflow_engine.py',
        'status'
    ])

    print(f"\n[OK] Registration complete: {registered} stories, {synced} dependencies")
    print("[->] Ready for delegation workflow")

    return {
        'registered': registered,
        'dependencies': synced
    }


if __name__ == "__main__":
    # Allow CLI usage for testing
    complete_story_registration()
