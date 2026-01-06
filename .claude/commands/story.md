# Story Command

Create stories for incremental development on existing codebases.

## Usage

```
/story [feature request]
```

## Examples

```
/story Add CSV export button to the dashboard
/story Implement user profile editing
/story Add dark mode toggle
```

## Behavior

Routes to Story Composer Agent to:

1. Analyze your request
2. Scan existing codebase for patterns
3. Check previous stories for consistency
4. Create properly structured story file(s)
5. Return for approval before implementation

## Prerequisites

For brownfield projects, may require `analysis/brownfield-architecture.md`.

## See Also

Full Story Composer capabilities: `.claude/agents/story-composer-agent.md`
