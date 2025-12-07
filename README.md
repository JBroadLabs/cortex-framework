# RX.CE-Framework Project

A surgical context engineering system for AI-assisted development using Hub-and-Spoke architecture.

## Quick Start

1. Clone this repository
2. Open in your preferred AI coding tool
3. Start coding - the framework activates automatically

## Multi-Platform Support

RX.CE-Framework works **100% automatically** across 5 major AI coding platforms:

| Platform | Status | Setup Required |
|----------|--------|----------------|
| Claude Code | Ready | None - pre-configured |
| GitHub Copilot | Ready | None - auto-loads `AGENTS.md` |
| Antigravity | Ready | None - auto-loads `.agent/` |
| Roo Code | Ready | None - auto-loads `AGENTS.md` |
| Cursor | Ready | None - auto-loads via `@` |

### Zero Configuration Required

All platforms work immediately:
1. Clone this repository
2. Open in your preferred tool
3. Start coding - framework is active

No manual file references. No setup steps. No configuration.

### How It Works

- **GitHub Copilot & Roo Code**: Automatically load root `AGENTS.md`
- **Antigravity**: Automatically loads `.agent/rules.md`
- **Cursor**: Automatically loads via `@AGENTS.md` references
- **Claude Code**: Pre-configured in `.claude/`

### Deleting Unused Platforms

Each platform is isolated - delete the folder to remove support:

```bash
rm -rf .agent/      # Remove Antigravity
rm -rf .github/     # Remove Copilot extras
rm -rf .roo/        # Remove Roo extras
rm -rf .cursor/     # Remove Cursor
```

### Validation

```bash
bash scripts/validate-configs.sh
```

### Documentation

Full setup guide: [docs/PLATFORM_SETUP.md](docs/PLATFORM_SETUP.md)

---

## Architecture

### Hub-and-Spoke Model

- **12 Specialized Agents** operating in strict isolation
- **Hub Agent** = Single orchestrator, routes to specialists
- **Spoke Agents** = Domain experts (Frontend, Backend, Testing, etc.)
- **No Direct Agent Communication** = Context isolation enforced

### Core Principle

**Precision over Coverage**: Load 3-5 perfect documents, not 30 irrelevant ones.

## Workflow States

Stories progress through defined states:

```
[Pending] -> [I] -> [CR] -> [T] -> [Q] -> [Done]
           Implementation  Code Review  Testing  QA  Complete
```

## Commands

- **Default**: Full POC workflow (System Design Agent)
- **/story**: Add incremental feature (Story Composer)
- **/refactor**: Brownfield modernization (Brownfield Architect)
- **/ask**: Get information (Ask Agent, read-only)

## Key Files

- `AGENTS.md` - Complete agent definitions (auto-loaded by most platforms)
- `RX.CE-Framework/PROTOCOL.md` - Story schemas, state transitions
- `RX.CE-Framework/modes/Greenfield.md` - Full POC workflow
- `RX.CE-Framework/modes/Brownfield.md` - Refactoring workflow
- `RX.CE-Framework/personas/*.md` - Detailed agent specifications

## Project Structure

```
AGENTS.md                     # Agent definitions (root level)
RX.CE-Framework/              # Core framework (read-only)
  ├── PROTOCOL.md
  ├── modes/
  │   ├── Greenfield.md
  │   └── Brownfield.md
  └── personas/

.claude/                      # Claude Code config
.agent/                       # Antigravity config
.github/                      # GitHub Copilot config
.roo/                         # Roo Code config
.cursor/                      # Cursor config

docs/                         # Project documentation
stories/                      # Story files
state/                        # State tracking
```

## Why Multi-Platform?

The same **surgical context engineering** works everywhere:
- Load 3-5 perfect docs, not 30 irrelevant ones
- Hub-and-Spoke architecture (12 specialized agents)
- Story-driven development (clear acceptance criteria)
- Choose your preferred tool without losing the framework

---

## License

See LICENSE file for details.
