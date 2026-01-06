# Ask Command

Get help and answers about the RX.CE-Framework.

## Usage

```
/ask [question]
```

## Examples

```
/ask Why is story-042 blocked?
/ask How does the code review workflow work?
/ask What's the difference between /story and /refactor?
/ask Show me the current project status
```

## Behavior

Routes to Ask Agent for read-only assistance:

- Answers questions about the framework
- Diagnoses issues with stories or workflows
- Explains concepts and patterns
- Shows project status and blockers

**Does NOT modify files or trigger workflows.**

## See Also

Full Ask Agent capabilities: `.claude/agents/ask-agent.md`
