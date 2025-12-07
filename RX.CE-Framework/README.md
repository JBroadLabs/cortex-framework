# RX.CE Multi-Agent Development Framework

An autonomous, agent-based workflow for software development that uses a "Hub and Spoke" orchestration model. A central Hub Agent coordinates 13 specialized agents to design, develop, test, and deliver applications across two distinct operational modes: Greenfield (new projects) and Brownfield (existing codebases).

## Project Overview

The RX.CE Framework automates the entire development lifecycle through intelligent agent orchestration, strict state management, and mode-aware context isolation. The Hub Agent manages workflow transitions, validates prerequisites, and ensures proper handoffs between specialized agents operating in stateless, context-isolated execution environments.

### Key Features

- **Dual-Mode Architecture**: Explicit mode routing (Greenfield vs Brownfield) with separate context sources, artifacts, and workflows
- **Hub and Spoke Orchestration**: Central Hub Agent coordinates 13 specialized agents with strict spoke-to-Hub-only communication
- **Stateless Agent Execution**: Agents start with empty context, load only required sources, and clear context on completion
- **Universal State Machine**: `[Pending] → [I] → [CR] → [T] → [Q] → [Done]` with configurable stage skips
- **Parallel Execution at [CR]**: Code Review + Frontend Unit Testing + Backend Unit Testing run simultaneously for faster feedback
- **Story-Centric Tracking**: Story files and TASK.md are the single source of truth; no auxiliary trackers
- **Human-in-the-Loop (HITL) Gates**: Two critical approval points with file-based status markers
  - Gate 1: Design artifacts (Greenfield) or Refactor plan (Brownfield)
  - Gate 2: Mode-specific proofpoint files (greenfield-proofpoint.md or brownfield-proofpoint.md)
- **ACE Self-Improvement System**: 95% automated documentation improvement with evidence-based delta proposals every 10 stories
- **Version Compatibility Enforcement**: Strict version checking prevents context mismatches and blocks incompatible stories

## 🚀 Quick Start with Claude Code

This repo is **zero-config** for Claude Code. Just clone and start building!

### One-Time Setup

Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

### Start Building

```bash
# Greenfield Mode: New project from scratch
claude code hub "Create a stock trading dashboard with real-time charts"
# → mode=greenfield → System Design Agent → Full design phase → HITL Gate 1

# Brownfield Mode: Add feature to existing codebase
claude code hub "/story add CSV export button"
# → mode=brownfield → Brownfield Architect (analysis-only, ~4 min first time)
# → Story Composer → User decides: implement now or later
# → Cached analysis used for subsequent /story commands

# Brownfield Mode: Refactor existing code
claude code hub "/refactor extract shared authentication logic"
# → mode=brownfield → Brownfield Architect (full-refactoring, ~7 min)
# → Generates refactoring-plan.md → HITL approval required
# → Creates refactor stories with risk levels and rollback plans
```

**Mode Selection:**
- **Greenfield** (default): Net-new projects, full design phase, monolithic-then-sharded docs
- **Brownfield** (`/story` or `/refactor`): Existing codebases, analysis artifacts, incremental changes

**Command Routing:**
- No command → Greenfield full POC workflow
- `/story [request]` → Brownfield incremental (analysis-only mode, ~4 min first time, cached after)
- `/refactor [scope]` → Brownfield refactoring (full-refactoring mode, ~7 min, HITL approval required)

That's it! The Hub Agent orchestrates everything automatically.

### 🤖 Ask Mode - Your Built-in Framework Expert

Need help? The Ask Agent can answer questions, diagnose issues, and explain concepts without modifying anything.

**Quick Examples:**

```bash
# Troubleshooting
claude code ask "why is story-042 blocked?"
claude code ask "stuck"  # Just one word - finds all blockages!

# Learning
claude code ask "how does sharding work?"
claude code ask "explain the complete workflow"

# Status Checks
claude code ask "project status"
claude code ask "what should I work on next?"

# Best Practices
claude code ask "when to use /story vs full POC?"
claude code ask "how to structure dependencies?"
```

**What Can Ask Mode Do?**

✅ **Diagnose Issues** - Finds why stories are blocked, version mismatches, dependency problems
✅ **Explain Concepts** - How agents work, sharding, versioning, HITL gates
✅ **Check Status** - Project progress, blocking issues, dependency chains
✅ **Provide Guidance** - Best practices, command suggestions, workflow optimization
✅ **Intelligent Understanding** - Understands vague questions like "stuck" or "help"

❌ **Cannot** - Modify files, change statuses, trigger agents (read-only advisor)

See full capabilities in [Ask Agent Documentation](.claude/commands/ask.md).

### What Happens Automatically

✅ **Mode-Aware Context Loading** - Hub loads greenfield or brownfield context sources based on mode
✅ **Design & Architecture** - System Design Agent (Greenfield) or Brownfield Architect (Brownfield)
✅ **Story Creation** - Hub decomposes design into story files with canonical schema
✅ **Parallel Code Review** - At [CR]: Code Review + Frontend Unit Testing + Backend Unit Testing run simultaneously
✅ **Testing** - Integration tests ([T]) and QA validation ([Q]) with regression suites
✅ **Coding Standards Enforcement** - Implementation and review agents enforce docs/coding-standards.md
✅ **Progress Tracking** - Story files and TASK.md are the single source of truth
✅ **Version Compatibility** - Strict checking blocks stories with incompatible doc versions

**You only approve at 2 gates:**
1. **HITL Gate 1**: Design docs (Greenfield) or refactor plan (Brownfield) - change status to `[APPROVED]`
2. **HITL Gate 2**: Mode-specific proofpoint file (greenfield-proofpoint.md or brownfield-proofpoint.md) - change status to `[APPROVED]`

### Available Commands

- **`hub`** - Primary command for all workflows (Greenfield and Brownfield)
- **`ask`** - Read-only advisory mode for questions and diagnostics
- Other commands (`frontend`, `backend`, `code-review`, etc.) - Manual intervention only (invoked by Hub)

See [.claude/quick_start.md](.claude/quick_start.md) and [COMMANDS.md](COMMANDS.md) for complete command reference.

### Operational Modes

The framework operates in two distinct modes with separate context sources and workflows:

**Greenfield Mode** (Net-new projects):
```bash
claude code hub "Create a stock trading dashboard"
```
**Workflow**: System Design Agent → Monolithic docs → HITL Gate 1 → Document sharding → Story creation → Implementation → greenfield-proofpoint.md → HITL Gate 2

**Context Sources**: `docs/spec.md`, `docs/architecture.md`, `docs/design.md`, `docs/frontend.md`, `docs/backend.md` (pre-approval), then sharded via `docs/shard-index.md` (post-approval)

---

**Brownfield Mode - Incremental** (`/story`):
```bash
claude code hub "/story add CSV export button"
```
**Workflow**: Brownfield Architect (analysis-only, ~4 min first time) → Story Composer → User decision (implement now?) → Implementation → brownfield-proofpoint.md → HITL Gate 2

**Context Sources**: `analysis/flattened-codebase.md`, `analysis/brownfield-architecture.md`

**Caching**: Analysis cached for subsequent `/story` commands (instant if reused)

---

**Brownfield Mode - Refactoring** (`/refactor`):
```bash
claude code hub "/refactor extract shared authentication logic"
```
**Workflow**: Brownfield Architect (full-refactoring, ~7 min) → Generates `analysis/refactoring-plan.md` → HITL Gate 1 (human approval required) → Story creation → Implementation → brownfield-proofpoint.md → HITL Gate 2

**Context Sources**: `analysis/flattened-codebase.md`, `analysis/brownfield-architecture.md`, `analysis/refactoring-plan.md`

**Key Features**: Risk assessment, phased strategies, rollback plans

---

## ACE - Agentic Context Engineering (Built-In)

This framework includes **ACE** - a 95% automated self-improvement system for documentation:

- **🤖 Automatic Feedback Collection**: Agents log helpful/misleading bullets during implementation (~2 min/story)
- **📊 Evidence-Based Analysis**: Every 10 stories, Reflector Agent analyzes patterns automatically
- **🎯 Smart Proposals**: Generates delta proposals (ADD/UPDATE/DEPRECATE) with evidence
- **✅ Human-Approved**: You review and approve changes in ~5 minutes every 10 stories
- **🔄 Auto-Applied**: Approved changes merged automatically with version bumps
- **📌 Version Safety**: Documents versioned; mismatches block implementation

**How it works:**
1. Agents add Context Feedback to each story (~2 min)
2. Every 10 stories, system analyzes feedback and proposes improvements
3. You review proposals backed by evidence (~5 min)
4. Approved changes auto-applied to documentation
5. Context stays accurate with zero manual maintenance

**Time investment**: ~27 min per 10 stories (vs 20 min manual updates)
**Automation**: 95% (human only approves evidence-based deltas)

See [docs/CONTEXT_ENGINEERING.md](docs/CONTEXT_ENGINEERING.md) for complete guide.

---

## 🎯 Built-In Skills System

The framework includes 12 production-grade skills that provide expert guidance automatically:

### Available Skills

**Backend & API:**
- **api-design** - REST/GraphQL patterns, versioning, pagination, error responses
- **database-schema-design** - Normalization, indexing, migrations, query optimization
- **async-background-jobs** - Job queues (Bull/Redis/SQS), workers, scheduling, retries
- **integration-patterns** - Microservices, event-driven, messaging, distributed systems
- **error-handling** - Retry strategies, logging, dead letter queues, graceful degradation
- **performance-optimization** - Database queries, caching, frontend/backend optimization

**Frontend:**
- **css-styling-expert** - Flexbox, Grid, animations, responsive design, accessibility
- **state-management** - State architecture, Redux, Context API, Zustand patterns

**Code Quality:**
- **code-review** - Best practices, anti-patterns, security vulnerabilities, maintainability
- **circular-dependency-resolver** - Detect and resolve import cycles, DI issues
- **implementation-best-practices** - Clean code, SOLID principles, design patterns

**Decision Making:**
- **critical-thinking** - Decision frameworks, trade-off analysis, problem-solving

### How It Works

✅ **Automatic** - Skills load automatically when relevant to your task
✅ **Zero Config** - Works out of the box with Claude Code
✅ **Combined** - Multiple skills can be used together (e.g., API design + database + error handling)

### Examples

```bash
# Building an API endpoint
# → Uses: api-design, database-schema-design, error-handling

# Optimizing slow queries
# → Uses: performance-optimization, database-schema-design

# Setting up background jobs
# → Uses: async-background-jobs, error-handling, integration-patterns

# Fixing circular dependency error
# → Uses: circular-dependency-resolver, code-review
```

**Location**: Skills are stored in both `RX.CE-Framework/skills/` and `.claude/skills/` - you can customize or add your own.

---

## Simple Configuration

Customize the framework with a single YAML file.

### Zero Setup Required

Config file auto-creates on first use with sensible defaults.

```bash
# First run - config creates automatically
claude code hub "Create my app"

✅ Created .claude/config.yml
📋 Active Workflow: [Pending] → [I] → [CR] → [T] → [Q] → [Done]
```

### Customize Anytime

```bash
# Edit the config
nano .claude/config.yml
```

**Common customizations:**

```yaml
# Fast prototyping (skip all validation)
skip_code_review: true
skip_testing: true
skip_qa: true
# Result: [I] → [Done]

# Trust tests only (skip manual reviews)
skip_code_review: true
skip_qa: true
# Result: [I] → [T] → [Done]

# Lower coverage for prototyping
min_coverage_percent: 50

# Disable strict version checking
strict_version_checking: false
```

### Available Settings

- `skip_code_review` - Skip [CR] stage (true/false)
- `skip_testing` - Skip [T] stage (true/false)
- `skip_qa` - Skip [Q] stage (true/false)
- `coding_standards` - Enforce linters (true/false)
- `strict_version_checking` - Block on version mismatch (true/false)
- `min_coverage_percent` - Test coverage threshold (0-100)
- `sharding_threshold` - Lines before doc sharding (default: 500)

**All settings have inline help in `.claude/config.yml`**

---

## Coding Standards (Built-In)

This framework includes automated coding standards enforcement:

- **📏 Defined Standards**: `docs/coding-standards.md` contains all project standards
- **🤖 Auto-Enforcement**: Implementation agents follow standards automatically
- **✅ Auto-Validation**: Code Review agent validates and runs linters
- **🔧 Customizable**: Edit standards file to match your preferences

**Workflow**:
1. System Design Agent creates standards with sensible defaults
2. You review and customize (or use defaults)
3. Implementation agents write code following standards
4. Code Review agent validates compliance and runs linters
5. Stories cannot pass review if standards violated (unless overridden)

**Supported Languages**:
- Python (Ruff, mypy, Google docstrings)
- JavaScript (ESLint, Prettier, JSDoc)
- TypeScript (ESLint, tsc, JSDoc)

**Zero Manual Setup**: All linters run automatically during code review.

---

## Getting Started

To get started with this project, you will need to have a development environment with the necessary tools installed.

### Prerequisites

- **Node.js** (v14 or higher) - Required for repomix and md-tree tools
- **npm** - Comes with Node.js

**Windows/macOS/Linux users**:
1. Install [Node.js](https://nodejs.org/) (includes npm)

**Automatic Installation**:
  - `repomix` - Code flattening tool with AI optimization (installed automatically via npm)
  - Token counting and compression built-in
  - `@kayvan/markdown-tree-parser` - Document sharding tool (installed automatically when needed)
  - No manual installation required.

### Setup and Configuration

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yeri-jeon/rx-hackathon
   ```


## Universal State Machine & Workflow

All stories follow the same state machine regardless of mode:

```
[Pending] → [I] → [CR] → [T] → [Q] → [Done]
              ↑               ↑
       Implementation    Parallel Execution
       (Frontend/       (Code Review +
        Backend)         Unit Tests)
```

### State Definitions

- **[Pending]** - Awaiting initiation, approval, or upstream dependencies
- **[Paused]** - Temporarily halted due to dependency failure or resource contention
- **[I]** - Implementation in progress (Frontend/Backend as applicable)
- **[CR]** - Code review + unit testing (parallelized: Code Review Agent + Frontend Unit Testing + Backend Unit Testing)
- **[T]** - Integration/component testing
- **[Q]** - Quality assurance/regression validation
- **[Done]** - Completed and approved

### Configurable Stage Skips

Customize workflow in `.claude/config.yml`:

```yaml
skip_code_review: false  # true = skip [CR] stage
skip_testing: false      # true = skip [T] stage
skip_qa: false          # true = skip [Q] stage
```

**Examples**:
- Fast prototyping: All true → `[I] → [Done]`
- Trust tests only: `skip_code_review=true, skip_qa=true` → `[I] → [T] → [Done]`

### Parallel Execution at [CR]

When a story transitions to `[CR]`, up to three agents run simultaneously:

```
[I] Implementation Complete
    ↓
[CR] Code Review Stage (PARALLEL)
    ├─→ Code Review Agent (quality, standards, linters)
    ├─→ Frontend Unit Testing Agent (if frontend changes)
    └─→ Backend Unit Testing Agent (if backend changes)
    ↓
[T] Integration Testing (if all pass)
```

The Hub Agent waits for all parallel agents to complete before advancing to `[T]`.

### Context Isolation & Checkpoints

**Rules**:
1. One story per agent context at a time
2. Mandatory reset before ANY work (new or remediation): clear loaded docs, working memory, patterns
3. Checkpoint at `[I] → [CR]`: record loaded docs (with versions), key patterns, decisions
4. Remediation restore (`[CR] → [I]` or `[T] → [I]`): clear context, restore from checkpoint, apply feedback
5. Pause save (`[I] → [Paused]`): save progress, note partial work and resume point

---

## Mode-Specific Workflows

### Greenfield Mode (Net-New Projects)

**Trigger**: Default command (no prefix)

**End-to-End Workflow**:
1. **Initiation**: Hub confirms scope, triggers System Design Agent
2. **Design**: System Design Agent produces monolithic docs in `docs/`:
   - `spec.md`, `architecture.md`, `design.md`, `frontend.md`, `backend.md`, `coding-standards.md`
3. **HITL Gate 1**: Human reviews and approves design docs (status: `[PENDING_APPROVAL]` → `[APPROVED]`)
4. **Document Sharding**: Hub triggers sharding; docs split into directories with `index.md` entrypoints
5. **Decomposition**: Hub creates story files from approved design using `docs/templates/story-template.md`
6. **Implementation**: Stories flow through universal state machine with parallel [CR] execution
7. **Final QA**: QA Agent validates against acceptance criteria and regression suite
8. **HITL Gate 2**: Hub creates `greenfield-proofpoint.md` (status: `[PENDING_APPROVAL]` → `[APPROVED]`)

**Context Sources**:
- Pre-approval: Monolithic docs (`docs/*.md`)
- Post-approval: Sharded docs via `docs/shard-index.md`

**Deliverables**:
- Core documentation (monolithic → sharded)
- Story files in `stories/`
- TASK.md task board
- Complete test suite
- greenfield-proofpoint.md

---

### Brownfield Mode - Incremental (`/story`)

**Trigger**: `/story [feature description]`

**End-to-End Workflow**:
1. **Story Command**: User provides `/story [request]`
2. **Prerequisite Check**: Hub checks for `analysis/brownfield-architecture.md`
3. **Analysis (First Time)**:
   - Brownfield Architect runs in **analysis-only mode** (~4 min)
   - Generates `analysis/flattened-codebase.md` and `analysis/brownfield-architecture.md`
   - Analysis cached for future commands
4. **Analysis (Subsequent)**:
   - Hub asks: "Use existing analysis? (yes/no)"
   - If yes: instant (uses cached analysis)
   - If no: regenerates analysis (~4 min)
5. **Story Creation**: Story Composer creates story files with codebase context
6. **User Decision**: Hub prompts "Implement now? (yes/no/select)"
7. **Implementation**: If yes, stories flow through universal state machine
8. **Final QA**: QA Agent validates with regression suite
9. **HITL Gate 2**: Hub creates `brownfield-proofpoint.md` (status: `[PENDING_APPROVAL]` → `[APPROVED]`)

**Context Sources**:
- `analysis/flattened-codebase.md` (auto-generated codebase snapshot)
- `analysis/brownfield-architecture.md` (architecture assessment)

**Key Features**:
- First use: ~4 min analysis (one-time cost)
- Subsequent uses: instant if analysis reused
- No HITL Gate 1 (no design approval needed)

---

### Brownfield Mode - Refactoring (`/refactor`)

**Trigger**: `/refactor [scope description]`

**End-to-End Workflow**:
1. **Refactor Command**: User provides `/refactor [scope]`
2. **Brownfield Analysis**: Brownfield Architect runs in **full-refactoring mode** (~7 min):
   - Flattens codebase
   - Analyzes code patterns and technical debt
   - Detects code smells and architectural issues
   - Identifies refactoring opportunities
3. **Document Generation**:
   - `analysis/flattened-codebase.md` (auto-generated snapshot)
   - `analysis/brownfield-architecture.md` (current state assessment)
   - `analysis/refactoring-plan.md` (phased strategy with risk levels)
4. **Sharding** (if needed): Documents >500 lines sharded with index files
5. **Story Generation**: Creates refactoring story files with:
   - Risk level assessment (Low/Medium/High)
   - Rollback plans
   - Phased strategy
6. **HITL Gate 1**: Human reviews and approves `analysis/refactoring-plan.md` (status: `[PENDING_APPROVAL]` → `[APPROVED]`)
7. **Implementation**: If approved, stories flow through universal state machine
8. **Final QA**: QA Agent validates with regression suite
9. **HITL Gate 2**: Hub creates `brownfield-proofpoint.md` (status: `[PENDING_APPROVAL]` → `[APPROVED]`)

**Context Sources**:
- `analysis/flattened-codebase.md`
- `analysis/brownfield-architecture.md`
- `analysis/refactoring-plan.md`

**Key Features**:
- Technical debt assessment
- Phased refactoring strategies (Low/Medium/High risk)
- Rollback plans and gradual rollout strategies
- HITL approval gate before implementation

---

### Command Comparison

| Command | Mode | Duration | Context Generated | HITL Gate 1 | Use Case |
|---------|------|----------|-------------------|-------------|----------|
| *(none)* | Greenfield | Varies | Monolithic docs → Sharded docs | Yes (design docs) | New projects |
| `/story` | Brownfield | ~4 min (first time), instant (cached) | Analysis artifacts | No | Feature additions, bug fixes |
| `/refactor` | Brownfield | ~7 min | Analysis + Refactoring plan | Yes (refactor plan) | Technical debt, code improvements |

For detailed command usage, see [COMMANDS.md](COMMANDS.md).

## Agent Roster

The framework includes 13 specialized agents coordinated by the Hub Agent:

| Agent | Role | Active States | Description |
|-------|------|---------------|-------------|
| **Hub Agent** | Orchestrator | All | Central coordinator, manages state transitions, validates prerequisites |
| **System Design Agent** | Design | [I], [CR] | Creates comprehensive design docs for Greenfield projects |
| **Brownfield Architect** | Analysis | [Pending], [I], [CR] | Analyzes existing codebases, generates refactoring plans |
| **Story Composer** | Planning | [Pending], [I] | Creates story files from design or brownfield analysis |
| **Frontend Agent** | Implementation | [I], [CR] | Implements frontend features and components |
| **Backend Agent** | Implementation | [I], [CR] | Implements backend services and APIs |
| **Code Review Agent** | Review | [CR] | Reviews code quality, enforces standards, runs linters |
| **Frontend Unit Testing** | Testing | [CR], [T] | Creates and runs frontend unit tests |
| **Backend Unit Testing** | Testing | [CR], [T] | Creates and runs backend unit tests |
| **Testing Agent** | Testing | [T], [Q] | Runs integration and E2E tests |
| **QA Agent** | Validation | [Q], [Done] | Final validation with regression suites |
| **Reflector Agent** | Improvement | [CR], [T], [Q], [Done] | Analyzes Context Feedback, generates delta proposals (ACE) |
| **Ask Agent** | Advisory | All (read-only) | Provides guidance, diagnostics, framework Q&A |

### Agent Communication Protocol

- **Hub-to-Spoke**: Hub invokes specialized agents via command routing
- **Spoke-to-Hub**: Agents report results in Story files under `## Review & Testing Notes`
- **No Spoke-to-Spoke**: Direct agent communication prohibited; Hub manages all integration
- **Stateless Execution**: Agents clear context on completion and reload fresh for each story

For complete agent details, see [AGENTS.md](AGENTS.md) and [PROTOCOL.md](PROTOCOL.md).

---

## Directory Structure

The framework uses a canonical directory structure with mode-specific artifacts:

```
RX.CE-Framework/                    # Framework core
├── .claude/                        # Claude Code configuration
│   ├── commands/                   # Agent command definitions
│   │   ├── hub.md                  # Hub Agent orchestrator
│   │   ├── ask.md                  # Advisory agent
│   │   ├── story-composer.md       # Story creation
│   │   ├── system-design.md        # Greenfield design
│   │   ├── brownfield-architect.md # Brownfield analysis
│   │   ├── frontend.md             # Frontend implementation
│   │   ├── backend.md              # Backend implementation
│   │   ├── code-review.md          # Code review
│   │   ├── frontend-unit-test.md   # Frontend unit tests
│   │   ├── backend-unit-test.md    # Backend unit tests
│   │   ├── test.md                 # Integration testing
│   │   ├── qa.md                   # QA validation
│   │   └── reflector.md            # ACE self-improvement
│   ├── config.yml                  # Framework configuration
│   └── quick_start.md              # Quick start guide
├── PROTOCOL.md                     # Universal operating contract
├── AGENTS.md                       # Agent roster and rules
├── COMMANDS.md                     # Command reference
├── modes/                          # Mode-specific workflows
│   ├── Greenfield.md               # Net-new projects
│   └── Brownfield.md               # Existing codebases
├── personas/                       # Agent persona definitions
├── config/                         # Agent command mappings
├── state/                          # Runtime state and registries
│   ├── agents_roster.yaml          # Agent eligibility
│   ├── artifacts.greenfield.json   # Greenfield artifact registry
│   └── artifacts.brownfield.json   # Brownfield artifact registry
├── docs/                           # Documentation and templates
│   ├── templates/                  # Story and handoff schemas
│   └── CONTEXT_ENGINEERING.md      # ACE system documentation
├── skills/                         # Implementation skills
│   ├── api-design/
│   ├── database-schema-design/
│   ├── async-background-jobs/
│   ├── error-handling/
│   ├── performance-optimization/
│   └── [12 total skills]
└── scripts/                        # Utility scripts
    └── merge-deltas.py             # ACE delta merging

# Project-level structure (generated during usage)
TASK.md                             # Project task board
stories/                            # Story files (single source of truth)
└── story-*.md                      # Individual work units

# Greenfield artifacts
docs/                               # Design documentation
├── spec.md                         # Functional specification (monolithic)
├── architecture.md                 # System architecture (monolithic)
├── design.md                       # High-level design (monolithic)
├── frontend.md                     # Frontend plan (monolithic)
├── backend.md                      # Backend plan (monolithic)
├── coding-standards.md             # Coding standards (MUST exist)
├── shard-index.md                  # Shard registry (post-approval)
├── design/                         # Sharded design (post-approval)
│   └── index.md                    # Design shard entrypoint
├── architecture/                   # Sharded architecture (post-approval)
│   └── index.md                    # Architecture shard entrypoint
├── frontend/                       # Sharded frontend plan (post-approval)
│   └── index.md                    # Frontend shard entrypoint
└── backend/                        # Sharded backend plan (post-approval)
    └── index.md                    # Backend shard entrypoint
greenfield-proofpoint.md            # Final sign-off (HITL Gate 2)

# Brownfield artifacts
analysis/                           # Brownfield analysis
├── flattened-codebase.md           # Auto-generated codebase snapshot
├── brownfield-architecture.md      # Architecture assessment
└── refactoring-plan.md             # Refactoring plan (refactor mode only)
brownfield-proofpoint.md            # Final sign-off (HITL Gate 2)

# Implementation modules (as applicable)
frontend/                           # Frontend module
├── src/                            # Implementation
└── tests/                          # Unit/integration/E2E tests

backend/                            # Backend module
├── src/                            # Implementation
└── tests/                          # Unit/integration/E2E tests
```

**Key Principles**:
- **Story files** are the single source of truth for work units
- **TASK.md** is the project-level rollup
- **Mode separation**: Greenfield uses `docs/`, Brownfield uses `analysis/`
- **No auxiliary trackers**: Story files contain all runtime state
- **Coding standards MUST exist**: `docs/coding-standards.md` is mandatory and enforced

---