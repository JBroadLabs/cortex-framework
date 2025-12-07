---
description: RX.CE-Framework Hub-and-Spoke Workflow
---

# RX.CE-Framework Workflow

This workflow implements the Hub-and-Spoke agent orchestration pattern.

## Step 1: Determine Mode

Ask yourself: What type of task is this?

- **Full POC / New Project** -> System Design Agent
- **Add Feature** -> Story Composer Agent
- **Refactor Code** -> Brownfield Architect Agent
- **Get Information** -> Ask Agent

## Step 2: Load Context

Load ONLY what the current agent needs:

### For System Design Agent:
- `docs/spec.md`
- `RX.CE-Framework/Greenfield.md`

### For Story Composer:
- `docs/architecture/index.md`
- `docs/design/index.md`

### For Implementation Agents (Frontend/Backend):
- `stories/story-{number}.md`
- `docs/{domain}/index.md` (frontend or backend)
- `docs/coding-standards.md`
- `{domain}/tests/` (for test discovery)

### For Review Agents:
- `stories/story-{number}.md`
- `docs/coding-standards.md`
- Changed files only

## Step 3: Execute Task

Follow agent-specific rules from `.agent/rules.md`

## Step 4: Update State

Update story state in the story file:
```markdown
## State: [NewState]
## Notes:
- What you did
- Any issues encountered
- Next steps
```

## Step 5: Hand Off

Return control to Hub Agent or wait for next command.

---

**Key Principle**: Precision over Coverage - Load 3-5 documents, not 30.
