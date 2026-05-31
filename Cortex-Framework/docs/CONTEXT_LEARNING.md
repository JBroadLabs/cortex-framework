# Context Learning System - User Guide

This framework includes an automated **Context Learning System** that improves documentation and troubleshooting guides based on real agent feedback during story execution.

## What is the Context Learning System?

A dual-stream feedback system that:
- ✅ Collects feedback from agents about documentation quality (Context Feedback)
- ✅ Captures significant issues and solutions encountered (Issues Encountered)
- ✅ Analyzes patterns every 10 stories using evidence-based rules
- ✅ Proposes two types of improvements: documentation updates and troubleshooting entries
- ✅ Requires human review and approval before applying changes
- ✅ Auto-applies approved changes to maintain quality

**Key Innovation**: Learns from BOTH what docs say (Context Feedback) AND what actually breaks (Issues Encountered)

---

## For Users (Humans)

### Initial Setup
✅ **Nothing required** - System is fully integrated and ready to use

### Every 10 Stories (Review Workflow)

When Hub Agent completes 10 stories, you'll receive a notification:

```
🧠 CONTEXT LEARNING TRIGGERED
============================================================
Batch #1
Stories: story-001 through story-010
Outputs:
  - docs/context-deltas-batch-1.md
  - docs/troubleshooting-updates-batch-1.md
============================================================

📄 IMPROVEMENTS READY FOR REVIEW
============================================================

📋 Documentation Improvements:
   File: docs/context-deltas-batch-1.md
   Deltas: 5 proposed

🔧 Troubleshooting Updates:
   File: docs/troubleshooting-updates-batch-1.md
   Issues: 3 patterns documented

Instructions:
1. Open BOTH delta files in your editor
2. Review each proposed change carefully
3. Mark your decisions:
   [x] APPROVED  - Apply this change
   [ ] REJECTED  - Skip this change
4. Save both files
5. Return here and confirm
============================================================

Apply these improvements? (yes/no/edit):
```

### Your Review Process (~5-7 minutes)

#### 1. Review Documentation Improvements

Open `docs/context-deltas-batch-N.md` and review each delta:

```markdown
## Delta 1: ADD - Distributed Rate Limiting Pattern

**Target**: docs/backend/api-patterns.md
**Section**: "## Rate Limiting"
**Type**: ADD
**Confidence**: HIGH

**Evidence**:
- Pattern mentioned in 3 stories: 007, 008, 009
- Helpful mentions: 2
- Misleading mentions: 1
- Specific feedback:
  - "needed distributed rate limiting with Redis token bucket"
  - "in-memory approach doesn't work for multi-instance"

**Action**:
```python
{
  "operation": "add",
  "target_file": "docs/backend/api-patterns.md",
  "target_section": "## Rate Limiting",
  "new_bullet": "- For multi-instance deployments, use Redis-based token bucket...",
  "insert_position": "end"
}
```

**Decision**: [ ] APPROVED [ ] REJECTED
```

**Mark your decision**:
- Change `[ ]` to `[x]` next to APPROVED to accept
- Change `[ ]` to `[x]` next to REJECTED to reject

#### 2. Review Troubleshooting Updates

Open `docs/troubleshooting-updates-batch-N.md` and review each issue:

```markdown
## Update 1: ADD - Circular Dependencies

**Frequency**: HIGH (new)
**Occurrences**: 3 in batch (stories 002, 015, 023)

**Action**:
```python
{
  "operation": "add_issue",
  "target_file": "docs/troubleshooting/common-issues.md",
  "section": "HIGH FREQUENCY",
  "content": "### Circular Dependencies\n\n**Occurred in**: 3 stories..."
}
```

**Decision**: [ ] APPROVED [ ] REJECTED
```

#### 3. Save and Apply

After marking all decisions:
1. Save both files
2. Return to terminal and type `yes`
3. System automatically applies approved changes
4. Backups are created automatically

**Or defer review**:
- Type `edit` to continue editing later
- Type `no` to reject all changes
- Run manually later: `python scripts/apply_deltas.py docs/context-deltas-batch-N.md`

### Review Guidelines

**For Documentation Deltas**:
- **ADD**: Does this fill a real gap? (3+ stories mentioned it)
- **UPDATE**: Is this a meaningful improvement?
- **DEPRECATE**: Is it truly misleading? (3+ stories complained)

**For Troubleshooting Updates**:
- **HIGH frequency** (3+): Usually approve - recurring issues need documenting
- **MEDIUM frequency** (2): Approve if solution is clear and reusable
- **ARCHIVE**: Approve if issue hasn't occurred in 20+ stories

### Rollback

If you need to undo applied changes:

```bash
# List available backups
ls Cortex-Framework/docs/.backups/

# Rollback to specific backup
python Cortex-Framework/scripts/apply_deltas.py --rollback 20260108_143022
```

---

## For Agents

### All Implementation Agents (Backend, Frontend, Testing, QA, Code Review)

After completing work, provide **TWO types of feedback**:

#### A. Context Feedback (REQUIRED)

Reflect on documentation quality:

```markdown
## Context Feedback

**Helpful**: [comma-separated document names]

**Misleading**: [doc-name (specific reason), doc-name (specific reason)]

**Missing**:
- [Specific pattern that should be documented]
- None (if nothing missing)
```

**Example**:
```markdown
## Context Feedback

**Helpful**: api-patterns.md, logging-strategy.md, error-handling.md

**Misleading**: api-rate-limiting.md (describes in-memory approach, but we need Redis-based distributed rate limiting)

**Missing**:
- Distributed rate limiting pattern using Redis token bucket
- Standard error response format with HTTP status codes
```

**Rules**:
- List docs actually referenced during implementation
- Include specific reasons for misleading docs
- Be specific about missing patterns (not vague)
- **Time budget**: 2 minutes max

#### B. Issues Encountered (OPTIONAL)

Document significant blockers to help future stories:

```markdown
## Issues Encountered

**{Brief Title}**
- Problem: {What error/blocker occurred}
- Solution: {How you fixed it}
- Prevention: {How to avoid in future}
```

**Example**:
```markdown
## Issues Encountered

**Circular Dependency: UserService ↔ AuthService**
- Problem: Build error "Circular dependency detected between UserService and AuthService"
- Solution: Extracted IUserData interface to shared/interfaces/, modified AuthService to import interface instead of concrete class
- Prevention: Define interfaces in separate files before implementations, follow dependency injection pattern

**Async Test Failure**
- Problem: Test "should update profile" intermittently failed with "Cannot read property of undefined"
- Solution: Wrapped assertion in waitFor() from @testing-library/react
- Prevention: Always use waitFor() when asserting on async state updates
```

**Document if**:
- Build or compilation error
- Test failure (non-obvious reason)
- Runtime error or crash
- Had to research solution externally
- Design decision that resolved complexity

**Rules**:
- Only document significant issues (not trivial bugs)
- Include complete Problem/Solution/Prevention
- **This section is OPTIONAL** - only if issues occurred
- **Time budget**: 1 minute per issue

### Hub Agent

**After Subagent Completes**:
1. Validate Context Feedback section exists (REQUIRED)
2. Parse and store feedback in database
3. Parse and store issues (optional)
4. Complete delegation

**After Story Reaches [Done]**:
1. Record story completion
2. Check if 10-story milestone reached
3. If yes, trigger Reflector Agent workflow
4. Present both delta files to human for review
5. Apply approved changes
6. Update metrics

### Reflector Agent

**Triggered every 10 stories**:

1. Read 10 completed story files
2. Extract Context Feedback sections (documentation quality)
3. Extract Issues Encountered sections (execution problems)
4. Aggregate patterns using evidence-based rules:
   - HIGH frequency: 3+ occurrences
   - MEDIUM frequency: 2 occurrences
   - LOW frequency: 1 occurrence (wait for more data)
5. Generate TWO delta files:
   - `docs/context-deltas-batch-N.md` (documentation improvements)
   - `docs/troubleshooting-updates-batch-N.md` (issue patterns)
6. Apply pruning to troubleshooting file (keep under 25 issues)

---

## How the System Improves Over Time

```
Stories 1-10:
├─ Agents implement stories normally
├─ Add Context Feedback sections (~2 min each)
│  ├─ Helpful: api-patterns.md, logging-strategy.md
│  ├─ Misleading: api-rate-limiting.md (outdated approach)
│  └─ Missing: "distributed rate limiting pattern"
├─ Add Issues Encountered sections (~1 min if issues occurred)
│  └─ "Circular Dependency: UserService ↔ AuthService"
└─ Complete work normally

Story 10 reached:
├─ Hub detects milestone
├─ Triggers Reflector Agent automatically
├─ Reflector analyzes all 10 Context Feedback sections
│  ├─ api-patterns.md: helpful 8/10 → Keep
│  ├─ api-rate-limiting.md: misleading 3/10 → Propose DEPRECATE
│  └─ "distributed rate limiting": mentioned 3/10 → Propose ADD
├─ Reflector analyzes all Issues Encountered sections
│  ├─ "Circular Dependency": occurred 3/10 → Propose ADD to troubleshooting
│  └─ "Async Test Failure": occurred 1/10 → Wait for more data (LOW)
├─ Generates docs/context-deltas-batch-1.md (5 deltas)
├─ Generates docs/troubleshooting-updates-batch-1.md (3 issues)
└─ Presents both to human for review

Human reviews deltas (~5-7 min):
├─ Reviews evidence for each proposal
├─ [X] APPROVED - ADD distributed rate limiting (HIGH confidence)
├─ [X] APPROVED - DEPRECATE outdated api-rate-limiting section
├─ [X] APPROVED - ADD Circular Dependency to troubleshooting (HIGH frequency)
└─ Saves both files

Hub auto-applies:
├─ Applies approved deltas to documentation
├─ Applies approved troubleshooting updates
├─ Creates timestamped backups
├─ Archives delta files
├─ Updates metrics in database
└─ Resumes story work

Stories 11-20:
├─ Agents load improved documentation
├─ Find "distributed rate limiting" pattern (newly added)
├─ Avoid deprecated api-rate-limiting section
├─ Hit circular dependency issue → Check troubleshooting guide → Find solution
├─ Add Context Feedback + Issues Encountered continues...
└─ Learning continues...

Story 20 reached:
└─ Learning workflow triggers again, cycle repeats
```

**Result**:
- ✅ Documentation stays accurate and current
- ✅ Troubleshooting guide captures recurring issues
- ✅ Agents spend less time debugging known issues
- ✅ Evidence-based improvements only (no guessing)
- ✅ Complete audit trail (feedback stored, deltas archived, backups created)

---

## System Components

### Files Created

**Core Scripts**:
- `Cortex-Framework/scripts/apply_deltas.py` - Applies approved deltas
  - Parses delta files (both types)
  - ADD/UPDATE/DEPRECATE operations
  - add_issue/archive_issue operations
  - Creates timestamped backups
  - Supports dry-run and rollback

**Database Tables**:
- `learning_metrics` - Tracks story completions and reflector batches
- `context_feedback` - Stores Context Feedback from stories
- `issues_encountered` - Stores Issues Encountered from stories
- `delta_history` - Tracks applied deltas (both types)

**Agents Updated**:
- `.claude/agents/backend-agent.md` - Step 6.7: Dual feedback
- `.claude/agents/frontend-agent.md` - Step 6.7: Dual feedback
- `.claude/agents/code-review-agent.md` - Step 4.5: Dual feedback
- `.claude/agents/testing-agent.md` - Step 6.5: Dual feedback
- `.claude/agents/qa-agent.md` - Step 3.5: Dual feedback
- `.claude/agents/hub-agent.md` - Context validation + Stage 12 workflow
- `.claude/agents/reflector-agent.md` - Step 5: Troubleshooting updates

**Generated Files** (per batch):
- `docs/context-deltas-batch-N.md` - Documentation improvement proposals
- `docs/troubleshooting-updates-batch-N.md` - Troubleshooting issue proposals

### Delta Types

#### Documentation Deltas

**ADD** - New content to documentation
- Trigger: Pattern mentioned in 3+ stories as "Missing"
- Action: Insert new content into target section

**UPDATE** - Enhance existing content
- Trigger: Content helpful but 3+ suggest improvements
- Action: Replace existing content with enhanced version

**DEPRECATE** - Mark content as outdated
- Trigger: Content marked misleading in 3+ stories
- Action: Replace with deprecation notice

#### Troubleshooting Updates

**ADD** - New issue to troubleshooting guide
- Trigger: Issue occurred 3+ times (HIGH) or 2 times (MEDIUM)
- Action: Add issue with Problem/Solution/Prevention to guide

**ARCHIVE** - Remove stale issue
- Trigger: Issue not seen in 20+ stories
- Action: Remove or move to archived section

### Evidence Requirements

For delta to be proposed:
- **HIGH confidence**: 3+ stories mention pattern/issue
- **MEDIUM confidence**: 2 stories mention pattern/issue
- **LOW confidence**: 1 story (not proposed - wait for more data)

Each delta includes:
- Story references (which stories mentioned it)
- Specific feedback quotes
- Frequency counts (X/10 stories)
- Confidence level with rationale

### Time Budget

**Per Story**: +2-3 minutes total
- 2 min: Context Feedback (REQUIRED)
- 1 min: Issues Encountered (OPTIONAL, if issues occurred)

**Per 10 Stories**: +5-7 minutes (Human Review)
- 3-4 min: Review both delta files
- 2-3 min: Check evidence and mark decisions
- Automatic: Delta application

**Total Overhead**: ~27-37 minutes per 10 stories
- **Benefit**: Prevents documentation drift and captures institutional knowledge

---

## CLI Commands

### View Learning Metrics

```bash
cd Cortex-Framework
python scripts/workflow_engine.py learning_metrics
```

Output:
```
==================================================
CONTEXT LEARNING METRICS
==================================================
Completed Stories: 15
Next Reflector At: 20 stories
Last Reflector Run: 2026-01-08 14:30:00
Total Batches: 1
Deltas Proposed: 8
Deltas Approved: 6
==================================================
```

### View Feedback for Story

```bash
cd Cortex-Framework
python scripts/workflow_engine.py feedback story-007
```

Output shows Context Feedback and Issues Encountered from that story.

### Apply Deltas Manually

```bash
cd Cortex-Framework

# Apply context deltas
python scripts/apply_deltas.py docs/context-deltas-batch-1.md

# Apply troubleshooting updates
python scripts/apply_deltas.py docs/troubleshooting-updates-batch-1.md

# Dry run (preview changes)
python scripts/apply_deltas.py docs/context-deltas-batch-1.md --dry-run

# Rollback to backup
python scripts/apply_deltas.py --rollback 20260108_143022
```

---

## Troubleshooting Guide Usage

The system maintains `docs/troubleshooting/common-issues.md` with three sections:

### HIGH FREQUENCY (3+ occurrences)
Issues seen in 3+ stories - check here first

### MEDIUM FREQUENCY (2 occurrences)
Issues seen in 2 stories - may be relevant

### LOW FREQUENCY (1 occurrence)
Recent one-time issues - context-specific

**How to use**:
1. When you hit an error, open `docs/troubleshooting/common-issues.md`
2. Search (Ctrl+F / Cmd+F) for error keywords
3. If found, apply documented solution
4. If not found, proceed with normal debugging
5. Document significant issues in Issues Encountered section

**Automatic maintenance**:
- Issues move between sections based on frequency
- Stale issues (not seen in 20+ stories) get archived
- Guide stays focused (max 25 active issues)

---

## Quick Reference

**For Humans**:
- Every 10 stories → Review TWO delta files (~5-7 min)
- Approve/reject each delta based on evidence
- System auto-applies approved changes
- Rollback available if needed

**For Agents**:
- After each story → Add Context Feedback (~2 min, REQUIRED)
- After issues occur → Add Issues Encountered (~1 min, OPTIONAL)
- Check troubleshooting guide first when errors occur
- Be specific in feedback (not vague)

**Key Benefits**:
- **Dual learning streams**: Documentation quality AND execution knowledge
- **Evidence-based**: Only proposes changes with 2-3+ occurrences
- **Comprehensive**: Improves both what's documented and what breaks
- **Auditable**: Complete history of feedback, deltas, and changes
- **Recoverable**: Backups and rollback for all changes

---

## Migration from Old ACE System

If you previously used the ACE system:

**Changes**:
- ❌ Old: `merge-deltas.py` → ✅ New: `apply_deltas.py`
- ❌ Old: Single delta file → ✅ New: Two delta files (context + troubleshooting)
- ❌ Old: Bullet IDs required → ✅ New: Simplified format, no IDs needed
- ❌ Old: Only Context Feedback → ✅ New: Dual feedback (Context + Issues)
- ❌ Old: Version management → ✅ New: Simplified (version management separate)

**What to do**:
1. Archive old `context-deltas-*.md` files
2. Archive old `merge-deltas.py` script
3. Use new system going forward
4. Database tracks everything automatically
