# Story Command

**Purpose:** Add features to existing codebase (incremental development).

**You are now Hub Agent in Incremental Mode.**

## Your Role

Load Hub Agent instructions and orchestrate incremental workflow:
- Check for brownfield analysis (trigger Brownfield Architect if missing)
- Story Composer creates feature stories using existing patterns
- Implementation workflow orchestration

## Context to Load

- `.claude/agents/hub-agent.md` - Your orchestration instructions
- Mode: `incremental` (brownfield)
- Workflow reference: `RX.CE-Framework/modes/Brownfield.md`

## Usage

```
/story [feature request]
```

**Examples:**
```
/story Add CSV export button to the dashboard
/story Implement user profile editing
/story Add dark mode toggle
```

## Prerequisites

Requires brownfield analysis:
- `analysis/brownfield-architecture.md` - Current codebase assessment
- `analysis/flattened-codebase.md` - Codebase snapshot

If missing, you'll automatically trigger Brownfield Architect (analysis mode, ~3-4 min).

## What Happens

1. **Analysis Check** (~30 sec)
   - Verify brownfield analysis exists
   - Prompt to reuse or regenerate

2. **Story Creation** (~2-3 min)
   - Analyzes user request
   - Discovers existing patterns
   - Creates stories following established conventions

3. **Implementation Loop**
   - State machine: [Pending] → [I] → [CR] → [T] → [Q] → [Done]
   - Agents load context via existing patterns

## Key Files Used

- `analysis/brownfield-architecture.md` - Architecture guide
- `analysis/flattened-codebase.md` - Code reference
- `docs/coding-standards.md` - Quality standards
- `stories/` - Feature stories

## Documentation

- **Complete workflow:** `RX.CE-Framework/modes/Brownfield.md`
- **Story Composer:** `.claude/agents/story-composer-agent.md`
- **State machine:** `RX.CE-Framework/PROTOCOL.md`

## Related Commands

- `/greenfield` - New project from scratch
- `/refactor` - Modernize existing code
- `/ask` - Framework questions
