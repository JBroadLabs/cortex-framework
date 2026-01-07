# Multi-Platform Setup Guide

RX.CE-Framework works with 5 AI coding platforms out of the box.

## Supported Platforms

| Platform | Auto-Loads? | Setup Time | How It Works |
|----------|-------------|------------|--------------|
| Claude Code | Yes | 0 min | Already configured |
| GitHub Copilot | Yes | 0 min | Loads root `AGENTS.md` |
| Antigravity | Yes | 0 min | Loads `.agent/rules.md` |
| Roo Code | Yes | 0 min | Loads root `AGENTS.md` |
| Cursor | Yes | 0 min | Loads via `@AGENTS.md` |

All platforms work 100% automatically with zero user configuration.

---

## Platform-Specific Details

### Claude Code
**Status**: Pre-configured

**Location**: `.claude/config.yml`

**How to use**:
```
# Just start coding - framework is already active
claude code
```

No additional setup needed.

---

### GitHub Copilot
**Status**: Auto-configured (loads root AGENTS.md)

**Locations**:
- `AGENTS.md` (root) - Auto-loaded
- `.github/copilot-instructions.md` - Optional extras
- `.github/instructions/*.instructions.md` - Mode-specific rules

**How to use**:
1. Install GitHub Copilot extension
2. Open project in VS Code
3. Start coding - AGENTS.md loads automatically

**Agent reference**:
```
# In chat, reference agents naturally:
"Act as Frontend Agent and implement story-003"
"Use the System Design Agent to create architecture"
```

Copilot will automatically load the agent definitions from root AGENTS.md.

---

### Antigravity
**Status**: Auto-configured

**Locations**:
- `.agent/rules.md` - Auto-loaded agent definitions
- `.agent/workflows/rx-framework.md` - Workflow automation

**How to use**:
1. Download Antigravity from https://antigravity.google/
2. Open project folder
3. Start coding - `.agent/` config loads automatically

**Workflows**:
Type `/rx-framework` to trigger the Hub-and-Spoke workflow.

---

### Roo Code
**Status**: Auto-configured (loads root AGENTS.md)

**Locations**:
- `AGENTS.md` (root) - Auto-loaded
- `.roo/rules/framework.md` - Optional extras
- `.roomodes` - Custom modes (optional)

**How to use**:
1. Install Roo Code extension in VS Code
2. Configure API key (OpenRouter recommended)
3. Open project - AGENTS.md loads automatically

**Custom modes** (optional):
- Select "hub-agent" mode for orchestration
- Select "frontend-agent" or "backend-agent" for implementation
- Modes defined in `.roomodes` file

---

### Cursor
**Status**: Auto-configured (loads via @ references)

**Locations**:
- `.cursor/rules/index.mdc` - Uses `@AGENTS.md` to auto-load
- `.cursor/rules/*.mdc` - Agent-specific rules

**How to use**:
1. Install Cursor from https://cursor.com/
2. Open project
3. Start coding - rules auto-apply based on file patterns

**How it works**:
- Editing `frontend/` -> frontend.mdc rules apply (loads Frontend Agent definition)
- Editing `backend/` -> backend.mdc rules apply (loads Backend Agent definition)
- `@AGENTS.md` in index.mdc automatically loads full agent system

---

## Deleting Platform Support

Each platform is isolated in its own folder. To disable a platform:

```bash
# Remove Antigravity support
rm -rf .agent/

# Remove GitHub Copilot extras (root AGENTS.md still works)
rm -rf .github/

# Remove Roo Code extras (root AGENTS.md still works)
rm -rf .roo/

# Remove Cursor support
rm -rf .cursor/
```

Root `AGENTS.md` file is shared by Copilot and Roo Code - keep it unless disabling both.

---

## Validation

Run validation script to confirm all configs present:

```bash
bash scripts/validate-configs.sh
```

---

## Universal Best Practices

### 1. Reference Current Story
Always start with: `stories/story-{number}.md`

### 2. Use Sharded Docs
Load `docs/{domain}/index.md`, not monolithic `docs/{domain}.md`

### 3. Test Discovery First
Check existing tests before creating new ones

### 4. Respect Agent Scope
Frontend Agent stays in `frontend/`, Backend Agent stays in `backend/`

### 5. Never Edit Framework
`RX.CE-Framework/` is read-only during implementation

---

## Troubleshooting

### "Context too large"
- Use sharded docs (`docs/*/index.md`) not monolithic
- Load current story only, not all stories
- Check `docs/shard-index.md` for available shards

### "Agent doing wrong things"
- Verify correct agent persona is active
- Query story state from SQLite database using `engine.get_story_status(story_id)`
- Review agent definition in root `AGENTS.md`

### "Can't find design docs"
- Greenfield: Docs are in `docs/{domain}/index.md` (sharded)
- Check `docs/shard-index.md` for registry
- Monolithic docs only exist before approval

---

## Platform Comparison

### Best For

**Claude Code**: Overall best experience, framework optimized for it
**GitHub Copilot**: Easiest setup, great VS Code integration
**Antigravity**: Strong multi-agent coordination, Google ecosystem
**Roo Code**: Most flexible modes, good for experimentation
**Cursor**: Best automatic rule application, `@` references

### All Platforms

- 100% automatic configuration
- Hub-and-Spoke architecture support
- Precision over Coverage context loading
- Deletable platform folders
- Zero user manual references needed

---

## Support

- Framework docs: `RX.CE-Framework/README.md`
- Protocol: `RX.CE-Framework/PROTOCOL.md`
- Agent definitions: `AGENTS.md` (root)
- Platform setup: `docs/PLATFORM_SETUP.md` (this file)
