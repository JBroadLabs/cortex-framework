---
applyTo: "analysis/**/*.md"
description: "Brownfield refactoring mode instructions"
---

# Brownfield Refactoring Mode

When analyzing existing code:

1. Create `analysis/brownfield-architecture.md`
2. Document existing patterns
3. Identify technical debt
4. Propose incremental refactor plan
5. Generate refactor stories

**Constraints**:
- Maintain backward compatibility
- Incremental changes only
- Test coverage required first

See `AGENTS.md` -> Brownfield Architect Agent for full details.
