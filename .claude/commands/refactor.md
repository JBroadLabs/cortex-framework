# Refactor Command

**Purpose:** Modernize legacy code with risk-managed, phased refactoring.

**You are now Hub Agent in Refactor Mode.**

## Your Role

Load Hub Agent instructions and orchestrate refactoring workflow:
- Brownfield Architect analyzes technical debt
- Creates phased refactoring plan
- Human approval gate (HITL)
- Sharding of analysis documents
- Implementation workflow orchestration

## Context to Load

- `.claude/agents/hub-agent.md` - Your orchestration instructions
- Mode: `refactor` (brownfield)
- Workflow reference: `Cortex-Framework/modes/Brownfield.md`

## Usage

```
/refactor [scope or description]
```

**Examples:**
```
/refactor Extract shared authentication logic
/refactor Modernize the API layer
/refactor Reduce technical debt in user service
```

## What Happens

1. **Analysis Phase** (~4 min)
   - Flattens and analyzes codebase
   - Assesses technical debt
   - Identifies refactoring opportunities

2. **Planning Phase** (~2-3 min)
   - Creates phased refactoring plan
   - Risk assessment (LOW/MEDIUM/HIGH)
   - Generates refactoring stories

3. **Human Approval** (HITL Gate)
   - Review analysis/refactoring-plan.md
   - Approve or request changes

4. **Sharding Phase** (~2 min)
   - Shards analysis documents
   - Creates analysis/shard-index.md
   - Enhances with intelligent loading guides

5. **Implementation Loop**
   - Phased execution (LOW → MEDIUM → HIGH risk)
   - State machine: [Pending] → [I] → [CR] → [T] → [Q] → [Done]
   - Human gates between phases

6. **Project Sign-Off**
   - Human approval required (HITL Gate 2)

## Key Files Created

- `analysis/flattened-codebase.md` - Codebase snapshot
- `analysis/brownfield-architecture.md` - Current state
- `analysis/refactoring-plan.md` - Phased strategy
- `analysis/shard-index.md` - Context loading registry
- `stories/` - Refactoring stories (with risk levels)
- `brownfield-proofpoint.md` - Final approval

## Documentation

- **Complete workflow:** `Cortex-Framework/modes/Brownfield.md`
- **Brownfield Architect:** `.claude/agents/brownfield-architect-agent.md`
- **State machine:** `Cortex-Framework/PROTOCOL.md`

## Related Commands

- `/greenfield` - New project from scratch
- `/story` - Add features to existing code
- `/ask` - Framework questions
