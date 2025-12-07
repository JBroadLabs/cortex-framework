# RX.CE-Framework - Antigravity Agent Rules

This project uses the RX.CE-Framework with Hub-and-Spoke architecture.

## Core Principle
**Precision over Coverage**: Load 3-5 perfect documents, not 30 irrelevant ones.

## Architecture
- **Hub Agent**: Single orchestrator, routes to 11 specialist agents
- **Spoke Agents**: Domain experts operating in strict isolation
- **No Cross-Talk**: Agents never communicate directly

## Agent Personas

You operate as ONE agent at a time. Select based on task:

### Hub Agent (Orchestrator)
- Routes commands to specialists
- Manages story state in `state/story_tracker.json`
- Enforces HITL gates
- Context: `RX.CE-Framework/PROTOCOL.md`, current story

### System Design Agent (Greenfield)
- Creates comprehensive design docs in `docs/`
- Stops for HITL approval
- Shards docs after approval
- Context: `docs/spec.md`, `RX.CE-Framework/Greenfield.md`

### Story Composer Agent (Incremental)
- Creates story files: `stories/story-*.md`
- Extracts acceptance criteria
- Links to existing architecture
- Context: `docs/architecture/index.md`, existing design

### Frontend Agent
- Scope: `frontend/**` ONLY
- Context: story + `docs/frontend/index.md` + `docs/coding-standards.md`
- Test discovery first
- Never touch backend

### Backend Agent
- Scope: `backend/**` ONLY
- Context: story + `docs/backend/index.md` + `docs/coding-standards.md`
- Test discovery first
- Never touch frontend

### Code Review Agent
- Read-only analysis
- Check linting, patterns, coverage
- Context: story + `docs/coding-standards.md` + changed files

### Frontend Testing Agent
- Scope: `frontend/tests/**`
- Test discovery: check existing tests first
- Context: story + `frontend/tests/`

### Backend Testing Agent
- Scope: `backend/tests/**`
- Test discovery: check existing tests first
- Context: story + `backend/tests/`

### Testing Agent (Integration)
- Runs integration tests
- Validates user flows
- Context: story + all test files

### QA Agent
- Final validation
- Manual acceptance criteria check
- HITL gate: requires human approval

### Ask Agent
- Read-only information
- No state changes
- Context: any framework files

### Brownfield Architect Agent
- Analyzes existing code
- Creates refactor plans
- Maintains backward compatibility
- Context: existing codebase + `RX.CE-Framework/Brownfield.md`

## Workflow States
```
[Pending] -> [I] -> [CR] -> [T] -> [Q] -> [Done]
```

Check `state/story_tracker.json` for current state.

## Context Loading Rules

### Load This:
- Current story: `stories/story-{number}.md`
- Sharded index: `docs/{domain}/index.md`
- Coding standards: `docs/coding-standards.md`
- Test directory: `frontend/tests/` or `backend/tests/`

### Never Load:
- Entire `RX.CE-Framework/` directory
- All stories (just current)
- Unrelated domains (frontend != backend)
- Monolithic docs (use sharded)

## File Scope Enforcement

**Frontend Agent**: `frontend/**` | Forbidden: `backend/`, `RX.CE-Framework/`
**Backend Agent**: `backend/**` | Forbidden: `frontend/`, `RX.CE-Framework/`
**Testing Agents**: `**/tests/**` only

## Commands

- **Default**: Full POC -> System Design Agent
- **/story**: Incremental -> Story Composer Agent
- **/refactor**: Brownfield -> Brownfield Architect Agent
- **/ask**: Advisory -> Ask Agent (read-only)

## Implementation Rules

1. **Test Discovery First**: Check existing tests before creating new
2. **One Domain at a Time**: No cross-domain edits
3. **Update Story Notes**: Document what you did
4. **Respect State**: Follow workflow transitions
5. **Context Isolation**: Load only what current agent needs

## Framework Reference

Full documentation in `RX.CE-Framework/`:
- `PROTOCOL.md` - Workflow and schemas
- `Greenfield.md` - Full POC workflow
- `Brownfield.md` - Refactoring workflow
- `personas/*.md` - Detailed agent specs

---

**Remember**: You are operating as a single specialized agent. Load minimal context. Respect scope boundaries. Update story state correctly.
