# Cortex Framework

**An autonomous, multi-agent development framework for [Claude Code](https://claude.com/claude-code).**

Cortex turns Claude Code into a coordinated software team. A central **Hub Agent** orchestrates 13 specialized agents to design, build, review, test, and ship software across two operating modes — **Greenfield** (new projects) and **Brownfield** (existing codebases) — using a strict state machine, mode-aware context isolation, and human approval gates.

> This repository is **zero-config**. Clone it, open Claude Code, and start with a slash command.

---

## Why Cortex

- **Hub-and-spoke orchestration** — one coordinator, 13 focused agents, no chaotic spoke-to-spoke chatter.
- **Stateless, context-isolated agents** — each agent starts clean, loads only what it needs, and clears context on completion. Smaller, cleaner context per step.
- **Universal state machine** — every story flows through `[Pending] → [I] → [CR] → [T] → [Q] → [Done]`, enforced by a SQLite engine.
- **Parallel review** — code review and unit testing run simultaneously at the `[CR]` stage for faster feedback.
- **Human-in-the-loop gates** — you approve at exactly two points (design/plan, then final proofpoint). Everything else is automated.
- **Self-improving docs** — the Context Learning System analyzes agent feedback every 10 stories and proposes evidence-based documentation and troubleshooting updates for you to approve.

---

## Quick Start

**1. Install Claude Code**

```bash
npm install -g @anthropic-ai/claude-code
```

**2. Clone this repo and open it in Claude Code**

```bash
git clone https://github.com/JBroadLabs/cortex-framework.git
cd cortex-framework
claude
```

**3. Drive it with a slash command**

```bash
# New project from scratch (Greenfield)
/greenfield "Create a stock trading dashboard with real-time charts"

# Add a feature to an existing codebase (Brownfield)
/story add CSV export button

# Refactor existing code with risk management (Brownfield)
/refactor extract shared authentication logic

# Read-only advisor — questions, diagnostics, status (changes nothing)
/ask "why is story-042 blocked?"
```

The Hub Agent handles the rest: design, story decomposition, implementation, parallel review, testing, and QA. You only step in at the two approval gates.

| Command | Mode | What it does |
|---|---|---|
| `/greenfield` | Greenfield | Full design phase → sharded docs → implementation |
| `/story` | Brownfield | Analyze codebase (cached) → compose stories → implement |
| `/refactor` | Brownfield | Analyze → risk-assessed refactoring plan → implement |
| `/ask` | Any | Read-only guidance, diagnostics, and status |

---

## The Two Approval Gates

Cortex is autonomous between gates and pauses for you at both:

1. **Gate 1 — Design / Plan.** Approve the design docs (Greenfield) or refactoring plan (Brownfield) by marking the file `[APPROVED]`.
2. **Gate 2 — Proofpoint.** Approve the final `greenfield-proofpoint.md` / `brownfield-proofpoint.md` sign-off.

---

## Repository Layout

```
.
├── .claude/                  # Active Claude Code configuration (this is what runs)
│   ├── commands/             # Slash commands: greenfield, story, refactor, ask
│   ├── agents/               # 13 agent definitions (hub, system-design, frontend, qa, ...)
│   ├── skills/               # Implementation skills (API design, DB schema, perf, ...)
│   ├── quick_start.md        # Short usage guide
│   └── settings.json         # Permissions
│
└── Cortex-Framework/         # Framework source, specification, and full docs
    ├── README.md             # Full reference (deep dive — start here for details)
    ├── PROTOCOL.md           # Universal operating contract for all agents
    ├── AGENTS.md             # Agent roster and rules
    ├── COMMANDS.md           # Complete command reference
    ├── modes/                # Greenfield.md, Brownfield.md workflows
    ├── personas/             # Agent persona definitions
    ├── config/               # Command → agent mappings
    ├── state/                # SQLite schema + agent roster
    ├── docs/                 # Templates, Context Learning, platform setup
    └── scripts/              # State machine engine, delegation, delta application
```

The root `.claude/` directory is the live configuration Claude Code loads. The `Cortex-Framework/` directory is the source of truth for the framework's behavior, schemas, and documentation.

---

## State Machine

Every story — regardless of mode — moves through the same path:

```
[Pending] → [I] → [CR] → [T] → [Q] → [Done]
              │     │
   Implementation   Parallel: Code Review + Frontend/Backend Unit Tests
```

- **[Pending]** — awaiting initiation, approval, or upstream dependencies
- **[I]** — implementation (Frontend/Backend)
- **[CR]** — code review + unit testing, run in parallel
- **[T]** — integration / component testing
- **[Q]** — QA and regression validation
- **[Done]** — completed and approved

A `[Paused]` state handles dependency failures and resource contention. Transitions are enforced by the SQLite engine — no manual configuration needed.

---

## Documentation

| Document | Purpose |
|---|---|
| [Cortex-Framework/README.md](Cortex-Framework/README.md) | Full reference — features, modes, workflows, directory spec |
| [Cortex-Framework/PROTOCOL.md](Cortex-Framework/PROTOCOL.md) | Universal operating contract, state machine, handoff rules |
| [Cortex-Framework/AGENTS.md](Cortex-Framework/AGENTS.md) | Agent roster and responsibilities |
| [Cortex-Framework/COMMANDS.md](Cortex-Framework/COMMANDS.md) | Complete command reference |
| [Cortex-Framework/modes/Greenfield.md](Cortex-Framework/modes/Greenfield.md) | New-project workflow |
| [Cortex-Framework/modes/Brownfield.md](Cortex-Framework/modes/Brownfield.md) | Existing-codebase workflows |
| [Cortex-Framework/docs/CONTEXT_LEARNING.md](Cortex-Framework/docs/CONTEXT_LEARNING.md) | Self-improvement / context learning system |

---

## Prerequisites

- **[Claude Code](https://claude.com/claude-code)** — the agent runtime.
- **Node.js** (v14+) and **npm** — used for `repomix` (codebase flattening) and the markdown sharding tool. Both are installed automatically when needed.
- **Python 3** — used by the workflow engine and utility scripts in `Cortex-Framework/scripts/`.

---

## License

Released under the [MIT License](LICENSE).
