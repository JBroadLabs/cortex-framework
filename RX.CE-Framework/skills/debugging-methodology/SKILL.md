---
name: debugging-methodology
description: Systematic debugging methodology for CONTEXT ENGINEERING framework. Use when troubleshooting blocked stories, workflow failures, agent errors, version conflicts, dependency issues, or framework malfunctions. Provides step-by-step diagnosis and resolution.
---

# Debugging Methodology

Systematic approach to diagnosing and resolving issues in the CONTEXT ENGINEERING framework.

## When to Use

Use this skill when you encounter:
- Blocked or stuck stories
- Agent errors or unexpected behavior  
- Version conflicts or dependency issues
- Workflow transition failures
- Code review, testing, or QA stage failures
- Context loading or sharding problems

## Core Workflow

### 1. Gather Information (5 min)

**Capture the symptom:**
- What is the current state?
- What was expected?
- What actually happened?
- When did it start?

**Check system state:**
```bash
# Story tracker
cat RX.CE-Framework/state/story_tracker.json

# Configuration
cat .claude/config.yml

# Recent logs
tail -n 50 RX.CE-Framework/logs/*.log 2>/dev/null
```

### 2. Match Patterns (10 min)

Check against common failure patterns:

#### Pattern: Version Mismatch
**Symptoms:** Story stuck at `[Pending]`, version incompatible messages

**Check:**
```bash
# Find version declarations
grep -r "version:" docs/
grep -r "version:" stories/
```

**Fix:** Update document versions to match requirements

#### Pattern: Missing Context Files  
**Symptoms:** Agent errors about missing files, incomplete outputs

**Check:**
```bash
# Verify required docs exist
test -f docs/system-design.md && echo "✅" || echo "❌"
test -f docs/frontend-spec.md && echo "✅" || echo "❌"
test -f docs/backend-spec.md && echo "✅" || echo "❌"
```

**Fix:** Generate missing documents, verify completeness

#### Pattern: Premature Sharding
**Symptoms:** Sharded directories exist before HITL Gate 1

**Check:**
```bash
# These shouldn't exist yet
test -d docs/frontend/ && echo "❌ Premature" || echo "✅"
test -d docs/backend/ && echo "❌ Premature" || echo "✅"
```

**Fix:** Consolidate back to monolithic docs, wait for HITL Gate 1

#### Pattern: Agent Role Confusion
**Symptoms:** Agent performing wrong tasks, conflicting agents

**Check:**
```bash
# Verify correct command for phase
cat RX.CE-Framework/state/story_tracker.json | grep "active_agent"
cat RX.CE-Framework/state/story_tracker.json | grep "phase"
```

**Fix:** Verify correct command, check persona definition, ensure proper context

#### Pattern: Workflow State Corruption
**Symptoms:** Story stuck in transition, phase indicators incorrect

**Check:**
```bash
# Examine tracker for inconsistencies
cat RX.CE-Framework/state/story_tracker.json
```

**Fix:** Backup tracker, manually correct state, verify consistency

#### Pattern: Configuration Override
**Symptoms:** Expected gates being skipped, unexpected behavior

**Check:**
```bash
# Review configuration
cat .claude/config.yml | grep -E "(skip_|coding_standards|min_coverage)"
```

**Fix:** Review intent, reset to defaults if needed, document rationale

### 3. Analyze Root Cause (15 min)

**Form hypothesis:**
- Based on patterns matched, what's the most likely cause?
- What evidence supports it?
- How can you verify it?

**Test hypothesis:**
- Design minimal test case
- Execute in isolation
- Observe results
- Accept or reject

**Document findings:**
```
ROOT CAUSE: [Verified cause]
IMPACT: [What's affected]
TRIGGER: [What caused it]
```

### 4. Resolve (Variable)

**Choose approach:**
- Quick Fix: Immediate workaround (<5 min)
- Proper Fix: Correct underlying issue (<30 min)
- Systemic Fix: Prevent recurrence (<2 hours)

**Implement:**
1. Document the fix being applied
2. Execute fix commands
3. Verify resolution
4. Confirm no new issues introduced

**Validate:**
- [ ] Original symptom resolved
- [ ] No new issues introduced  
- [ ] System in consistent state
- [ ] Workflow can proceed

### 5. Document & Prevent (5 min)

**Record the issue:**
```bash
cat > RX.CE-Framework/debug-log/issue-$(date +%Y%m%d-%H%M%S).md << EOF
# Debug Session: $(date)

## Symptom
[Problem description]

## Root Cause
[Verified cause]

## Resolution
[Fix applied]

## Prevention
[How to avoid in future]
EOF
```

**Update preventive measures:**
- Update validation scripts
- Add guards to agents
- Document in framework
- Share with team

## Common Issues Quick Reference

### Story Blocked at [Pending]

**Diagnosis:**
```bash
# Check dependencies
cat stories/[story-id].md | grep -A 20 "dependencies:"
```

**Common causes:**
1. Version mismatch in dependencies
2. Missing required documents
3. Circular dependencies

**Resolution:**
→ Update document versions
→ Generate missing docs
→ Break circular references

### Agent Producing Errors

**Diagnosis:**
```bash
# Check agent command
cat .claude/commands/[agent].md
```

**Common causes:**
1. Missing context files
2. Incorrect file paths
3. Tool not available

**Resolution:**
→ Generate missing context
→ Update paths
→ Install tools

### Tests Failing

**Diagnosis:**
```bash
# Check test config
cat .claude/config.yml | grep -A 5 "testing"
```

**Common causes:**
1. Coverage below threshold
2. Environment mismatch
3. Incomplete implementation

**Resolution:**
→ Add test coverage
→ Match environment
→ Complete implementation

### Code Review Failures

**Diagnosis:**
```bash
# Check standards
cat .claude/config.yml | grep "coding_standards"
```

**Common causes:**
1. Standards not configured
2. Linting errors
3. Missing documentation

**Resolution:**
→ Enable standards
→ Fix linting
→ Add documentation

## Emergency Procedures

### Complete System Freeze

**Recovery:**
```bash
# Backup state
cp -r RX.CE-Framework RX.CE-Framework.backup.$(date +%s)

# Check for locks
find . -name "*.lock" -type f

# Reset tracker
cp RX.CE-Framework/state/story_tracker.json.backup \
   RX.CE-Framework/state/story_tracker.json

# Verify config
cat .claude/config.yml

# Restart minimal
claude code hub "Create test story: Hello World"
```

### Cascading Failures

**Recovery:**
```bash
# Identify common dependency
grep -r "dependencies:" stories/ | sort | uniq -c | sort -rn

# Revert problematic doc
git diff docs/[problematic-doc].md

# Fix version
# Update in document frontmatter
```

### Data Loss/Corruption

**Recovery:**
```bash
# Check git history
git log --oneline --all

# Restore from commit
git checkout [commit-hash] -- [file-path]

# Or restore from backup
cp -r RX.CE-Framework.backup.[timestamp]/* RX.CE-Framework/

# Re-run validation
bash RX.CE-Framework/scripts/validate-system-design.sh
```

## Guidelines

**Do:**
- Start with most likely causes
- Use pattern matching before deep dives
- Document as you investigate
- Verify fixes thoroughly

**Don't:**
- Make multiple changes at once
- Skip documentation
- Ignore root cause
- Forget to share learnings

## Examples

### Example 1: Version Mismatch
```
User: "Story-042 is stuck at pending"

Debugging:
1. Check story dependencies → requires logging-strategy v2.x
2. Check document version → currently v1.5
3. Update document to v2.0
4. Story automatically unblocks
```

### Example 2: Missing Context
```
User: "Backend agent failing with file not found"

Debugging:
1. Check agent command → loads docs/backend-spec.md
2. Verify file exists → file missing
3. Run System Design Agent to generate
4. Agent succeeds on retry
```

### Example 3: Configuration Issue
```
User: "Tests are being skipped"

Debugging:
1. Check config.yml → skip_testing: true
2. User intended to skip only for prototypes
3. Reset to false
4. Tests now run properly
```

## Integration with Framework

This skill works with:
- `/ask` command for questions
- `/hub` command for orchestration
- All agent commands for their specific tasks
- Story workflow for automatic recovery

The skill is automatically invoked when Claude detects debugging-related requests.