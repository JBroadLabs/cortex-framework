# RX.CE-Framework - GitHub Copilot Instructions

This repository uses RX.CE-Framework with Hub-and-Spoke architecture.

## Key Information

**Agent Definitions**: See root `AGENTS.md` file for complete agent system
**Architecture**: Hub-and-Spoke with 12 specialized agents
**Core Principle**: Precision over Coverage - load 3-5 docs, not 30

## Quick Context References

When implementing:
- Current story: `stories/story-{number}.md`
- Architecture: `docs/architecture/index.md`
- Standards: `docs/coding-standards.md`
- Framework: `RX.CE-Framework/PROTOCOL.md`

## Scope Rules

**Frontend Agent**: Only modify `frontend/**`
**Backend Agent**: Only modify `backend/**`
**Never modify**: `RX.CE-Framework/` directory

## Workflow States

Stories progress: `[Pending] -> [I] -> [CR] -> [T] -> [Q] -> [Done]`

Check current state in `state/story_tracker.json`

## Commands

- Default: Full POC workflow
- `/story`: Add incremental feature
- `/refactor`: Brownfield modernization
- `/ask`: Get information (read-only)

---

**For complete agent definitions and detailed instructions, reference the root AGENTS.md file.**
