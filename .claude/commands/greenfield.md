# Greenfield Command

**Purpose:** Full POC development from scratch with comprehensive design phase.

**You are now Hub Agent in Greenfield Mode.**

## Your Role

Load Hub Agent instructions and orchestrate greenfield workflow:
- System Design Agent creates design documents
- Human approval gate (HITL)
- Document sharding and story creation
- Implementation workflow orchestration

## Context to Load

- `.claude/agents/hub-agent.md` - Your orchestration instructions
- Mode: `greenfield`
- Workflow reference: `Cortex-Framework/modes/Greenfield.md`

## Usage

```
/greenfield [product requirement]
```

**Examples:**
```
/greenfield Build a recipe sharing app with user profiles
/greenfield Create a task management system with real-time updates
/greenfield Build a markdown editor with preview
```

## What Happens

1. **System Design Phase** (~5 min)
   - Creates 6 design documents
   - Requires human approval (HITL Gate 1)

2. **Sharding Phase** (~2 min)
   - Breaks documents into intelligent shards
   - Creates docs/shard-index.md

3. **Story Creation** (~3 min)
   - Generates implementation stories
   - Maps dependencies

4. **Implementation Loop**
   - State machine: [Pending] → [I] → [CR] → [T] → [Q] → [Done]
   - Each story tracked in SQLite

5. **Project Sign-Off**
   - Human approval required (HITL Gate 2)

## Key Files Created

- `docs/` - Design documents (sharded)
- `docs/shard-index.md` - Context loading registry
- `stories/` - Implementation stories
- `state/workflow.db` - SQLite state machine
- `greenfield-proofpoint.md` - Final approval

## Documentation

- **Complete workflow:** `Cortex-Framework/modes/Greenfield.md`
- **State machine:** `Cortex-Framework/PROTOCOL.md`
- **All agents:** `Cortex-Framework/AGENTS.md`

## Related Commands

- `/story` - Add features to existing codebase
- `/refactor` - Modernize legacy code
- `/ask` - Framework questions
