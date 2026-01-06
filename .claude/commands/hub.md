# Hub Command

The main entry point for the RX.CE-Framework.

## Usage

```
/hub [request]
```

## Examples

```
/hub Create a stock trading dashboard with real-time charts
/hub Continue with story-008
/hub What's the status of current stories?
```

## Behavior

This command activates the Hub Agent for orchestration. The Hub will:

1. Parse your request
2. Determine the appropriate workflow (Greenfield, Incremental, or Refactor)
3. Delegate to specialized subagents as needed
4. Manage state transitions per PROTOCOL.md

## Related Commands

- `/story` - Incremental development (creates stories for existing codebase)
- `/refactor` - Brownfield refactoring (analyzes and plans refactoring)
- `/ask` - Framework questions (read-only guidance)

## See Also

Full Hub Agent capabilities: `.claude/agents/hub-agent.md`
