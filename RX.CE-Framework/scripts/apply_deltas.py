#!/usr/bin/env python3
"""
Apply approved context deltas to documentation.

Usage:
    python scripts/apply_deltas.py docs/context-deltas-batch-N.md
    python scripts/apply_deltas.py docs/context-deltas-batch-N.md --dry-run
    python scripts/apply_deltas.py --rollback <backup_id>
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import shutil


def parse_delta_file(delta_file: Path) -> List[Dict]:
    """Extract approved deltas from proposal file."""
    content = delta_file.read_text(encoding='utf-8')

    deltas = []
    # Split by "## Delta N:"
    sections = re.split(r'\n## Delta \d+:', content)

    for i, section in enumerate(sections[1:], 1):  # Skip header
        # Check if approved
        is_approved = '[x] APPROVED' in section or '[X] APPROVED' in section
        is_rejected = '[ ] REJECTED' not in section or '[x] REJECTED' in section or '[X] REJECTED' in section

        if not is_approved:
            continue

        # Extract delta type
        delta_type = None
        if 'Type**: ADD' in section or 'Type: ADD' in section:
            delta_type = 'ADD'
        elif 'Type**: DEPRECATE' in section or 'Type: DEPRECATE' in section:
            delta_type = 'DEPRECATE'
        elif 'Type**: UPDATE' in section or 'Type: UPDATE' in section:
            delta_type = 'UPDATE'

        # Extract action JSON
        action_match = re.search(r'```(?:python|json)\n({.*?})\n```', section, re.DOTALL)
        if action_match:
            try:
                action = json.loads(action_match.group(1))
                action['delta_number'] = i
                action['delta_type'] = delta_type
                deltas.append(action)
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Failed to parse action JSON for Delta {i}: {e}")
                continue

    return deltas


def backup_files(files: List[Path]) -> Path:
    """Create timestamped backup before applying changes."""
    backup_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('docs/.backups') / backup_id
    backup_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        if file.exists():
            backup_path = backup_dir / file.name
            shutil.copy2(file, backup_path)

    return backup_dir


def apply_delta(delta: Dict, dry_run: bool = False) -> bool:
    """Apply a single delta operation to target file."""
    target_file = Path(delta['target_file'])

    if not target_file.exists():
        print(f"  ⚠️  Target file not found: {target_file}")
        return False

    content = target_file.read_text(encoding='utf-8')
    original_content = content

    try:
        if delta['operation'] == 'add':
            # Find target section
            section = delta['target_section']
            new_bullet = delta['new_bullet']
            insert_pos = delta.get('insert_position', 'end')

            # Find section in content
            section_pattern = re.escape(section) + r'.*?\n'
            section_match = re.search(section_pattern, content)

            if not section_match:
                print(f"  ⚠️  Section not found: {section}")
                return False

            # Insert bullet
            if insert_pos == 'end':
                # Find next section or end of file
                next_section = re.search(r'\n##[^#]', content[section_match.end():])
                if next_section:
                    insert_point = section_match.end() + next_section.start()
                else:
                    insert_point = len(content)

                content = content[:insert_point] + f"{new_bullet}\n\n" + content[insert_point:]
            else:
                # Insert right after section header
                insert_point = section_match.end()
                content = content[:insert_point] + f"{new_bullet}\n" + content[insert_point:]

        elif delta['operation'] == 'deprecate':
            # Find and replace bullet
            target = delta['target_bullet']
            replacement = delta['replacement']

            if target in content:
                content = content.replace(target, replacement, 1)
            else:
                print(f"  ⚠️  Bullet not found: {target[:80]}...")
                return False

        elif delta['operation'] == 'update':
            # Replace existing bullet
            target = delta['target_bullet']
            replacement = delta['replacement']

            if target in content:
                content = content.replace(target, replacement, 1)
            else:
                print(f"  ⚠️  Bullet not found: {target[:80]}...")
                return False

        else:
            print(f"  ⚠️  Unknown operation: {delta['operation']}")
            return False

        # Write updated content
        if not dry_run:
            target_file.write_text(content, encoding='utf-8')

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def archive_delta_file(delta_file: Path, applied: bool):
    """Move delta file to archive."""
    archive_subdir = 'applied' if applied else 'rejected'
    archive_dir = Path('docs/archive') / archive_subdir
    archive_dir.mkdir(parents=True, exist_ok=True)

    archive_path = archive_dir / delta_file.name
    shutil.move(str(delta_file), str(archive_path))

    return archive_path


def rollback(backup_id: str):
    """Restore files from a backup."""
    backup_dir = Path('docs/.backups') / backup_id

    if not backup_dir.exists():
        print(f"❌ Backup not found: {backup_id}")
        print(f"   Available backups:")
        backups = list(Path('docs/.backups').iterdir())
        for b in sorted(backups, reverse=True)[:5]:
            print(f"   - {b.name}")
        sys.exit(1)

    print(f"Rolling back to backup: {backup_id}\n")

    # Restore all files from backup
    restored = 0
    for backup_file in backup_dir.iterdir():
        if backup_file.is_file():
            target = Path('docs') / backup_file.name
            shutil.copy2(backup_file, target)
            print(f"✓ Restored {target}")
            restored += 1

    print(f"\n✅ Rollback complete: {restored} files restored")


def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/apply_deltas.py docs/context-deltas-batch-N.md")
        print("  python scripts/apply_deltas.py docs/context-deltas-batch-N.md --dry-run")
        print("  python scripts/apply_deltas.py --rollback <backup_id>")
        sys.exit(1)

    # Handle rollback
    if sys.argv[1] == '--rollback':
        if len(sys.argv) < 3:
            print("Usage: python scripts/apply_deltas.py --rollback <backup_id>")
            sys.exit(1)
        rollback(sys.argv[2])
        sys.exit(0)

    # Parse delta file
    delta_file = Path(sys.argv[1])
    dry_run = '--dry-run' in sys.argv

    if not delta_file.exists():
        print(f"❌ Delta file not found: {delta_file}")
        sys.exit(1)

    if dry_run:
        print("🔍 DRY RUN - No files will be modified\n")

    # Parse approved deltas
    deltas = parse_delta_file(delta_file)

    if not deltas:
        print("❌ No approved deltas found in file")
        print("   Check that deltas are marked: [x] APPROVED")
        sys.exit(1)

    print(f"Applying {len(deltas)} approved delta(s) from {delta_file.name}...\n")

    # Collect affected files for backup
    affected_files = list(set(Path(d['target_file']) for d in deltas))

    # Create backup
    if not dry_run:
        backup_dir = backup_files(affected_files)
        print(f"💾 Backup created: {backup_dir}")
        print(f"   Rollback: python scripts/apply_deltas.py --rollback {backup_dir.name}\n")

    # Apply each delta
    success_count = 0
    for delta in deltas:
        delta_num = delta.get('delta_number', '?')
        print(f"Delta {delta_num}: {delta['operation'].upper()} in {Path(delta['target_file']).name}")
        if apply_delta(delta, dry_run=dry_run):
            print(f"  ✓ Applied")
            success_count += 1
        else:
            print(f"  ✗ Failed")

    print(f"\n{'✅' if success_count == len(deltas) else '⚠️'} {success_count}/{len(deltas)} deltas applied successfully")

    # Show updated files
    if success_count > 0:
        print("\nUpdated files:")
        for file in affected_files:
            print(f"  - {file}")

    # Archive delta file
    if not dry_run:
        archive_path = archive_delta_file(delta_file, applied=success_count > 0)
        print(f"\n📁 Delta file archived: {archive_path}")

    sys.exit(0 if success_count == len(deltas) else 1)


if __name__ == '__main__':
    main()
