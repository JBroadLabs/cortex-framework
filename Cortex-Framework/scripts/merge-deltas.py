#!/usr/bin/env python3
"""
ACE Self-Improvement: Delta Merge Script

This script parses approved context deltas and applies them to documentation files.
It handles ADD, UPDATE, and DEPRECATE operations, auto-increments versions, and
generates summary reports.

Usage:
    python Cortex-Framework/scripts/merge-deltas.py <delta-file-path>

Example:
    python Cortex-Framework/scripts/merge-deltas.py docs/context-deltas-batch-1.md
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class Delta:
    """Represents a single context delta proposal."""

    def __init__(self, number: int, title: str, target: str, section: str,
                 delta_type: str, confidence: str, evidence: str,
                 bullet_content: str, status: str):
        self.number = number
        self.title = title
        self.target = target
        self.section = section
        self.type = delta_type
        self.confidence = confidence
        self.evidence = evidence
        self.bullet_content = bullet_content
        self.status = status
        self.bullet_id = self._extract_bullet_id()

    def _extract_bullet_id(self) -> Optional[str]:
        """Extract bullet ID from bullet content."""
        match = re.search(r'id:\s*(\S+)', self.bullet_content)
        return match.group(1) if match else None

    def is_approved(self) -> bool:
        """Check if delta is approved."""
        return '[X] APPROVED' in self.status or '[x] APPROVED' in self.status


def parse_delta_file(file_path: Path) -> List[Delta]:
    """
    Parse delta file and extract all proposals with approval status.

    Args:
        file_path: Path to the delta file

    Returns:
        List of Delta objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    deltas = []

    # Split into delta sections
    delta_pattern = r'## Delta (\d+):\s*(.*?)\n(.*?)(?=## Delta \d+:|## Summary Statistics|$)'
    matches = re.finditer(delta_pattern, content, re.DOTALL)

    for match in matches:
        delta_num = int(match.group(1))
        title = match.group(2).strip()
        delta_content = match.group(3).strip()

        # Extract fields
        target = re.search(r'\*\*Target\*\*:\s*(.+)', delta_content)
        section = re.search(r'\*\*Section\*\*:\s*"([^"]+)"', delta_content)
        delta_type = re.search(r'\*\*Type\*\*:\s*(\w+)', delta_content)
        confidence = re.search(r'\*\*Confidence\*\*:\s*(\w+)', delta_content)

        # Extract evidence
        evidence_match = re.search(r'\*\*Evidence\*\*:(.*?)(?=\*\*Proposed|\*\*Updated|\*\*Deprecated)',
                                   delta_content, re.DOTALL)
        evidence = evidence_match.group(1).strip() if evidence_match else ""

        # Extract bullet content (YAML block)
        bullet_match = re.search(r'```(?:yaml)?\n(.*?)\n```', delta_content, re.DOTALL)
        bullet_content = bullet_match.group(1).strip() if bullet_match else ""

        # Extract status
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', delta_content)
        status = status_match.group(1).strip() if status_match else ""

        if all([target, section, delta_type, bullet_content]):
            delta = Delta(
                number=delta_num,
                title=title,
                target=target.group(1).strip(),
                section=section.group(1).strip(),
                delta_type=delta_type.group(1).strip(),
                confidence=confidence.group(1).strip() if confidence else "MEDIUM",
                evidence=evidence,
                bullet_content=bullet_content,
                status=status
            )
            deltas.append(delta)

    return deltas


def add_bullet(content: str, delta: Delta) -> str:
    """
    Add new bullet to document under target section.

    Args:
        content: Current document content
        delta: Delta containing the new bullet

    Returns:
        Updated document content
    """
    # Find the target section
    section_pattern = rf'^##\s+{re.escape(delta.section)}\s*$'
    lines = content.split('\n')

    section_idx = None
    for i, line in enumerate(lines):
        if re.match(section_pattern, line):
            section_idx = i
            break

    if section_idx is None:
        raise ValueError(f"Section '{delta.section}' not found in {delta.target}")

    # Find where to insert (after section header and any existing bullets)
    insert_idx = section_idx + 1

    # Skip empty lines after section header
    while insert_idx < len(lines) and lines[insert_idx].strip() == '':
        insert_idx += 1

    # Find the end of existing bullets in this section
    while insert_idx < len(lines):
        line = lines[insert_idx].strip()
        # If we hit another section or end of bullets, insert here
        if line.startswith('##') or (line and not line.startswith('-') and not line.startswith('**')):
            break
        if line.startswith('-') or line.startswith('**'):
            insert_idx += 1
            # Skip continuation lines
            while insert_idx < len(lines) and lines[insert_idx].strip() and not lines[insert_idx].strip().startswith('-'):
                insert_idx += 1
        else:
            break

    # Format the new bullet
    bullet_lines = []
    bullet_lines.append('')  # Empty line before bullet

    # Parse YAML-like content and format as markdown list item
    content_lines = delta.bullet_content.split('\n')
    for i, line in enumerate(content_lines):
        line = line.strip()
        if not line:
            continue

        # First line with id should start with '- **id**:'
        if 'id:' in line and i == 0:
            bullet_lines.append(f"- **id**: {line.split(':', 1)[1].strip()}")
        elif line.startswith('content:') or line.startswith('content |'):
            bullet_lines.append(f"  **content**: {line.split(':', 1)[1].strip() if ':' in line else ''}")
        elif not line.startswith('id:') and not line.startswith('content'):
            # Continuation of content
            bullet_lines.append(f"  {line}")

    bullet_lines.append('')  # Empty line after bullet

    # Insert the bullet
    lines[insert_idx:insert_idx] = bullet_lines

    return '\n'.join(lines)


def update_bullet(content: str, delta: Delta) -> str:
    """
    Update existing bullet in place.

    Args:
        content: Current document content
        delta: Delta containing the updated bullet

    Returns:
        Updated document content
    """
    if not delta.bullet_id:
        raise ValueError(f"No bullet ID found in delta {delta.number}")

    lines = content.split('\n')

    # Find the bullet by ID
    bullet_start = None
    for i, line in enumerate(lines):
        if f'id: {delta.bullet_id}' in line or f'id**: {delta.bullet_id}' in line:
            # Find the start of this bullet (look backwards for the '- **id**:' pattern)
            for j in range(i, -1, -1):
                if lines[j].strip().startswith('- **id**:'):
                    bullet_start = j
                    break
            if bullet_start is None:
                bullet_start = i
            break

    if bullet_start is None:
        raise ValueError(f"Bullet {delta.bullet_id} not found in {delta.target}")

    # Find the end of this bullet
    bullet_end = bullet_start + 1
    while bullet_end < len(lines):
        line = lines[bullet_end].strip()
        if line.startswith('- **id**:') or line.startswith('##'):
            break
        bullet_end += 1

    # Replace the bullet
    new_bullet_lines = []

    # Parse YAML-like content and format as markdown list item
    content_lines = delta.bullet_content.split('\n')
    for i, line in enumerate(content_lines):
        line = line.strip()
        if not line:
            continue

        # First line with id should start with '- **id**:'
        if 'id:' in line and i == 0:
            new_bullet_lines.append(f"- **id**: {line.split(':', 1)[1].strip()}")
        elif line.startswith('content:') or line.startswith('content |'):
            new_bullet_lines.append(f"  **content**: {line.split(':', 1)[1].strip() if ':' in line else ''}")
        elif not line.startswith('id:') and not line.startswith('content'):
            # Continuation of content
            new_bullet_lines.append(f"  {line}")

    lines[bullet_start:bullet_end] = new_bullet_lines

    return '\n'.join(lines)


def deprecate_bullet(content: str, delta: Delta) -> str:
    """
    Mark bullet as deprecated (don't delete for audit trail).

    Args:
        content: Current document content
        delta: Delta containing the bullet to deprecate

    Returns:
        Updated document content
    """
    if not delta.bullet_id:
        raise ValueError(f"No bullet ID found in delta {delta.number}")

    lines = content.split('\n')

    # Find the bullet by ID
    for i, line in enumerate(lines):
        if f'id: {delta.bullet_id}' in line or f'id**: {delta.bullet_id}' in line:
            # Add [DEPRECATED] marker
            if '[DEPRECATED]' not in line:
                lines[i] = line.replace(delta.bullet_id, f"{delta.bullet_id} [DEPRECATED]")
            break

    return '\n'.join(lines)


def increment_version(content: str, change_type: str) -> Tuple[str, str, str]:
    """
    Auto-increment version based on change type.

    Args:
        content: Current document content
        change_type: Type of change (ADD/UPDATE/DEPRECATE)

    Returns:
        Tuple of (updated content, old version, new version)
    """
    # Find version in frontmatter
    version_match = re.search(r'^version:\s*(\d+)\.(\d+)\.(\d+)', content, re.MULTILINE)

    if not version_match:
        raise ValueError("No version found in document frontmatter")

    major, minor, patch = map(int, version_match.groups())
    old_version = f"{major}.{minor}.{patch}"

    # Increment based on change type
    if change_type in ['ADD', 'UPDATE']:
        minor += 1
        patch = 0
    elif change_type == 'DEPRECATE':
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    # Update version in content
    content = re.sub(
        r'^version:\s*\d+\.\d+\.\d+',
        f'version: {new_version}',
        content,
        count=1,
        flags=re.MULTILINE
    )

    return content, old_version, new_version


def update_date(content: str) -> str:
    """
    Update 'updated' date field to current date.

    Args:
        content: Current document content

    Returns:
        Updated document content
    """
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(
        r'^updated:\s*\d{4}-\d{2}-\d{2}',
        f'updated: {today}',
        content,
        count=1,
        flags=re.MULTILINE
    )
    return content


def apply_delta(delta: Delta) -> Dict:
    """
    Apply a single approved delta to target document.

    Args:
        delta: Delta to apply

    Returns:
        Dictionary with change information
    """
    target_path = Path(delta.target)

    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {delta.target}")

    # Read current content
    with open(target_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply the change
    if delta.type == 'ADD':
        content = add_bullet(content, delta)
    elif delta.type == 'UPDATE':
        content = update_bullet(content, delta)
    elif delta.type == 'DEPRECATE':
        content = deprecate_bullet(content, delta)
    else:
        raise ValueError(f"Unknown delta type: {delta.type}")

    # Increment version
    content, old_version, new_version = increment_version(content, delta.type)

    # Update date
    content = update_date(content)

    # Write updated content
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return {
        'delta_num': delta.number,
        'type': delta.type,
        'target': delta.target,
        'bullet_id': delta.bullet_id,
        'old_version': old_version,
        'new_version': new_version
    }


def generate_report(delta_file: Path, approved_deltas: List[Delta],
                   changes: List[Dict], rejected_deltas: List[Delta]) -> str:
    """
    Generate human-readable summary report.

    Args:
        delta_file: Path to the delta file
        approved_deltas: List of approved deltas
        changes: List of applied changes
        rejected_deltas: List of rejected deltas

    Returns:
        Report content
    """
    # Extract batch number from filename
    batch_match = re.search(r'batch[_-](\d+)', delta_file.name)
    batch_num = batch_match.group(1) if batch_match else "N"

    report = f"""# Context Learning Report: Batch #{batch_num}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Applied Changes**: {len(changes)} delta(s) merged
**Rejected Changes**: {len(rejected_deltas)} delta(s)

## Changes Applied

"""

    if changes:
        for change in changes:
            report += f"- ✓ {change['type']} {change['bullet_id']} to {change['target']}\n"
    else:
        report += "- None\n"

    report += "\n## Changes Rejected\n\n"

    if rejected_deltas:
        for delta in rejected_deltas:
            report += f"- ✗ Delta {delta.number}: {delta.type} {delta.bullet_id or delta.title}\n"
    else:
        report += "- None\n"

    report += "\n## Documents Updated\n\n"

    # Group changes by document
    doc_changes = {}
    for change in changes:
        target = change['target']
        if target not in doc_changes:
            doc_changes[target] = []
        doc_changes[target].append(change)

    if doc_changes:
        for target, target_changes in doc_changes.items():
            # Get final version (last change to this doc)
            old_ver = target_changes[0]['old_version']
            new_ver = target_changes[-1]['new_version']
            report += f"- {target}: v{old_ver} → v{new_ver}\n"
    else:
        report += "- None\n"

    # Calculate next batch
    next_batch = int(batch_num) + 1 if batch_num.isdigit() else "N+1"

    if batch_num.isdigit():
        next_story_start = int(batch_num) * 10 + 1
        next_story_end = next_story_start + 9
        report += f"""
## Next Review Due

After story-{next_story_end:03d} completes (stories {next_story_start:03d}-{next_story_end:03d})
"""
    else:
        report += f"""
## Next Review Due

After next batch of 10 stories completes
"""

    return report


def main():
    """Main entry point."""
    # Fix Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) != 2:
        print("Usage: python Cortex-Framework/scripts/merge-deltas.py <delta-file-path>")
        sys.exit(1)

    delta_file_path = Path(sys.argv[1])

    if not delta_file_path.exists():
        print(f"[X] Error: Delta file not found: {delta_file_path}")
        sys.exit(1)

    print(f"[*] Reading delta file: {delta_file_path}")

    try:
        # Parse delta file
        deltas = parse_delta_file(delta_file_path)
        print(f"   Found {len(deltas)} delta(s)")

        # Separate approved and rejected
        approved = [d for d in deltas if d.is_approved()]
        rejected = [d for d in deltas if not d.is_approved()]

        print(f"   Approved: {len(approved)}, Rejected: {len(rejected)}")

        if not approved:
            print("\n[!] No approved deltas to apply")
            sys.exit(0)

        # Apply approved deltas
        changes = []
        print(f"\n[+] Applying {len(approved)} approved delta(s)...")

        for delta in approved:
            try:
                print(f"   [{delta.number}] {delta.type} {delta.bullet_id or delta.title} -> {delta.target}")
                change = apply_delta(delta)
                changes.append(change)
                print(f"       [OK] Success (v{change['old_version']} -> v{change['new_version']})")
            except Exception as e:
                print(f"       [X] Failed: {e}")
                sys.exit(1)

        # Generate report
        report = generate_report(delta_file_path, approved, changes, rejected)

        # Determine report path
        report_path = delta_file_path.parent / delta_file_path.name.replace('deltas', 'learnings')

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[OK] Successfully applied {len(changes)} change(s)")
        print(f"[*] Report generated: {report_path}")

        sys.exit(0)

    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
