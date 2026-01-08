# ⚠️ DEPRECATED - Context Engineering (ACE System)

**This document describes the OLD ACE (Agentic Context Engineering) system which has been replaced.**

---

## 🔄 Migration Notice

**Current System**: [Context Learning System](CONTEXT_LEARNING.md) ✅

**What Changed**:
- ❌ Old: ACE (Agentic Context Engineering)
- ✅ New: Context Learning System with Dual-Stream Feedback

**Key Improvements**:
1. **Dual feedback streams**: Now captures BOTH documentation quality (Context Feedback) AND execution issues (Issues Encountered)
2. **Troubleshooting guide**: Automatically maintains `docs/troubleshooting/common-issues.md` based on recurring issues
3. **Simplified workflow**: No bullet IDs required, cleaner format
4. **Better tracking**: Database-backed with full audit trail
5. **Two delta files**: Separate documentation improvements from troubleshooting updates

---

## 📖 Please Use New Documentation

**For complete documentation of the current system, see:**
- **[CONTEXT_LEARNING.md](CONTEXT_LEARNING.md)** - Complete user guide for the new system

---

## 🗄️ Archive: Old ACE System Overview

<details>
<summary>Click to expand old ACE documentation (for reference only)</summary>

# Context Engineering - How It Works (OLD - DEPRECATED)

This framework included **ACE (Agentic Context Engineering)** - an automated system that learned from story execution and continuously improved documentation quality with minimal human intervention.

## What was ACE?

ACE was a self-improvement system that:
- ✅ Automatically collected feedback from agents during story implementation
- ✅ Analyzed patterns every 10 stories using evidence-based rules
- ✅ Proposed specific, actionable documentation improvements
- ✅ Auto-applied approved changes to maintain context quality
- ✅ Required only ~5 minutes of human review every 10 stories

**Automation Level**: 95% (agents collect data, system analyzes, human only approves deltas)

## Why Was It Replaced?

**Limitations of old ACE system**:
1. Only captured documentation feedback (not execution issues)
2. Required bullet IDs for all documentation
3. Single delta file made review harder
4. No troubleshooting guide maintenance
5. Version management was coupled with learning system

**New system advantages**:
1. **Dual learning**: Learns from BOTH documentation gaps AND actual problems encountered
2. **Troubleshooting guide**: Automatically captures and organizes recurring issues
3. **Cleaner format**: No bullet IDs needed, more maintainable
4. **Better organization**: Two separate delta files for different concerns
5. **Database-backed**: Complete audit trail and metrics

## Components That Were Deprecated

**Deprecated Scripts**:
- ❌ `RX.CE-Framework/scripts/merge-deltas.py` → ✅ Use `apply_deltas.py` instead

**Deprecated Files**:
- ❌ `RX.CE-Framework/personas/reflector_agent.md` → ✅ Use `.claude/agents/reflector-agent.md`
- ❌ `.claude/commands/reflector.md` → ✅ Integrated into hub-agent.md Stage 12

**Deprecated Concepts**:
- ❌ Bullet IDs (e.g., `api-rate-001`) → ✅ Simplified format without IDs
- ❌ Single delta file → ✅ Two delta files (context + troubleshooting)
- ❌ Version auto-increment → ✅ Version management separate
- ❌ `context-learnings-batch-N.md` report → ✅ Database metrics

## Migration Path

If you have old ACE delta files:

```bash
# Archive old files
mkdir -p RX.CE-Framework/docs/archive/old-ace
mv docs/context-deltas-*.md RX.CE-Framework/docs/archive/old-ace/
mv docs/context-learnings-*.md RX.CE-Framework/docs/archive/old-ace/

# Remove old script
rm RX.CE-Framework/scripts/merge-deltas.py

# Use new system
# See CONTEXT_LEARNING.md for complete guide
```

## Key Differences Summary

| Feature | Old ACE | New Context Learning |
|---------|---------|---------------------|
| Feedback types | Context only | Context + Issues |
| Delta files | 1 file | 2 files (context + troubleshooting) |
| Bullet IDs | Required | Not required |
| Troubleshooting | Manual | Auto-maintained |
| Database | No | Yes (full tracking) |
| Script | merge-deltas.py | apply_deltas.py |
| Backup/Rollback | Limited | Full support |

</details>

---

## ✅ Next Steps

1. Read the new documentation: [CONTEXT_LEARNING.md](CONTEXT_LEARNING.md)
2. Archive any old ACE files you have
3. Start using the new dual-feedback system
4. The new system is already integrated and ready to use

---

**Document Status**: DEPRECATED (replaced 2026-01-08)
**Replacement**: [CONTEXT_LEARNING.md](CONTEXT_LEARNING.md)
