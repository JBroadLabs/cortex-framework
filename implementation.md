# Context Learning System - Implementation Plan

## Executive Summary

Implement a feedback-driven documentation improvement system where:
1. Agents provide feedback on context quality after completing work
2. Every 10 stories, Hub triggers Reflector to analyze feedback
3. Reflector generates delta proposals for documentation improvements
4. Human reviews and approves deltas via HITL gate (same pattern as spec review)
5. System auto-applies approved deltas to documentation

**Timeline**: 12 hours core implementation + 3 hours testing = 15 hours total

**Risk**: LOW - Additive changes only, no breaking modifications

---

## Phase 1: Agent Feedback Collection

### Task 1.1: Update Backend Agent

**File**: `.claude/agents/backend-agent.md`

**Location**: After Step 6.6 (Handle Pause Signal), before Step 7 (Update Status for Handoff)

**Action**: Add new Step 6.7

```markdown
6.7. **Provide Context Feedback** (~2 minutes):

Before completing work, reflect on the context you used during implementation.

**Purpose**: Help the framework learn which documentation helped, which misled, and what was missing. This feedback enables continuous improvement of context quality.

**Required Fields**:

a. **Helpful Documents**: Which docs provided exactly what you needed?
   - Had the right pattern/example
   - Clear and accurate guidance
   - Saved research time

b. **Misleading Documents**: Which docs led you astray or contained outdated info?
   - Must include specific reason why misleading
   - Example: "describes single-instance pattern, we need distributed"

c. **Missing Patterns**: What did you wish was documented?
   - Specific patterns you had to figure out from scratch
   - Common scenarios not covered
   - Write "None" if nothing was missing

**Append to Story File**:
```markdown
## Context Feedback

**Helpful**: [comma-separated document names]

**Misleading**: [doc-name (specific reason), doc-name (specific reason)]

**Missing**: 
- [Specific pattern that should be documented]
- [Another missing pattern]
- None (if nothing missing)
```

**Example**:
```markdown
## Context Feedback

**Helpful**: api-patterns.md, logging-strategy.md, error-handling.md

**Misleading**: api-rate-limiting.md (describes in-memory Map approach, but we need Redis-based distributed rate limiting for multi-instance deployment)

**Missing**: 
- Distributed rate limiting pattern using Redis token bucket algorithm
- Standard error response format with HTTP status + app-specific error codes
```

⚠️ **CRITICAL**: This section is REQUIRED. Hub will not complete your delegation without it. Be specific in reasons for misleading docs and descriptions of missing patterns.

**Time Required**: 2 minutes per story - quick reflection on what helped/didn't help.
```

**Time Estimate**: 30 minutes

---

### Task 1.2: Update Frontend Agent

**File**: `.claude/agents/frontend-agent.md`

**Location**: Same as backend - after pause handling, before handoff

**Action**: Add same Step 6.7 as backend, but adjust example to frontend context:

```markdown
**Example**:
```markdown
## Context Feedback

**Helpful**: component-patterns.md, state-management.md, styling-conventions.md

**Misleading**: form-validation.md (shows basic HTML5 validation, but we need Zod schema validation with React Hook Form)

**Missing**: 
- Complex form validation patterns with Zod + React Hook Form
- Optimistic UI update patterns for mutations
```
```

**Time Estimate**: 20 minutes

---

### Task 1.3: Update Code Review Agent

**File**: `.claude/agents/code-review-agent.md`

**Location**: After Step 4 (Analyze and Report Results), before final handoff

**Action**: Add Step 4.5 - Context Feedback (same structure as above)

**Example adjusted for code review**:
```markdown
**Helpful**: coding-standards.md, security-patterns.md
**Misleading**: None
**Missing**: 
- Common anti-patterns specific to our codebase
- Performance optimization guidelines for our stack
```

**Time Estimate**: 15 minutes

---

### Task 1.4: Update Testing Agent

**File**: `.claude/agents/testing-agent.md`

**Location**: After Step 6 (Update Status & Handoff), add as Step 6.5

**Action**: Add Context Feedback step

**Example adjusted for testing**:
```markdown
**Helpful**: testing-patterns.md, test-data-setup.md
**Misleading**: None
**Missing**: 
- Integration test patterns for our API structure
- Mock data factory patterns
```

**Time Estimate**: 15 minutes

---

### Task 1.5: Update QA Agent

**File**: `.claude/agents/qa-agent.md`

**Location**: After final approval step, before completion

**Action**: Add Context Feedback step

**Example adjusted for QA**:
```markdown
**Helpful**: qa-checklist.md, acceptance-criteria.md
**Misleading**: None
**Missing**: 
- Edge case testing scenarios
- Cross-browser compatibility checklist
```

**Time Estimate**: 15 minutes

---

## Phase 2: State Machine Integration

### Task 2.1: Add Database Schema

**File**: `RX.CE-Framework/state/schema.sql`

**Location**: At the end of the file, before the final migration comments

**Action**: Add new tables

```sql
-- ============================================================================
-- CONTEXT LEARNING SYSTEM
-- ============================================================================

-- Track story completions for reflector triggering
CREATE TABLE IF NOT EXISTS learning_metrics (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton table
    completed_stories INTEGER DEFAULT 0,
    last_reflector_batch INTEGER DEFAULT 0,
    next_reflector_at INTEGER DEFAULT 10,
    last_reflector_run TEXT,
    total_deltas_proposed INTEGER DEFAULT 0,
    total_deltas_approved INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Initialize singleton row
INSERT OR IGNORE INTO learning_metrics (id, completed_stories) VALUES (1, 0);

-- Store context feedback from completed stories
CREATE TABLE IF NOT EXISTS context_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    helpful_docs TEXT,      -- JSON array of doc names
    misleading_docs TEXT,   -- JSON array of {doc, reason}
    missing_patterns TEXT,  -- JSON array of pattern descriptions
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_feedback_story ON context_feedback(story_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON context_feedback(created_at);

-- Track delta application history
CREATE TABLE IF NOT EXISTS delta_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_number INTEGER NOT NULL,
    delta_file_path TEXT NOT NULL,
    total_deltas INTEGER NOT NULL,
    approved_deltas INTEGER NOT NULL,
    rejected_deltas INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'applied', 'rejected', 'archived')),
    applied_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_delta_batch ON delta_history(batch_number);
```

**Time Estimate**: 15 minutes

---

### Task 2.2: Update Workflow Engine

**File**: `RX.CE-Framework/scripts/workflow_engine.py`

**Location**: Add methods after the existing hub interface methods (around line 29990)

**Action**: Add three new methods

```python
# ========================================================================
# CONTEXT LEARNING SYSTEM
# ========================================================================

def record_story_completion(self, story_id: str) -> DelegationResult:
    """
    Record story completion and check if reflector should trigger.
    
    Returns: DelegationResult with metadata.should_trigger_reflector = True if count reaches threshold
    """
    conn = self._get_conn()
    try:
        # Increment counter
        conn.execute("""
            UPDATE learning_metrics 
            SET completed_stories = completed_stories + 1,
                updated_at = datetime('now')
            WHERE id = 1
        """)
        
        # Get current count and threshold
        metrics = conn.execute("""
            SELECT completed_stories, next_reflector_at, last_reflector_batch
            FROM learning_metrics WHERE id = 1
        """).fetchone()
        
        completed = metrics['completed_stories']
        trigger_at = metrics['next_reflector_at']
        last_batch = metrics['last_reflector_batch']
        
        should_trigger = (completed >= trigger_at)
        
        if should_trigger:
            # Update for next trigger
            next_batch = last_batch + 1
            conn.execute("""
                UPDATE learning_metrics 
                SET last_reflector_batch = ?,
                    next_reflector_at = next_reflector_at + 10,
                    last_reflector_run = datetime('now')
                WHERE id = 1
            """, (next_batch,))
            
            conn.commit()
            
            return DelegationResult(
                success=True,
                message=f"Story {story_id} completion recorded ({completed} total) - TRIGGER REFLECTOR",
                metadata={
                    'should_trigger_reflector': True,
                    'batch_number': next_batch,
                    'completed_count': completed,
                    'story_range_start': completed - 9,
                    'story_range_end': completed
                }
            )
        else:
            conn.commit()
            return DelegationResult(
                success=True,
                message=f"Story {story_id} completion recorded ({completed}/{trigger_at})",
                metadata={
                    'should_trigger_reflector': False,
                    'completed_count': completed,
                    'next_trigger_at': trigger_at
                }
            )
    except Exception as e:
        conn.rollback()
        return DelegationResult(success=False, error=str(e))
    finally:
        conn.close()


def parse_context_feedback(self, story_id: str) -> Optional[Dict]:
    """
    Extract Context Feedback section from story file and parse it.
    
    Returns: {
        'helpful': ['doc-name-1', 'doc-name-2'],
        'misleading': [{'doc': 'doc-name', 'reason': 'explanation'}],
        'missing': ['pattern 1', 'pattern 2']
    }
    """
    story_file = STORIES_DIR / f"{story_id}.md"
    if not story_file.exists():
        return None
    
    content = story_file.read_text()
    
    # Extract Context Feedback section
    feedback_match = re.search(
        r'## Context Feedback\n(.*?)(?=\n##|\Z)', 
        content, 
        re.DOTALL
    )
    
    if not feedback_match:
        return None
    
    feedback_text = feedback_match.group(1)
    
    # Parse helpful docs
    helpful_match = re.search(r'\*\*Helpful\*\*:\s*([^\n]+)', feedback_text)
    helpful = []
    if helpful_match:
        helpful = [d.strip() for d in helpful_match.group(1).split(',') if d.strip() and d.strip().lower() != 'none']
    
    # Parse misleading docs (with reasons)
    misleading_match = re.search(r'\*\*Misleading\*\*:\s*([^\n]+)', feedback_text)
    misleading = []
    if misleading_match:
        misleading_text = misleading_match.group(1).strip()
        if misleading_text.lower() != 'none':
            for item in misleading_text.split(','):
                item = item.strip()
                if '(' in item and ')' in item:
                    doc_name, reason = item.split('(', 1)
                    misleading.append({
                        'doc': doc_name.strip(),
                        'reason': reason.rstrip(')').strip()
                    })
                elif item:
                    misleading.append({'doc': item, 'reason': 'no reason given'})
    
    # Parse missing patterns
    missing_match = re.search(r'\*\*Missing\*\*:\s*\n(.*?)(?=\n\*\*|\Z)', feedback_text, re.DOTALL)
    missing = []
    if missing_match:
        for line in missing_match.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- '):
                pattern = line[2:].strip()
                if pattern.lower() != 'none':
                    missing.append(pattern)
            elif line and line.lower() != 'none':
                missing.append(line)
    
    return {
        'helpful': helpful,
        'misleading': misleading,
        'missing': missing
    }


def store_context_feedback(self, story_id: str, agent: str) -> DelegationResult:
    """
    Parse and store context feedback from story file.
    Called by Hub after agent completion.
    """
    feedback = self.parse_context_feedback(story_id)
    
    if not feedback:
        return DelegationResult(
            success=False,
            error=f"No Context Feedback section found in {story_id}"
        )
    
    conn = self._get_conn()
    try:
        conn.execute("""
            INSERT INTO context_feedback 
            (story_id, agent, helpful_docs, misleading_docs, missing_patterns)
            VALUES (?, ?, ?, ?, ?)
        """, (
            story_id,
            agent,
            json.dumps(feedback['helpful']),
            json.dumps(feedback['misleading']),
            json.dumps(feedback['missing'])
        ))
        conn.commit()
        
        return DelegationResult(
            success=True,
            message=f"Context feedback stored for {story_id}",
            metadata=feedback
        )
    except Exception as e:
        conn.rollback()
        return DelegationResult(success=False, error=str(e))
    finally:
        conn.close()
```

**Time Estimate**: 1 hour (write + test)

---

### Task 2.3: Add CLI Commands

**File**: `RX.CE-Framework/scripts/workflow_engine.py`

**Location**: In the `if __name__ == '__main__':` section (around line 30542)

**Action**: Add new CLI commands

```python
# Add after existing commands, before final else

elif sys.argv[1] == 'learning_metrics':
    # Show learning system status
    engine = WorkflowEngine()
    conn = engine._get_conn()
    metrics = conn.execute("SELECT * FROM learning_metrics WHERE id = 1").fetchone()
    conn.close()
    
    print("\n" + "="*50)
    print("CONTEXT LEARNING METRICS")
    print("="*50)
    print(f"Completed Stories: {metrics['completed_stories']}")
    print(f"Next Reflector At: {metrics['next_reflector_at']} stories")
    print(f"Last Reflector Run: {metrics['last_reflector_run'] or 'Never'}")
    print(f"Total Batches: {metrics['last_reflector_batch']}")
    print(f"Deltas Proposed: {metrics['total_deltas_proposed']}")
    print(f"Deltas Approved: {metrics['total_deltas_approved']}")
    print("="*50 + "\n")

elif sys.argv[1] == 'feedback':
    # View feedback for a specific story
    if len(sys.argv) < 3:
        print("Usage: workflow_engine.py feedback <story_id>")
        sys.exit(1)
    
    engine = WorkflowEngine()
    feedback = engine.parse_context_feedback(sys.argv[2])
    
    if feedback:
        print(f"\nContext Feedback for {sys.argv[2]}:")
        print(f"Helpful: {', '.join(feedback['helpful']) if feedback['helpful'] else 'None'}")
        print(f"Misleading: {len(feedback['misleading'])} doc(s)")
        for item in feedback['misleading']:
            print(f"  - {item['doc']}: {item['reason']}")
        print(f"Missing: {len(feedback['missing'])} pattern(s)")
        for pattern in feedback['missing']:
            print(f"  - {pattern}")
    else:
        print(f"No feedback found for {sys.argv[2]}")
```

**Time Estimate**: 20 minutes

---

## Phase 3: Hub Agent Integration

### Task 3.1: Add Context Feedback Validation

**File**: `.claude/agents/hub-agent.md`

**Location**: In the "After Subagent Completes" section (around line 2045)

**Action**: Modify Step 1 (Verify evidence exists) to also check for Context Feedback

```markdown
1. **Verify Evidence AND Context Feedback**:

a. **Check for agent evidence** (existing):
```python
found, evidence_hash, location = engine.verify_agent_evidence(
    story_id="story-XXX",
    agent="code-review-agent"
)

if not found:
    # STOP - Subagent didn't complete properly
    engine.hub_fail_delegation(txn_id, "No evidence found in story file")
    return
```

b. **Check for Context Feedback** (NEW):
```python
# Read story file
story_path = Path(f"stories/{story_id}.md")
story_content = story_path.read_text()

# Verify Context Feedback section exists
if '## Context Feedback' not in story_content:
    print(f"❌ ERROR: {agent} must provide Context Feedback section")
    print(f"   Story: {story_id}")
    print(f"   Required for framework learning system")
    print(f"   Agent must add feedback before completion")
    
    engine.hub_fail_delegation(
        txn_id=txn_id,
        reason="Missing required Context Feedback section"
    )
    return

# Parse and validate feedback
feedback = engine.parse_context_feedback(story_id)
if not feedback:
    print(f"❌ ERROR: Context Feedback section malformed in {story_id}")
    engine.hub_fail_delegation(txn_id, "Malformed Context Feedback section")
    return

print(f"✓ Context Feedback validated for {story_id}")
```

c. **Store feedback in database** (NEW):
```python
# Store feedback for later analysis
result = engine.store_context_feedback(story_id=story_id, agent=agent)
if not result.success:
    print(f"⚠️  Warning: Failed to store feedback: {result.error}")
    # Continue anyway - feedback is in story file
```

d. **Then complete delegation** (existing):
```python
# 2. Complete the delegation
result = engine.hub_complete_delegation(
    txn_id=txn_id,
    evidence_hash=evidence_hash,
    evidence_location=location
)
# Story phase is now automatically advanced
```
```

**Time Estimate**: 30 minutes

---

### Task 3.2: Add Reflector Triggering Logic

**File**: `.claude/agents/hub-agent.md`

**Location**: Add new Stage 12 after existing stages (around line 2400, after "Integration Points" section)

**Action**: Add complete new stage

```markdown
## Stage 12: Context Learning (Every 10 Stories)

### When to Trigger

After ANY story reaches [Done] phase:

```python
# Record completion
result = engine.record_story_completion(story_id)

if result.metadata['should_trigger_reflector']:
    # Trigger reflector workflow
    trigger_reflector(result.metadata)
```

### Reflector Workflow

1. **Start Reflector Delegation**:
   ```python
   batch_num = result.metadata['batch_number']
   start_story = result.metadata['story_range_start']
   end_story = result.metadata['story_range_end']
   
   # Create reflector delegation in state machine
   txn = engine.hub_start_delegation(
       story_id=f"reflector-batch-{batch_num}",
       to_agent="reflector-agent",
       to_phase="Analysis"
   )
   
   if not txn.success:
       print(f"❌ Failed to start reflector delegation: {txn.error}")
       return
   ```

2. **Trigger Reflector Agent**:
   ```python
   print("\n" + "="*60)
   print("🧠 CONTEXT LEARNING TRIGGERED")
   print("="*60)
   print(f"Batch #{batch_num}")
   print(f"Stories: story-{start_story:03d} through story-{end_story:03d}")
   print(f"Output: docs/context-deltas-batch-{batch_num}.md")
   print("="*60 + "\n")
   
   # Delegate to reflector agent
   reflector_prompt = f"""
   Reflector Agent: Analyze context feedback from stories {start_story:03d} through {end_story:03d}.
   
   Task:
   1. Read all 10 story files: stories/story-{start_story:03d}.md through stories/story-{end_story:03d}.md
   2. Extract "Context Feedback" section from each story
   3. Aggregate patterns:
      - Which docs were helpful (mentioned 5+ times)
      - Which docs were misleading (mentioned 3+ times with reasons)
      - Which patterns were missing (requested 3+ times)
   4. Generate delta proposals following your workflow in .claude/agents/reflector-agent.md
   5. Create file: docs/context-deltas-batch-{batch_num}.md
   
   Follow the exact format specified in your persona for delta proposals.
   Each delta must include executable action JSON for auto-application.
   """
   
   # Execute reflector (this triggers the reflector agent in its context)
   # Reflector will create the delta file
   ```

3. **Wait for Reflector Completion**:
   ```python
   # Reflector creates: docs/context-deltas-batch-{batch_num}.md
   # Verify file was created
   
   delta_file = Path(f"docs/context-deltas-batch-{batch_num}.md")
   if not delta_file.exists():
       print(f"❌ Reflector failed to create delta file")
       engine.hub_fail_delegation(txn.txn_id, "Delta file not created")
       return
   
   # Complete reflector delegation
   evidence_hash = hashlib.sha256(delta_file.read_bytes()).hexdigest()[:16]
   engine.hub_complete_delegation(
       txn_id=txn.txn_id,
       evidence_hash=evidence_hash,
       evidence_location=str(delta_file)
   )
   ```

4. **Present Deltas to User (HITL Gate)**:
   ```python
   # Read delta file to show summary
   delta_content = delta_file.read_text()
   delta_count = delta_content.count('## Delta ')
   
   # Extract summary info
   approved_pattern = r'\[ \] APPROVED'
   total_deltas = len(re.findall(approved_pattern, delta_content))
   
   print("\n" + "="*60)
   print("📄 CONTEXT IMPROVEMENTS READY FOR REVIEW")
   print("="*60)
   print(f"File: docs/context-deltas-batch-{batch_num}.md")
   print(f"Proposed Changes: {total_deltas} deltas")
   print("\nInstructions:")
   print("1. Open the delta file in your editor")
   print("2. Review each proposed change carefully")
   print("3. Mark your decisions:")
   print("   [x] APPROVED  - Apply this change")
   print("   [ ] REJECTED  - Skip this change")
   print("4. Save the file")
   print("5. Return here and type your decision")
   print("="*60 + "\n")
   
   # Wait for user decision
   decision = input("Apply these deltas? (yes/no/edit): ").strip().lower()
   
   if decision == 'edit':
       print("\nContinue editing. When ready, run:")
       print(f"  python scripts/apply_deltas.py docs/context-deltas-batch-{batch_num}.md")
       return
   elif decision == 'no':
       print("\n❌ Deltas rejected by user")
       archive_delta_file(delta_file, applied=False)
       return
   elif decision != 'yes':
       print(f"\n⚠️  Invalid input: {decision}")
       print("Please run apply_deltas.py manually when ready")
       return
   ```

5. **Auto-Apply Approved Deltas**:
   ```python
   # Call apply_deltas script
   import subprocess
   
   result = subprocess.run(
       ['python', 'scripts/apply_deltas.py', str(delta_file)],
       capture_output=True,
       text=True
   )
   
   print(result.stdout)
   
   if result.returncode == 0:
       print("\n✅ Deltas applied successfully")
   else:
       print(f"\n❌ Error applying deltas: {result.stderr}")
   ```

6. **Update Metrics**:
   ```python
   # Parse applied deltas for metrics
   applied_count = result.stdout.count('✓ Applied')
   rejected_count = result.stdout.count('✗ Failed') + result.stdout.count('rejected')
   
   conn = engine._get_conn()
   conn.execute("""
       UPDATE learning_metrics
       SET total_deltas_proposed = total_deltas_proposed + ?,
           total_deltas_approved = total_deltas_approved + ?
       WHERE id = 1
   """, (total_deltas, applied_count))
   conn.commit()
   conn.close()
   ```

### Error Handling

- **Reflector fails**: Mark delegation as failed, continue workflow
- **User cancels**: Archive delta file, continue workflow
- **Apply fails**: Show error but don't block workflow
- **Missing feedback**: Reflector handles gracefully (notes in output)

### Resume Capability

If Hub is interrupted during delta approval:
- Delta file exists with status PENDING_REVIEW
- User can manually run: `python scripts/apply_deltas.py docs/context-deltas-batch-N.md`
- Or Hub can detect on restart and prompt for approval
```

**Time Estimate**: 1.5 hours

---

## Phase 4: Delta Application Script

### Task 4.1: Create apply_deltas.py Script

**File**: `RX.CE-Framework/scripts/apply_deltas.py` (NEW FILE)

**Action**: Create complete script

```python
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
    content = delta_file.read_text()
    
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
    
    content = target_file.read_text()
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
            target_file.write_text(content)
        
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
```

**Time Estimate**: 2 hours

---

### Task 4.2: Make Script Executable

**Action**:
```bash
chmod +x RX.CE-Framework/scripts/apply_deltas.py
```

**Time Estimate**: 1 minute

---

## Phase 5: Update Reflector Agent

### Task 5.1: Update Reflector Output Format

**File**: `.claude/agents/reflector-agent.md`

**Location**: In "Step 4: Generate Delta File" section (around line 2712)

**Action**: Update the delta format to include executable JSON

**Find and replace the delta template with**:

```markdown
**Template:**

```markdown
---
status: [PENDING_REVIEW]
generated: {current_date}
stories_analyzed: {start}-{end}
batch: {N}
---

# Context Delta Batch #{N}

**Summary**: {X} additions, {Y} updates, {Z} deprecations proposed

---

## Delta 1: {TYPE} - {Brief Description}

**Target**: docs/{module}/{file}.md
**Section**: "{Section Name}" (for ADD operations)
**Type**: ADD | UPDATE | DEPRECATE
**Confidence**: HIGH | MEDIUM | LOW

**Evidence**:
- Pattern mentioned in {count} stories: {story-list}
- Helpful mentions: {count}
- Misleading mentions: {count}
- Specific feedback:
  - "{feedback quote from story}"
  - "{another feedback quote}"

**Action**:
```python
{
  "operation": "add",  # or "deprecate" or "update"
  "target_file": "docs/backend/api-patterns.md",
  "target_section": "## Rate Limiting",  # for ADD only
  "target_bullet": "- Existing bullet text",  # for DEPRECATE/UPDATE only
  "new_bullet": "- New bullet text",  # for ADD only
  "replacement": "- Replacement bullet text",  # for DEPRECATE/UPDATE only
  "insert_position": "end"  # or "start", for ADD only
}
```

**Decision**: [ ] APPROVED [ ] REJECTED

---

{Repeat for each delta}

---

## Summary Statistics

**Document Usage (stories {start}-{end})**:
- {doc-name.md}: X/10 stories referenced
- {doc-name.md}: X/10 stories referenced

**Most Helpful Documents**:
- {doc-name.md}: Referenced X times (X helpful, X misleading)

**Top Missing Patterns**:
- "{pattern}": Mentioned in X stories
- "{pattern}": Mentioned in X stories
```
```

**Time Estimate**: 20 minutes

---

## Phase 6: Testing & Validation

### Task 6.1: Schema Migration

**Action**: Run schema migration to create new tables

```bash
# Option 1: Reinitialize database (if safe to lose data)
rm RX.CE-Framework/state/workflow.db
python RX.CE-Framework/scripts/workflow_engine.py init

# Option 2: Apply schema updates to existing database
python RX.CE-Framework/scripts/workflow_engine.py migrate
```

**Expected Output**:
```
[OK] Database initialized: RX.CE-Framework/state/workflow.db
[OK] Created learning_metrics table
[OK] Created context_feedback table
[OK] Created delta_history table
```

**Time Estimate**: 10 minutes

---

### Task 6.2: Test Complete Workflow

**Action**: Run through complete 10-story cycle

```bash
# 1. Start fresh project or use existing one
# 2. Generate 10 stories (or use existing)

# 3. For each story, manually add Context Feedback section
# (or let agents add it as they complete)

# 4. After story 10, verify reflector triggers
python RX.CE-Framework/scripts/workflow_engine.py learning_metrics

# Expected: completed_stories = 10, should trigger reflector

# 5. Manually trigger reflector if needed
# (or let Hub trigger automatically)

# 6. Verify delta file created
ls docs/context-deltas-batch-1.md

# 7. Review and mark deltas
# Edit file, add [x] APPROVED to some deltas

# 8. Apply deltas
python RX.CE-Framework/scripts/apply_deltas.py docs/context-deltas-batch-1.md

# 9. Verify files updated
git diff docs/

# 10. Check backup created
ls docs/.backups/

# 11. Test rollback
python RX.CE-Framework/scripts/apply_deltas.py --rollback $(ls -t docs/.backups/ | head -1)
```

**Time Estimate**: 2 hours

---

## Phase 7: Documentation Updates

### Task 7.1: Update README or Main Docs

**Action**: Document the new context learning feature

**Suggested location**: Add section to main README or create `docs/CONTEXT_LEARNING.md`

**Content**:
```markdown
## Context Learning System

The framework continuously improves its documentation based on agent feedback.

### How It Works

1. **Feedback Collection**: After completing work, agents provide feedback on which docs helped, which misled, and what was missing

2. **Batch Analysis**: Every 10 completed stories, the Reflector Agent automatically analyzes all feedback

3. **Delta Proposals**: Reflector generates evidence-based proposals for documentation improvements

4. **Human Approval**: You review proposals and approve/reject each one

5. **Auto-Application**: Approved changes are automatically applied to documentation

### Agent Workflow

When agents complete work, they must add:

```markdown
## Context Feedback
**Helpful**: [docs that helped]
**Misleading**: [docs that misled (with reasons)]
**Missing**: [patterns that should be documented]
```

### Viewing Metrics

```bash
python RX.CE-Framework/scripts/workflow_engine.py learning_metrics
```

### Manual Delta Application

If workflow is interrupted:

```bash
python RX.CE-Framework/scripts/apply_deltas.py docs/context-deltas-batch-N.md
```

### Rollback

If changes need to be reverted:

```bash
# List backups
ls docs/.backups/

# Rollback to specific backup
python RX.CE-Framework/scripts/apply_deltas.py --rollback YYYYMMDD_HHMMSS
```
```

**Time Estimate**: 30 minutes

---

## Acceptance Criteria

### Functional Requirements

- [ ] All 5 agents (Backend, Frontend, Code Review, Testing, QA) have Context Feedback step
- [ ] Hub validates Context Feedback presence before completing delegations
- [ ] State machine tracks story completions and triggers reflector at count=10
- [ ] Reflector generates delta file with executable JSON actions
- [ ] HITL gate presents deltas for human review (same UX as spec review)
- [ ] apply_deltas.py successfully applies approved deltas
- [ ] Backup system creates timestamped backups before applying
- [ ] Rollback system can restore from backups
- [ ] CLI commands (learning_metrics, feedback) work correctly
- [ ] Delta files archived after application

### Quality Requirements

- [ ] No breaking changes to existing workflows
- [ ] Agents can complete normally with Context Feedback
- [ ] Hub handles missing feedback gracefully (fails delegation with clear message)
- [ ] Malformed feedback doesn't crash system
- [ ] Concurrent story development doesn't interfere with reflector
- [ ] Manual doc edits between batches are handled (via HITL rejection)
- [ ] Complete audit trail (feedback stored, deltas archived, backups created)

### Performance Requirements

- [ ] Feedback collection adds <2 minutes per story
- [ ] Reflector analysis completes in <2 minutes for 10 stories
- [ ] Delta approval takes <5 minutes (human time)
- [ ] Auto-application completes in <10 seconds

---

## Timeline

| Phase | Tasks | Time | Dependencies |
|-------|-------|------|--------------|
| 1 | Agent feedback collection | 1.75 hours | None |
| 2 | State machine integration | 1.5 hours | Phase 1 |
| 3 | Hub integration | 2 hours | Phase 1, 2 |
| 4 | Delta application script | 2 hours | None (parallel) |
| 5 | Reflector updates | 20 min | None (parallel) |
| 6 | Testing & validation | 3 hours | All phases |
| 7 | Documentation | 30 min | Phase 6 |
| **Total** | **11.25 hours** | | |

**Buffer**: +0.75 hours for unexpected issues = **12 hours total**

---

## Rollout Plan

### Phase 1: Internal Testing (First 10 Stories)

1. Implement all changes
2. Run 10 test stories with manual feedback
3. Verify reflector triggers correctly
4. Test delta application on non-critical docs
5. Validate rollback works

### Phase 2: Production Deployment (Next 90 Stories)

1. Roll out to production project
2. Monitor first 3 batches (30 stories) closely
3. Collect user feedback on HITL experience
4. Refine delta proposal quality based on patterns

### Phase 3: Optimization (After 100 Stories)

1. Analyze which doc improvements had highest impact
2. Adjust reflector thresholds if needed (currently 3+ mentions)
3. Consider adding batch frequency config if needed

---

## Success Metrics

### Immediate (After First Batch)

- ✅ 10 stories provide Context Feedback successfully
- ✅ Reflector generates delta file
- ✅ User successfully approves/rejects deltas
- ✅ Approved deltas applied to docs correctly

### Short-term (After 3 Batches / 30 Stories)

- ✅ Misleading docs identified and deprecated
- ✅ Missing patterns added to documentation
- ✅ Helpful docs validated and kept
- ✅ Developer feedback on HITL experience is positive

### Long-term (After 10 Batches / 100 Stories)

- ✅ Documentation quality measurably improved
- ✅ Agents spend less time researching undocumented patterns
- ✅ Context precision increases (3-5 docs remain optimal)
- ✅ Development velocity increases due to better context

---

## Risk Mitigation

### Risk: Agents Skip Context Feedback

**Mitigation**: Hub validation enforces presence. Delegation fails if missing.

**Fallback**: If validation is too strict, add warning mode first, then enforce after 1 week.

### Risk: Low-Quality Feedback

**Mitigation**: 
- Clear examples in agent workflows
- Require specific reasons for "misleading"
- Require specific descriptions for "missing"

**Fallback**: Reflector can filter low-quality feedback (ignore generic/vague entries)

### Risk: Bad Deltas Applied

**Mitigation**: 
- HITL gate catches before application
- Backup system allows rollback
- Git version control as final safety net

**Fallback**: Can always manually revert changes via git or rollback script

### Risk: Workflow Interruption During Approval

**Mitigation**: 
- Delta file persists with PENDING_REVIEW status
- User can resume with manual apply_deltas.py call
- State machine tracks incomplete delegations

**Fallback**: Worst case, user manually applies changes from delta file

---

## Questions for Implementation

1. **Batch Frequency**: Currently set to 10 stories. Should this be configurable?
   - Recommendation: Start with 10, add config later if needed

2. **Reflector Model**: Use same model as other agents or dedicated stronger model?
   - Recommendation: Start with same model, upgrade if analysis quality is insufficient

3. **Delta Auto-Merge**: Should any deltas auto-apply without human review?
   - Recommendation: NO - always require human approval for safety

4. **Feedback Storage**: Currently stores in both story files and database. Keep both?
   - Recommendation: YES - story files are source of truth, database for query/analysis

5. **Rollback Expiry**: How long to keep backups?
   - Recommendation: Keep last 10 backups, auto-delete older ones

---

## Implementation Checklist

Use this checklist to track progress:

### Phase 1: Agent Updates
- [ ] backend-agent.md updated with Step 6.7
- [ ] frontend-agent.md updated with Step 6.7
- [ ] code-review-agent.md updated with feedback step
- [ ] testing-agent.md updated with feedback step
- [ ] qa-agent.md updated with feedback step

### Phase 2: State Machine
- [ ] schema.sql updated with new tables
- [ ] workflow_engine.py: record_story_completion() added
- [ ] workflow_engine.py: parse_context_feedback() added
- [ ] workflow_engine.py: store_context_feedback() added
- [ ] workflow_engine.py: CLI commands added

### Phase 3: Hub Integration
- [ ] hub-agent.md: Context Feedback validation added
- [ ] hub-agent.md: Stage 12 (reflector triggering) added
- [ ] hub-agent.md: HITL gate for delta approval added

### Phase 4: Delta Application
- [ ] apply_deltas.py script created
- [ ] Script made executable
- [ ] Backup functionality implemented
- [ ] Rollback functionality implemented

### Phase 5: Reflector Updates
- [ ] reflector-agent.md: Delta format updated with executable JSON

### Phase 6: Testing
- [ ] Schema migration tested
- [ ] Complete 10-story workflow tested
- [ ] Edge cases tested
- [ ] Rollback tested

### Phase 7: Documentation
- [ ] Context learning feature documented
- [ ] CLI commands documented
- [ ] Rollback procedure documented

---

## Ready to Implement

This plan is complete and ready for execution. All modifications are additive with no breaking changes. The system will continue to work normally even if agents don't provide feedback initially (Hub will enforce it).

Start with Phase 1 (agent updates) and work through sequentially. Each phase can be tested independently before proceeding to the next.

**Estimated Total Time**: 12 hours implementation + 3 hours testing = **15 hours**

**Risk Level**: LOW (additive changes, multiple safety mechanisms)

**Expected Value**: HIGH (continuous documentation improvement, learning from real usage)