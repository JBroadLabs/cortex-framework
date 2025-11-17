# Context Engineering - How It Works

This framework includes **ACE (Agentic Context Engineering)** - an automated system that learns from story execution and continuously improves documentation quality with minimal human intervention.

## What is ACE?

ACE is a self-improvement system that:
- ✅ Automatically collects feedback from agents during story implementation
- ✅ Analyzes patterns every 10 stories using evidence-based rules
- ✅ Proposes specific, actionable documentation improvements
- ✅ Auto-applies approved changes to maintain context quality
- ✅ Requires only ~5 minutes of human review every 10 stories

**Automation Level**: 95% (agents collect data, system analyzes, human only approves deltas)

## For Users (Humans)

### Initial Setup
✅ **Nothing required** - ACE system is fully automated and ready to use

### Every 10 Stories (ACE Workflow)

When Hub Agent completes 10 stories, you'll receive a notification:

```
📊 Context Learning Batch #1 Ready for Review

Analyzed stories 001-010

Review required: docs/context-deltas-batch-1.md

⚠️ NEW STORY WORK BLOCKED UNTIL REVIEW COMPLETE
```

**Your Review Process (~5 minutes)**:

1. **Open the delta file**: `docs/context-deltas-batch-N.md`

2. **Review each proposed change**. You'll see evidence-based proposals like:
   ```markdown
   ## Delta 1: ADD - Distributed Rate Limiting

   **Target**: docs/backend/api-patterns.md
   **Section**: "Rate Limiting"
   **Type**: ADD
   **Confidence**: HIGH

   **Evidence**:
   - Pattern mentioned in 3 stories: 007, 008, 009
   - Specific feedback: "needed distributed rate limiting with Redis"

   **Proposed Bullet**:
   ```yaml
   id: api-rate-003
   content: |
     For multi-instance deployments, use Redis-based token bucket.
     Store tokens with key: "rate:limit:{user_id}:{endpoint}".
   ```

   **Status**: [ ] APPROVED [ ] REJECTED
   ```

3. **Make decisions**:
   - Change to `[X] APPROVED` to accept
   - Change to `[X] REJECTED` to reject

4. **Save the file**

5. **Done!** Hub Agent automatically:
   - ✅ Applies approved changes
   - ✅ Increments version numbers
   - ✅ Updates document dates
   - ✅ Generates learning report
   - ✅ Resumes story work

**Review Checklist**:
- For ADD: Does this fill a real gap? (3+ stories mentioned it)
- For UPDATE: Is this a meaningful improvement?
- For DEPRECATE: Is it truly misleading? (3+ stories complained)

### When Manually Updating Documentation (Optional)

**With ACE**: Version updates are automatic! ✅

When you approve deltas, the merge script automatically:
- Updates version numbers (ADD/UPDATE → minor, DEPRECATE → patch)
- Updates the `updated:` date field
- No manual version management needed

**If manually editing docs** (outside ACE workflow):
1. Open the file
2. Update version in YAML header:
   ```yaml
   ---
   version: 1.1.0  # ← increment this
   updated: 2025-10-23  # ← update date
   ---
   ```
3. Follow semantic versioning:
   - **Major** (X.0.0): Breaking changes, incompatible with previous version
   - **Minor** (1.X.0): New patterns/sections added, backward compatible
   - **Patch** (1.0.X): Typo fixes, clarifications, no new content

### If Version Mismatch Blocks a Story
You'll see this in the story's Context Validation section:
```
- Version compatibility: FAILED
- logging-strategy.md (v1.5.0) ❌ INCOMPATIBLE (needs v2.x.x)
```

**Fix it:**
1. Update the incompatible document to match the major version
2. Or rollback index.md if the version bump was premature
3. Story will automatically re-validate and proceed

---

## For Agents

### System Design Agent
- Add version headers (v1.0.0) to all sharded documents automatically
- Add version header to each index.md file

### Hub Agent
- **Step 4.6c**: Validate version compatibility before allowing [I] status
- **Stage 12**: ACE Self-Improvement Workflow (every 10 stories)
  - 12a: Detect 10-story milestone
  - 12b: Trigger Reflector Agent
  - 12c: Block new stories & notify human
  - 12d: Poll for human approval
  - 12e: Auto-merge approved deltas
  - 12f: Notify human & resume
  - 12g: Error recovery

### Reflector Agent (NEW)
- **Command**: `.claude/commands/reflector.md`
- **Persona**: `RX.CE-Framework/personas/reflector_agent.md`
- **Role**: Analyze Context Feedback from 10 stories and generate delta proposals
- **Input**: Story files N-9 to N with Context Feedback sections
- **Process**:
  1. Extract Context Feedback from each story
  2. Aggregate metrics (helpful/misleading counts per bullet)
  3. Identify missing patterns (mentioned in 3+ stories)
  4. Apply delta generation rules:
     - ADD: Missing pattern in 3+ stories
     - UPDATE: Helpful bullet with 3+ improvement suggestions
     - DEPRECATE: Bullet marked misleading in 3+ stories
  5. Generate `docs/context-deltas-batch-N.md` with evidence
- **Output**: Delta file with approval checkboxes for human review
- **Time**: ~5-7 minutes per batch

### Implementation Agents (Frontend/Backend/QA)
- **After completing story**: Add Context Feedback section (~2 minutes)
  ```markdown
  ## Context Feedback

  **Helpful**: [comma-separated bullet IDs used]
  **Misleading**: [bullet-id (reason), ...]
  **Missing**:
  - [Specific pattern needed]
  ```
- **Rules**:
  - List bullets actually referenced during implementation
  - Include 5-10 word reason for misleading bullets
  - Be specific about missing patterns (not vague)
  - Time budget: 2 minutes max

---

## How ACE Improves Over Time

```
Stories 1-10:
├─ Agents implement stories normally
├─ Add Context Feedback sections (~2 min each)
│  ├─ Helpful: api-rate-001, sec-auth-002
│  ├─ Misleading: api-rate-003 (outdated approach)
│  └─ Missing: "distributed rate limiting pattern"
└─ Complete work normally

Story 10 reached:
├─ Hub detects milestone
├─ Triggers Reflector Agent automatically
├─ Reflector analyzes all 10 Context Feedback sections
│  ├─ api-rate-001: helpful 8/10 → Keep
│  ├─ api-rate-003: misleading 3/10 → Propose DEPRECATE
│  └─ "distributed rate limiting": mentioned 3/10 → Propose ADD
├─ Generates docs/context-deltas-batch-1.md
└─ Blocks new stories until review

Human reviews deltas (~5 min):
├─ Reviews evidence for each proposal
├─ [X] APPROVED - ADD distributed rate limiting (HIGH confidence)
├─ [X] APPROVED - DEPRECATE api-rate-003 (HIGH confidence)
└─ Saves file

Hub auto-merges:
├─ Applies approved deltas to docs
├─ api-rate-004 added to api-patterns.md
├─ api-rate-003 marked [DEPRECATED]
├─ Versions updated: 2.1.0 → 2.3.0
├─ Dates updated automatically
├─ Generates docs/context-learnings-batch-1.md
└─ Resumes story work

Stories 11-20:
├─ Agents load improved context
├─ Find "distributed rate limiting" pattern (newly added)
├─ Avoid deprecated api-rate-003
├─ Add Context Feedback continues...
└─ Learning continues...

Story 20 reached:
└─ ACE workflow triggers again, cycle repeats
```

**Result**:
- ✅ Context stays accurate and current
- ✅ No manual documentation maintenance
- ✅ Evidence-based improvements only
- ✅ Prevents context decay and brevity bias
- ✅ 95% automated (human only approves)

---

## Version Compatibility Rules

**Major Version Changes (1.x.x → 2.x.x)**:
- Breaking changes
- All docs in that module must match major version
- Stories blocked until versions aligned

**Minor Version Changes (1.2.x → 1.3.x)**:
- New patterns added
- Backward compatible
- No blocking

**Patch Version Changes (1.2.3 → 1.2.4)**:
- Bug fixes, clarifications
- Fully compatible
- No blocking

---

## ACE System Components

### Files Created

**Core Scripts**:
- `RX.CE-Framework/scripts/merge-deltas.py` - Applies approved deltas to documentation
  - Parses delta files
  - ADD/UPDATE/DEPRECATE operations
  - Auto-increments versions
  - Generates learning reports

**Agents**:
- `.claude/commands/reflector.md` - Command for triggering Reflector Agent
- `RX.CE-Framework/personas/reflector_agent.md` - Persona definition
  - Reads 10 story files
  - Aggregates metrics
  - Applies evidence-based rules
  - Generates delta proposals

**Agent Updates**:
- `.claude/commands/hub.md` - Stage 12: ACE workflow integration
- `.claude/commands/backend.md` - Step 8: Context Feedback
- `.claude/commands/frontend.md` - Step 8: Context Feedback
- `.claude/commands/qa.md` - Step 4: Context Feedback

**Generated Files** (per batch):
- `docs/context-deltas-batch-N.md` - Delta proposals for human review
- `docs/context-learnings-batch-N.md` - Learning report after merge

### Delta Types

**ADD** - New bullet to documentation
- Trigger: Pattern mentioned in 3+ stories as "Missing"
- Confidence: HIGH (3+ stories), MEDIUM (2 stories)
- Example: "distributed rate limiting with Redis" mentioned in stories 7, 8, 9
- Action: Insert new bullet with unique ID

**UPDATE** - Enhance existing bullet
- Trigger: Bullet helpful in 5+ stories BUT 3+ suggest improvements
- Confidence: HIGH (3+ suggestions), MEDIUM (2 suggestions)
- Example: api-err-001 helpful but "need structured format" mentioned 3 times
- Action: Enhance content, preserve core guidance

**DEPRECATE** - Mark bullet as outdated
- Trigger: Bullet marked misleading in 3+ stories
- Confidence: HIGH (3+ stories), MEDIUM (2 stories)
- Example: api-rate-002 misleading in stories 7, 8, 9 ("in-memory not suitable")
- Action: Add [DEPRECATED] marker, suggest alternative

### Evidence Requirements

For delta to be proposed:
- **HIGH confidence**: 3+ stories mention pattern/issue
- **MEDIUM confidence**: 2 stories mention pattern/issue
- **LOW confidence**: 1 story (not proposed - wait for more data)

Each delta includes:
- Story references (which stories mentioned it)
- Specific feedback quotes
- Count of mentions (X/10 stories)
- Confidence level with rationale

### Time Budget

**Per Story**: +2 minutes (Context Feedback)
- 1 min: Review which bullets were referenced
- 30 sec: Note misleading bullets
- 30 sec: Note missing patterns

**Per 10 Stories**: +5-7 minutes (Human Review)
- 3 min: Review delta proposals
- 2 min: Check evidence and make decisions
- Automatic: Merge script execution

**Total Overhead**: ~27 minutes per 10 stories (vs 20 min manual)
- **Benefit**: Prevents context decay, ensures documentation quality

### Bullet ID Format

For documents converted to bullet format:

```
{doc-prefix}-{category}-{number}

Examples:
- api-rate-001    (API patterns, Rate Limiting, #1)
- api-err-002     (API patterns, Error Handling, #2)
- comp-form-001   (Component patterns, Forms, #1)
- sec-auth-003    (Security, Authentication, #3)

Prefixes:
- api-  = API patterns
- comp- = Component patterns
- sec-  = Security
- db-   = Database
- test- = Testing
```

### Testing

Test the system:
```bash
# Run test merge
python RX.CE-Framework/scripts/merge-deltas.py test-ace/test-deltas.md

# Verify results
cat test-ace/test-doc.md          # Check document updates
cat test-ace/test-learnings.md    # Check generated report
```

Expected results:
- New bullets added
- Existing bullets updated
- Rejected deltas skipped
- Versions incremented correctly
- Report generated

---

## Quick Reference

**For Humans**:
- Every 10 stories → Review delta file (~5 min)
- Approve/reject each delta
- System auto-applies changes
- See: [ACE-QUICK-START.md](../../../ACE-QUICK-START.md)

**For Agents**:
- After each story → Add Context Feedback (~2 min)
- List helpful/misleading bullets
- Note missing patterns
- See agent-specific instructions in `.claude/commands/`

**Key Benefits**:
- 95% automated
- Evidence-based improvements
- Prevents documentation drift
- No manual version management
- Continuous quality improvement
