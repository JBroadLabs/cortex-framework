# Refactor Command

Analyze and refactor existing codebases.

## Usage

```
/refactor [scope or description]
```

## Examples

```
/refactor Extract shared authentication logic
/refactor Modernize the API layer
/refactor Reduce technical debt in user service
```

## Behavior

Routes to Brownfield Architect Agent to:

1. Flatten and analyze the codebase (via Repomix)
2. Assess technical debt and architecture
3. Identify refactoring opportunities
4. Create phased refactoring plan with risk levels
5. Generate atomic stories for implementation

## Output

Creates in `analysis/` directory:
- `flattened-codebase.md` - Codebase snapshot
- `brownfield-architecture.md` - Current state assessment
- `refactoring-plan.md` - Phased strategy with risk levels

**Requires human approval before implementation begins.**

## See Also

Full Brownfield Architect capabilities: `.claude/agents/brownfield-architect-agent.md`
