# Agent-Based Software Development Workflow

This project demonstrates an autonomous, agent-based workflow for software development. It utilizes a "Hub and Spoke" model where a central `Hub Agent` coordinates a team of specialized agents to design, develop, and test a application.

## Project Overview

The core of this project is an automated system that manages the entire development lifecycle, from initial design to final QA. The workflow is orchestrated by a `Hub Agent` that delegates tasks to a set of specialized agents, each with a specific role and responsibility.

### Key Features

- **Autonomous Operation**: Agents operate autonomously between human approval gates, ensuring a streamlined and efficient workflow.
- **Hub and Spoke Model**: A central `Hub Agent` coordinates tasks, while specialized "spoke" agents perform specific functions like system design, frontend and backend development, and testing.
- **Strict State Management**: The project follows a strict state machine, with the status of each task tracked in a `TASK.md` file and individual `Story` files.
- **Human-in-the-Loop (HITL) Gates**: The workflow includes two critical human approval gates for design and final project sign-off, ensuring quality and alignment with project goals.
- **Self-Improving Context System**: Automatically tracks which documentation is actually useful, generates optimization reports every 10 stories, and enforces version compatibility to prevent stale context errors.

## 🚀 Quick Start with Claude Code

This repo is **zero-config** for Claude Code. Just clone and start building!

### One-Time Setup

Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

### Start Building

```bash
# New project (Full POC Mode)
claude code hub "Create a stock trading dashboard with real-time charts"

# Add feature to existing project (Incremental Mode)
claude code hub "/story add CSV export button"
# First time: Runs brownfield analysis (~4 min)
# After that: Asks to use cached analysis (instant if yes)

# Bug fix
claude code hub "/story fix authentication timeout"
# Uses cached analysis (instant)

# Refactor existing code (Brownfield Mode)
claude code hub "/refactor extract shared authentication logic"
# Full analysis + refactoring plan (~7 min)
```

**Mode Comparison:**
- `/story`: Analysis mode (~4 min first time, instant after)
- `/refactor`: Full refactoring mode (~7 min, generates improvement plan)

Both use Brownfield Architect, but `/story` is faster because it only generates what's needed for feature development.

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

✅ **Design & Architecture** - System Design Agent creates comprehensive docs
✅ **Code Generation** - Frontend and Backend agents implement features
✅ **Testing** - Unit tests, integration tests, E2E tests run automatically
✅ **Code Review** - Automated review for quality and standards
✅ **QA Validation** - Final validation before human approval
✅ **Progress Tracking** - Real-time status in `TASK.md`

**You only approve at 2 gates:**
1. After design documents are created (HITL Gate 1)
2. After final QA validation (HITL Gate 2)

### Available Commands

- **`hub`** - Primary command (use this for everything)
- Other commands (`story`, `frontend`, `backend`, etc.) - Manual intervention only

See [.claude/README.md](.claude/quick_start.md) for complete command reference.

### Three Modes of Operation

**Full POC Mode** (for new projects):
```bash
claude code hub "Create a [description]"
```
→ Complete design phase → Human approval → Implementation

**Incremental Mode** (for existing projects):
```bash
claude code hub "/story [feature description]"
```
→ Story creation → Implement now? → Implementation

**Brownfield Mode** (for refactoring):
```bash
claude code hub "/refactor [scope description]"
```
→ Code analysis → Refactoring plan → Human approval → Implementation

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

The framework includes 10 production-grade skills that provide expert guidance automatically:

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

**Code Quality:**
- **debugging-methodology** - Systematic debugging, profiling, root cause analysis
- **circular-dependency-resolver** - Detect and resolve import cycles, DI issues

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
# → Uses: circular-dependency-resolver, debugging-methodology
```

**Location**: Skills are stored in `~/.claude/skills/` - you can customize or add your own.

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


## Usage Modes

This framework supports three modes of operation:

### 1. Full POC Mode (Default)
Traditional workflow with complete design documentation.

**Use for**:
- New projects from scratch
- Major architectural changes
- When comprehensive design docs are needed

**Usage**:
```bash
# Just describe what you want to build
"Create a stock trading dashboard with real-time charts"
```

**Workflow**: Design → Approval → Implementation → Testing → QA → Final Approval

---

### 2. Incremental Mode (`/story` command)
Quick story creation for adding features to existing codebases.

**Use for**:
- Adding features to existing projects
- Bug fixes and enhancements
- When design patterns are already established
- Rapid iterations

**Usage**:
```bash
# Use the /story command
"/story add CSV export button to dashboard"
"/story fix authentication bug in login"
"/story add user profile settings page"
```

**How it works**:
1. Checks for brownfield analysis (runs if missing, asks to reuse if exists)
2. Brownfield Architect runs in analysis-only mode (~4 min if needed)
3. Story Composer creates stories with full codebase context
4. You decide: implement now or later
5. Implementation follows full workflow: [I] → [CR] → [T] → [Q] → [Done]

**First use (no analysis exists)**:
```bash
"/story add notifications"

→ "ℹ️  Running brownfield analysis (~4 min first time)"
→ Creates stories with full codebase context
→ Analysis cached for future /story commands
```

**Subsequent uses (analysis exists)**:
```bash
"/story add dark mode"

→ "📋 Use existing analysis? (yes/no)"
→ If yes: instant story creation
→ If no: regenerates analysis (~4 min)
```

**Workflow**: Brownfield Analysis (analysis mode) → Story Creation → Implementation Decision → [I] → [CR] → [T] → [Q] → [Done]

---

### 3. Brownfield Mode (`/refactor` command)
Analyze existing code and create refactoring plans with risk assessments.

**Use for**:
- Technical debt reduction
- Legacy code modernization
- Extracting shared utilities or services
- Performance optimization
- Architectural improvements
- Code consolidation

**Usage**:
```bash
# Use the /refactor command
"/refactor extract shared authentication logic"
"/refactor modernize API to use async/await"
"/refactor consolidate duplicate validation code"
```

**How it works**:
1. Brownfield Architect runs in full-refactoring mode (~7 min)
2. Generates comprehensive analysis + phased refactoring plan
3. Creates refactoring story files with risk levels
4. You review and approve the plan
5. If approved, stories move to [Pending]
6. You decide: implement now or later
7. Implementation follows full workflow with rollback plans

**Example**:
```bash
"/refactor extract shared auth logic"

→ "🔧 Running full refactoring analysis (~7 min)"
→ Generates brownfield-architecture.md
→ Generates refactoring-plan.md with 3 phases
→ Creates 5 refactoring story files
→ "📋 Review plan: analysis/refactoring-plan.md"
→ "Approve and implement? (yes/no)"
```

**Workflow**: Brownfield Analysis (refactor mode) → Refactoring Plan → Human Approval → Implementation → [I] → [CR] → [T] → [Q] → [Done]

**Key Features**:
- **Auto-installs tools**: Repomix and md-tree install automatically
- **Technical debt assessment**: Identifies code smells, duplications, security issues
- **Phased strategies**: Creates low/medium/high risk phases
- **Risk mitigation**: Includes rollback plans and gradual rollout strategies
- **Human approval gate**: Review and approve refactoring plan before implementation

---

### Command Reference

| Command | Description | Use Case |
|---------|-------------|----------|
| *(no command)* | Full POC workflow | New projects, major features |
| `/story [request]` | Create story files only | Add features, bug fixes, enhancements |

For detailed command usage, see [COMMANDS.md](COMMANDS.md).

## Workflow

The project follows a structured, end-to-end workflow orchestrated by the `Hub Agent`. The workflow consists of the following steps:

1. **Initiation**: The `Hub Agent` confirms the project scope and triggers the `System Design Agent`.
2. **Design**: The `System Design Agent` produces the required design artifacts in the `docs/` directory and automatically shards large implementation documents into subdirectories with enhanced index files for efficient context loading.
3. **Design Approval**: The `Hub Agent` requests human approval for the core design documents.
4. **Decomposition & Task Board Creation**: Upon approval, the `Hub Agent` decomposes the design into `Story` files and creates a `TASK.md` file to track progress.
5. **Implementation & Parallel Review/Testing**: The `Hub Agent` schedules the workflow, triggering the appropriate agents for development, code review, and testing.
6. **Final QA**: Once all stories are complete, the `QA Agent` performs a final validation of the application.
7. **Project Sign-off**: After successful QA, the `Hub Agent` awaits final human approval.

For more detailed information on the agent operating protocol, please refer to the `PROTOCOL.md` file.