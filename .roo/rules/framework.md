# RX.CE-Framework - Roo Code Rules

## Agent System

**Complete agent definitions**: See root `AGENTS.md` file

## Quick Reference

### Context Loading
- Current story: `stories/story-{number}.md`
- Design: `docs/{domain}/index.md` (sharded)
- Standards: `docs/coding-standards.md`
- Framework: `RX.CE-Framework/PROTOCOL.md`

### Scope Enforcement
**Frontend Agent**: `frontend/**` | Forbidden: `backend/`, `RX.CE-Framework/`
**Backend Agent**: `backend/**` | Forbidden: `frontend/`, `RX.CE-Framework/`

### Test Discovery
Always check `frontend/tests/` or `backend/tests/` BEFORE creating new tests.

### State Management
Update story state in story file after completing work.

---

**For full agent definitions, reference root AGENTS.md file.**
