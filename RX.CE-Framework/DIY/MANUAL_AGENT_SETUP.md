# Manual Agent Setup Guide

This guide shows you how to use this framework's agent specifications with popular AI coding assistants.

Note: This framework is ~80% autonomous, out of the box with Claude code, for manual DIY setup read below.

**One-time setup (2-5 minutes) → Start building with agents!**

---

## Table of Contents

1. [Quick Platform Selection](#quick-platform-selection)
2. [Universal: AGENTS.md (Recommended)](#universal-agentsmd-recommended)
3. [GitHub Copilot Setup](#github-copilot-setup)
4. [Cursor Setup](#cursor-setup)
5. [Roo Code Setup](#roo-code-setup)
6. [OpenAI Codex CLI Setup](#openai-codex-cli-setup)
7. [Workflow Guide](#workflow-guide)
8. [Complete Example](#complete-example)
9. [Troubleshooting](#troubleshooting)

---

## Quick Platform Selection

**Pick your tool and follow that section:**

| Tool | Setup Time | Best For | 2025 Status |
|------|------------|----------|-------------|
| **Claude Code** | 0 min | Full automation (recommended) | ✅ Native |
| **AGENTS.md** | 1 min | Universal cross-platform | ✅ 2025 Standard |
| **OpenAI Codex CLI** | 2 min | Terminal coding agent | ✅ Supported |
| **GitHub Copilot** | 0 min (setup files included) | VS Code users | ✅ Supported |
| **Cursor** | 0 min (setup files included) | Cursor IDE users | ✅ Supported |
| **Roo Code** | 0 min (setup files included) | Terminal-first developers | ✅ Supported |

**Pick one and follow the instructions below.**

---

## Universal: AGENTS.md (Recommended)

**The 2025 cross-platform standard for AI coding assistants.**

### What is AGENTS.md?

AGENTS.md is an emerging standard (2025) that allows you to define agent behaviors in a single file that works across multiple AI coding tools (Copilot, Cursor, Roo Code, and more).

**Key Benefits:**
- ✅ Write once, works everywhere
- ✅ Standardized format
- ✅ Supported by major AI coding tools
- ✅ Simple natural language instructions

### One-Time Setup (1 minute)

**Good news: This framework already has AGENTS.md!**

Open terminal in your project root:

```bash
# Check if AGENTS.md exists
ls RX.CE-Framework/AGENTS.md

# If it exists, you're done! Just use it.
# If not, create a symlink/copy:
cp RX.CE-Framework/AGENTS.md ./AGENTS.md
```

### What's in AGENTS.md?

Your framework's AGENTS.md defines the complete agent workflow. AI tools automatically read this file and understand how to work with your project.

### Usage with Different Tools

**GitHub Copilot:**
```
You: "Follow the agents defined in AGENTS.md"
Copilot: [Reads AGENTS.md automatically]
         [Understands Hub Agent, Frontend Agent, Backend Agent, etc.]

You: "Act as Hub Agent and create a story for CSV export"
Copilot: [Follows Hub Agent workflow from AGENTS.md]
```

**Cursor:**
```
You: "@AGENTS.md act as Hub Agent"
Cursor: [Loads AGENTS.md]
        [Executes Hub Agent workflow]
```

**Roo Code:**
```
You: "Read AGENTS.md and act as Hub Agent"
Roo: [Understands the complete agent system]
     [Follows Hub Agent protocol]
```

### How It Works

1. Your AI tool reads `AGENTS.md` (automatically or when referenced)
2. It understands the complete agent structure and workflows
3. When you say "act as [Agent Name]", it loads that agent's persona from `RX.CE-Framework/personas/`
4. The agent follows its defined workflow from PROTOCOL.md

**That's it!** This is the simplest, most universal approach.

---

## GitHub Copilot Setup

**For VS Code users with GitHub Copilot**

### Understanding Copilot's Capabilities

GitHub Copilot (2025) supports:
- ✅ `.github/copilot-instructions.md` - Repository-wide instructions (automatic)
- ✅ `AGENTS.md` - Agent definitions (automatic)
- ✅ `.github/instructions/*.instructions.md` - File-specific instructions
- ✅ Chat mode with custom personas

### Setup Status: Already Complete!

**Setup files are already included in this framework.** These files are auto-loaded when you open the project in VS Code with GitHub Copilot.

Included files:
- `.github/copilot-instructions.md` - Lists all 12 agents with activation patterns

### Reference: Manual Setup Instructions (already done)

If you need to recreate the setup files, here are the reference instructions.

Open terminal in your project root:

```bash
# Step 1: Create .github directory if it doesn't exist
mkdir -p .github

# Step 2: Create copilot-instructions.md that references your framework
cat > .github/copilot-instructions.md << 'EOF'
# Context Engineering Framework - GitHub Copilot Integration

This repository uses an agent-based development framework with specialized AI agents.

## Framework Location
All agent definitions: `RX.CE-Framework/personas/`
Agent coordination: `RX.CE-Framework/AGENTS.md`
Operating protocol: `RX.CE-Framework/PROTOCOL.md`

## How to Use Agents

When the user says "act as [Agent Name]", follow these steps:

1. Read `RX.CE-Framework/AGENTS.md` to understand the agent system
2. Read `RX.CE-Framework/personas/[agent-name]_agent.md` for specific agent instructions
3. Follow the agent's workflow exactly as defined
4. Reference `RX.CE-Framework/PROTOCOL.md` for state machine rules
5. Update story files in `/stories/` directory

## Available Agents

**Core Workflow Agents:**
- **Hub Agent** (`RX.CE-Framework/personas/hub_agent.md`) - Main orchestrator, creates stories
- **System Design Agent** (`RX.CE-Framework/personas/system_design_agent.md`) - Creates design docs (POC mode)
- **Story Composer** (`RX.CE-Framework/personas/story_composer_agent.md`) - Creates story files (incremental mode)
- **Frontend Agent** (`RX.CE-Framework/personas/frontend_agent.md`) - UI implementation
- **Backend Agent** (`RX.CE-Framework/personas/backend_agent.md`) - Server-side implementation
- **Code Review Agent** (`RX.CE-Framework/personas/code_review_agent.md`) - Quality validation
- **Testing Agent** (`RX.CE-Framework/personas/testing_agent.md`) - Test execution
- **QA Agent** (`RX.CE-Framework/personas/qa_agent.md`) - Final validation

**Parallel Testing Agents:**
- **Frontend Unit Testing Agent** (`RX.CE-Framework/personas/frontend_unit_testing_agent.md`) - Parallel frontend unit tests
- **Backend Unit Testing Agent** (`RX.CE-Framework/personas/backend_unit_testing_agent.md`) - Parallel backend unit tests

**Phase 2 Agents:**
- **Brownfield Architect Agent** (`RX.CE-Framework/personas/brownfield_architect_agent.md`) - Legacy codebase analysis
- **Ask Agent** (`RX.CE-Framework/personas/ask_agent.md`) - Codebase questions and analysis

## Agent Activation Pattern

When user requests: "act as Hub Agent"
Your response:
1. "I'm now acting as the Hub Agent. Let me read the agent specification..."
2. [Read `RX.CE-Framework/personas/hub_agent.md` completely]
3. [Follow the workflow defined in that file]
4. [Reference PROTOCOL.md for state transitions]

## Key Files
- `state/workflow.db` - SQLite state machine (project state tracking)
- `/stories/story-*.md` - Individual story files (work tracking)
- `/docs/[module]/index.md` - Context loading guides
- `.claude/config.yml` - Framework configuration

## Important Rules
1. Always read the complete agent file before acting
2. Follow the agent's step-by-step workflow exactly
3. Update story files according to handoff protocol
4. Clear context between stories (Context Isolation Protocol)
5. Load context based on Task Type from `docs/[module]/index.md`
EOF

# Step 3: Done!
echo "✅ Setup complete! Copilot will read this automatically."
```

### Daily Usage

**Activate an agent:**

```
You: "act as Hub Agent"

Copilot: [Reads .github/copilot-instructions.md]
         [Loads RX.CE-Framework/personas/hub_agent.md]
         "I'm the Hub Agent. What would you like to build?"

You: "create a story for CSV export"

Copilot: [Follows hub_agent.md workflow]
         [Creates story file]
         [Registers story in SQLite state machine]
```

**Switch agents:**

```
You: "act as Frontend Agent"

Copilot: [Loads frontend_agent.md]
         "I'm the Frontend Agent. Which story should I implement?"

You: "implement story-042"

Copilot: [Reads stories/story-042.md]
         [Loads context from docs/frontend/index.md]
         [Implements code following patterns]
         [Updates story file]
```

### Important Notes

- Copilot reads `.github/copilot-instructions.md` automatically on every chat
- The "act as" pattern requires explicit instructions (provided above)
- You may need to remind Copilot to read the agent file if it doesn't automatically
- Use `@AGENTS.md` or `@RX.CE-Framework/PROTOCOL.md` to reference framework docs

---

## Cursor Setup

**For Cursor IDE users**

### Understanding Cursor's Capabilities

Cursor (2025) supports:
- ✅ `.cursor/rules/*.mdc` - Modern rule format (recommended)
- ✅ `.cursorrules` - Legacy format (deprecated but still works)
- ✅ `@-mentions` - Direct file references
- ✅ `AGENTS.md` - Agent definitions (automatic)

### Setup Status: Already Complete!

**Setup files are already included in this framework.** These files are auto-loaded when you open the project in Cursor IDE.

Included files:
- `.cursor/rules/framework-agents.mdc` - Lists all 12 agents with @-mention examples

### Reference: Manual Setup Instructions (already done)

If you need to recreate the setup files, here are the reference instructions.

Open terminal in your project root:

```bash
# Step 1: Create modern rules directory
mkdir -p .cursor/rules

# Step 2: Create main rule that references your framework
cat > .cursor/rules/framework-agents.mdc << 'EOF'
---
title: Context Engineering Framework Agents
description: Agent-based development with specialized AI agents
globs: ["**/*"]
---

# Context Engineering Framework - Cursor Integration

This repository uses an agent-based development framework.

## Framework Files
- Agent definitions: `RX.CE-Framework/personas/*.md`
- Agent system: `RX.CE-Framework/AGENTS.md`
- Protocol: `RX.CE-Framework/PROTOCOL.md`
- Configuration: `.claude/config.yml`

## Using Agents with @-mentions

To activate an agent, use the @-mention pattern:

**Examples:**
```
@RX.CE-Framework/personas/hub_agent.md create a story for CSV export
@RX.CE-Framework/personas/frontend_agent.md implement story-042
@RX.CE-Framework/personas/backend_agent.md implement story-043
@RX.CE-Framework/personas/code_review_agent.md review story-042
```

## Agent Behavior

When a persona file is @-mentioned:
1. Read the complete agent file
2. Understand the role, workflow, and constraints
3. Follow the step-by-step workflow exactly
4. Reference `@RX.CE-Framework/PROTOCOL.md` for state rules
5. Update story files in `/stories/` following handoff protocol

## Available Agents

**Core Workflow Agents:**
- `hub_agent.md` - Main orchestrator
- `system_design_agent.md` - Design & architecture (POC mode)
- `story_composer_agent.md` - Story creation (incremental)
- `frontend_agent.md` - Frontend implementation
- `backend_agent.md` - Backend implementation
- `code_review_agent.md` - Code quality review
- `testing_agent.md` - Test execution
- `qa_agent.md` - Final validation

**Parallel Testing Agents:**
- `frontend_unit_testing_agent.md` - Parallel frontend unit tests
- `backend_unit_testing_agent.md` - Parallel backend unit tests

**Phase 2 Agents:**
- `brownfield_architect_agent.md` - Legacy codebase analysis
- `ask_agent.md` - Codebase questions and analysis

## Context Loading

Before implementing:
1. Read story file in `/stories/`
2. Extract Task Type from Dev Notes
3. Navigate to `docs/[module]/index.md`
4. Load only required documents for Task Type
5. Log loaded context in story file

## Key Directories
- `/stories/` - Story files (work tracking)
- `/docs/` - Documentation and context guides
- `state/workflow.db` - SQLite state machine (project state tracking)
EOF

# Step 3: Done!
echo "✅ Setup complete! Cursor reads .cursor/rules automatically."
```

### Daily Usage

**Using @-mentions (recommended):**

```
You: "@RX.CE-Framework/personas/hub_agent.md create a story for CSV export"

Cursor: [Loads hub_agent.md via @-mention]
        [Follows workflow]
        [Creates story file]
```

**Using natural language with framework rules:**

```
You: "act as Frontend Agent and implement story-042"

Cursor: [Reads .cursor/rules/framework-agents.mdc]
        [Loads RX.CE-Framework/personas/frontend_agent.md]
        [Implements code]
```

### Tips for Cursor

- **@-mentions are most reliable** - Direct file references work best
- Use `/` to see available files for @-mention
- Reference `@AGENTS.md` to show Cursor the agent system
- If Cursor forgets context, re-mention the agent file

---

## Roo Code Setup

**For terminal-first developers**

### Understanding Roo Code's Capabilities

Roo Code (2025) supports:
- ✅ `.roo/rules/*.md` - Custom mode rules
- ✅ `projectBrief.md` - Project context (root)
- ✅ `AGENTS.md` - Agent definitions (recommended)
- ✅ Shell command execution
- ✅ Direct file read/write

### Setup Status: Already Complete!

**Setup files are already included in this framework.** These files are auto-loaded when you start Roo Code in the project directory.

Included files:
- `.roo/rules/framework-agents.md` - Lists all 12 agents with activation commands
- `projectBrief.md` - Project overview with agent list

### Reference: Manual Setup Instructions (already done)

If you need to recreate the setup files, here are the reference instructions.

Open terminal in your project root:

```bash
# Step 1: Create .roo directory
mkdir -p .roo/rules

# Step 2: Create instructions that reference your framework
cat > .roo/rules/framework-agents.md << 'EOF'
# Context Engineering Framework for Roo Code

This repository uses an agent-based development framework with specialized AI agents.

## Framework Location
- Agent definitions: `RX.CE-Framework/personas/*.md`
- Agent system: `RX.CE-Framework/AGENTS.md`
- Operating protocol: `RX.CE-Framework/PROTOCOL.md`
- Configuration: `.claude/config.yml`

## How to Activate Agents

When I say "act as [Agent Name]", automatically:

1. Read `RX.CE-Framework/AGENTS.md` to understand the agent system
2. Read `RX.CE-Framework/personas/[agent-name]_agent.md` for the specific agent
3. Follow the agent's workflow exactly as defined
4. Reference `RX.CE-Framework/PROTOCOL.md` for state machine rules
5. Update story files in `/stories/` directory

## Available Agents

**Core Workflow Agents:**
- "act as Hub Agent" → `RX.CE-Framework/personas/hub_agent.md`
- "act as System Design Agent" → `RX.CE-Framework/personas/system_design_agent.md`
- "act as Story Composer" → `RX.CE-Framework/personas/story_composer_agent.md`
- "act as Frontend Agent" → `RX.CE-Framework/personas/frontend_agent.md`
- "act as Backend Agent" → `RX.CE-Framework/personas/backend_agent.md`
- "act as Code Review Agent" → `RX.CE-Framework/personas/code_review_agent.md`
- "act as Testing Agent" → `RX.CE-Framework/personas/testing_agent.md`
- "act as QA Agent" → `RX.CE-Framework/personas/qa_agent.md`

**Parallel Testing Agents:**
- "act as Frontend Unit Testing Agent" → `RX.CE-Framework/personas/frontend_unit_testing_agent.md`
- "act as Backend Unit Testing Agent" → `RX.CE-Framework/personas/backend_unit_testing_agent.md`

**Phase 2 Agents:**
- "act as Brownfield Architect Agent" → `RX.CE-Framework/personas/brownfield_architect_agent.md`
- "act as Ask Agent" → `RX.CE-Framework/personas/ask_agent.md`

## Agent Workflow

When activated as an agent:
1. Read the complete agent file from `RX.CE-Framework/personas/`
2. Announce: "I'm now acting as the [Agent Name]"
3. Follow the step-by-step workflow in the agent file
4. Reference PROTOCOL.md for state transitions
5. Update story files following the handoff protocol
6. Use direct file I/O (you can read and write files)
7. Execute shell commands when needed (tests, linters, etc.)

## Key Framework Concepts

**Story-Driven**: All work tracked in `/stories/story-*.md` files
**State Machine**: Stories progress through [Pending] → [I] → [CR] → [T] → [Q] → [Done]
**Context Loading**: Load docs from `docs/[module]/index.md` based on Task Type
**Context Isolation**: Clear context between stories (one story at a time)

## Story File Location
All stories: `/stories/story-*.md`
State tracking: `state/workflow.db` (SQLite database)

## Configuration
Framework config: `.claude/config.yml`
Edit to skip stages (code review, testing, QA) or adjust quality gates
EOF

# Step 3: Create projectBrief.md (Roo-specific convention)
cat > projectBrief.md << 'EOF'
# Context Engineering Framework

This project uses an agent-based development workflow.

## Overview
- **Framework**: Context Engineering with specialized AI agents
- **Agents**: Defined in `RX.CE-Framework/personas/`
- **Protocol**: `RX.CE-Framework/PROTOCOL.md`
- **Coordination**: `RX.CE-Framework/AGENTS.md`

## Usage
Tell Roo to "act as [Agent Name]" to activate an agent.

Example: "act as Hub Agent"

Roo will read the agent definition and follow its workflow.

## Key Directories
- `/stories/` - Work tracking (story files)
- `/docs/` - Documentation and context guides
- `RX.CE-Framework/` - Framework core files

For detailed setup, see `.roo/rules/framework-agents.md`
EOF

# Step 4: Done!
echo "✅ Setup complete! Roo will read these files automatically."
```

### Daily Usage

**Start Roo and activate an agent:**

```bash
# Start Roo in your project directory
roo
```

```
You: "read projectBrief.md"

Roo: [Reads project context]
     "I understand this is a Context Engineering Framework project
     with agent-based development."

You: "act as Hub Agent"

Roo: [Reads .roo/rules/framework-agents.md]
     [Loads RX.CE-Framework/personas/hub_agent.md]

     "I'm now acting as the Hub Agent.

     My role:
     - Orchestrate development workflow
     - Create and manage stories
     - Coordinate between agents
     - Track state and dependencies

     What would you like to build?"

You: "create a story for CSV export"

Roo: [Follows hub_agent.md workflow]
     [Creates stories/story-042.md]
     [Registers story in SQLite state machine]

     "Story-042 created: CSV Export Feature
     Status: [Pending]

     Implement now? (yes/no)"
```

**Switch agents:**

```
You: "act as Frontend Agent"

Roo: [Clears previous context]
     [Loads RX.CE-Framework/personas/frontend_agent.md]

     "I'm now acting as the Frontend Agent.
     Which story should I implement?"

You: "implement story-042"

Roo: [Reads stories/story-042.md]
     [Loads context from docs/frontend/index.md]
     [Implements code]
     [Writes files directly]
     [Updates story file]

     "Implementation complete.

     Created:
     - frontend/src/components/ExportButton.tsx
     - frontend/tests/ExportButton.test.tsx

     Updated stories/story-042.md
     Status: [I] → [CR]

     Ready for code review."
```

### Why Roo Works Well

✅ **Direct file access**: Roo can read and write files without user intervention
✅ **Shell execution**: Can run tests, linters, builds automatically
✅ **Terminal-first**: Perfect for command-line workflows
✅ **Fast iteration**: No IDE overhead
✅ **Persistent context**: Understands projectBrief.md automatically

### Tips for Roo Code

**✅ DO:**
- Start each session with "read projectBrief.md"
- Use "act as [Agent]" to switch agents
- Let Roo create and modify files directly
- Roo can execute shell commands (tests, linters, etc.)

**❌ DON'T:**
- Forget to re-activate agent if Roo loses context
- Mix multiple agents in one command
- Manually copy/paste file content (Roo can write directly)

---

## OpenAI Codex CLI Setup

**For developers who want a powerful terminal-based coding agent**

**Key Features:**
- ✅ Runs locally in your terminal (macOS, Linux, experimental Windows)
- ✅ Native AGENTS.md support (reads your framework automatically!)
- ✅ Three approval modes (from read-only to full-auto)
- ✅ Direct file I/O and shell command execution
- ✅ Works with ChatGPT Plus/Pro or API key

### One-Time Setup (2 minutes)

**Step 1: Install Codex CLI**

```bash
# Install via npm (recommended)
npm install -g @openai/codex

# Or via Homebrew (macOS only)
brew install codex
```

**Step 2: Authenticate**

First time you run Codex, you'll be prompted to authenticate:

```bash
# Start Codex (will trigger authentication)
codex

# Option 1: Sign in with ChatGPT account (recommended)
# Follow the prompts to sign in via browser

# Option 2: Use API key
export OPENAI_API_KEY="your-api-key-here"
printenv OPENAI_API_KEY | codex login --with-api-key
```

**Step 3: Create AGENTS.md (if not already exists)**

**Good news: Your framework already has AGENTS.md!** Codex will automatically read it.

```bash
# Verify AGENTS.md exists
ls RX.CE-Framework/AGENTS.md

# If it doesn't exist, create a copy at project root
cp RX.CE-Framework/AGENTS.md ./AGENTS.md
```

**Step 4: Done!**

Codex is now set up and will automatically read your framework's AGENTS.md file.

### Understanding Approval Modes

Codex CLI has three modes that control autonomy:

#### 1. **Suggest Mode** (Safest - Default)
```bash
codex --suggest
# or just: codex
```
- Requires approval for ALL file writes and shell commands
- Best for: Learning, sensitive operations, maximum control

#### 2. **Auto Edit Mode** (Balanced)
```bash
codex --auto-edit
```
- Auto-approves file edits
- Requires approval for shell commands only
- Best for: Coding tasks while retaining control over system commands

#### 3. **Full Auto Mode** (Fastest)
```bash
codex --full-auto
```
- Auto-approves everything (files + commands)
- Best for: Trusted workflows, rapid development

**Switch modes in-session:** Use `/mode` command

### Daily Usage

**Navigate to your project:**

```bash
cd /path/to/your/project
```

**Start Codex in suggest mode (recommended to start):**

```bash
codex
```

**Activate an agent:**

```
You: "Read AGENTS.md and act as Hub Agent"

Codex: [Reads RX.CE-Framework/AGENTS.md automatically]
       [Loads RX.CE-Framework/personas/hub_agent.md]

       "I'm acting as the Hub Agent. What would you like to build?"

You: "create a story for CSV export"

Codex: [Follows hub_agent.md workflow]
       [Proposes changes to create stories/story-042.md]

       "I'll create story-042.md with the following content:
       [Shows story file content]

       Approve? (y/n/edit)"

You: "y"

Codex: [Writes file]
       [Registers story in SQLite state machine]

       "Story-042 created. Status: [Pending]
       Implement now?"
```

**Switch agents:**

```
You: "Clear context and act as Frontend Agent"

Codex: [Clears previous context]
       [Loads RX.CE-Framework/personas/frontend_agent.md]

       "I'm the Frontend Agent. Which story?"

You: "implement story-042"

Codex: [Reads stories/story-042.md]
       [Reads docs/frontend/index.md]
       [Loads required context based on Task Type]
       [Proposes code changes]

       "I'll create the following files:
       - frontend/src/components/ExportButton.tsx
       - frontend/tests/ExportButton.test.tsx

       [Shows code]

       Approve? (y/n/edit)"

You: "y"

Codex: [Writes files]
       [Updates story file]

       "Implementation complete. Story-042 → [CR]"
```

### Advanced Features

**Attach images/screenshots:**
```bash
codex -i screenshot.png "Fix this error"
codex --image diagram.png "Implement this architecture"
```

**Quiet mode (for scripting):**
```bash
codex -q "create story for user login" --json
```

**Specify different model:**
```bash
codex --model gpt-5-codex "implement story-042"
```

**Disable project documentation auto-load:**
```bash
codex --no-project-doc
# or set environment variable:
export CODEX_DISABLE_PROJECT_DOC=1
```

### Configuration

Codex stores preferences in `~/.codex/config.toml`

**Personal instructions** (applied to all projects):
```bash
# Edit global instructions
nano ~/.codex/instructions.md
```

**Project-specific instructions** (Codex reads these automatically):
- `AGENTS.md` - Your framework already has this!
- `.codex/instructions.md` - Additional project-specific guidance

### Why Codex Works Well with This Framework

✅ **Native AGENTS.md support**: Automatically reads and follows your framework
✅ **Direct file I/O**: Can write files without user copy/paste
✅ **Shell execution**: Runs tests, linters, builds automatically
✅ **Approval controls**: Choose your safety level
✅ **GPT-5-Codex**: More powerful than GPT-4 for coding
✅ **Open source**: Transparent, community-driven

### Example: Full Story Workflow

```bash
# Start Codex in auto-edit mode (approves file edits automatically)
codex --auto-edit

You: "Act as Hub Agent and create a story for dark mode toggle"

Codex: [Reads AGENTS.md]
       [Follows hub_agent.md workflow]
       [Auto-creates story-043.md]
       [Registers story in SQLite state machine]
       "Story-043 created. Implement now?"

You: "Yes. Act as Frontend Agent and implement story-043"

Codex: [Switches to frontend_agent.md]
       [Reads story-043.md]
       [Loads context from docs/frontend/index.md]
       [Auto-creates component files]
       [Auto-creates test files]
       [Auto-updates story file]

       "Implementation complete. Run tests? (y/n)"

You: "y"

Codex: [Executes: npm test]
       "✓ All tests passed
       Story-043 → [CR]
       Ready for code review."

You: "Act as Code Review Agent and review story-043"

Codex: [Switches to code_review_agent.md]
       [Reviews code]
       [Runs linters (requires approval in auto-edit mode)]

       "Run ESLint? (y/n)"

You: "y"

Codex: [Executes: npm run lint]
       "✓ All checks passed
       Story-043 → [T]
       Approved for testing."
```

### Tips for Codex CLI

**✅ DO:**
- Start with suggest mode (`codex`) to learn the workflow
- Use auto-edit mode (`codex --auto-edit`) once comfortable
- Let Codex read and write files directly
- Approve shell commands carefully (especially in suggest mode)
- Use AGENTS.md (your framework already has it!)

**❌ DON'T:**
- Jump straight to full-auto mode without testing first
- Ignore approval prompts for destructive commands
- Manually copy/paste when Codex can write files
- Forget to commit changes (Codex doesn't auto-commit)

---

## Workflow Guide

### Understanding the Three Workflow Modes

The framework supports three different workflows depending on your project type:

**1. Full POC Mode (Default - New Projects)**
```
0. Design Phase    → System Design Agent creates architecture docs
1. HITL Gate 1     → Human approves design documents
2. Story Creation  → Hub Agent decomposes design into stories
3. Implementation  → Frontend/Backend Agents
4. Code Review     → Code Review Agent
5. Testing         → Testing Agent
6. QA              → QA Agent
7. HITL Gate 2     → Human final approval
8. Done            → Ship it!
```

**2. Incremental Mode (`/story` command - Existing Projects)**
```
1. Story Creation  → Story Composer Agent
2. Implementation  → Frontend/Backend Agents
3. Code Review     → Code Review Agent
4. Testing         → Testing Agent
5. QA              → QA Agent
6. Done            → Ship it!
```

**3. Brownfield Mode (`/refactor` command - Legacy Codebases)**
```
0. Analysis Phase  → Brownfield Architect analyzes existing code
1. HITL Gate       → Human approves refactoring plan
2. Story Creation  → Hub Agent creates refactoring stories
3. Implementation  → Frontend/Backend Agents
4. Code Review     → Code Review Agent
5. Testing         → Testing Agent
6. QA              → QA Agent
7. Done            → Ship it!
```

---

### Phase 0: Design & Architecture (Full POC Mode Only)

**For new projects**, start with the System Design Agent:

**All Platforms:**
```
"act as System Design Agent"
"Create a complete design for a stock trading dashboard with real-time charts"
```

**Agent will:**
- Create `docs/spec.md` (functional specifications)
- Create `docs/architecture.md` (system architecture)
- Create `docs/design.md` (high-level design)
- Create `docs/frontend.md` (frontend implementation plan)
- Create `docs/backend.md` (backend implementation plan)
- Create `docs/coding-standards.md` (quality standards)
- Set all files to `[PENDING_APPROVAL]` status

**Human Action Required:**
- Review all design documents
- Change status from `[PENDING_APPROVAL]` to `[APPROVED]` in each file
- Hub Agent will then shard documents and create stories

**Then proceed to Phase 1** (Hub Agent creates stories from approved design)

---

### Phase 1: Story Creation

**For Incremental Mode (`/story` command) or after design approval:**

**All Platforms:**
```
"act as Hub Agent"
"create a story for CSV export"
```

**Cursor (alternative):**
```
@RX.CE-Framework/personas/hub_agent.md create a story for CSV export
```

**Agent will:**
- Create story file in `/stories/`
- Register story in SQLite state machine
- Set status to `[Pending]`
- Ask: "Implement now?"

### Phase 2: Implementation

**Update story status to `[I]` first**, then:

**All Platforms:**
```
"act as Frontend Agent"
"implement story-042"
```

**Cursor (alternative):**
```
@RX.CE-Framework/personas/frontend_agent.md implement story-042
```

**Agent will:**
- Read story file
- Load context from `docs/[module]/index.md`
- Implement code and tests
- Update story to `[CR]`

### Phase 3: Code Review

**All Platforms:**
```
"act as Code Review Agent"
"review story-042"
```

**Agent will:**
- Review code quality
- Check coding standards
- Run linters
- Update story to `[T]` or back to `[I]`

### Phase 4: Testing

**All Platforms:**
```
"act as Testing Agent"
"test story-042"
```

**Agent will:**
- Create integration tests
- Run test suite
- Update story to `[Q]`

### Phase 5: QA

**All Platforms:**
```
"act as QA Agent"
"validate story-042"
```

**Agent will:**
- Validate acceptance criteria
- Check for regressions
- Update story to `[Done]`

---

## Complete Example

### End-to-End Story Implementation

This example uses **Roo Code**, but the flow is identical for all platforms.

```
═══════════════════════════════════════════════════════
PHASE 1: Story Creation
═══════════════════════════════════════════════════════

$ roo

You: "read projectBrief.md"

Roo: "I understand this repository uses agent-based development."

You: "act as Hub Agent"

Roo: [Loads RX.CE-Framework/personas/hub_agent.md]
     "I'm the Hub Agent. What would you like to build?"

You: "create a story for dark mode toggle in settings"

Roo: [Follows hub_agent.md workflow]

     "Creating story for dark mode toggle...

     Analyzing codebase:
     - React + TypeScript
     - Redux Toolkit
     - Tailwind CSS

     ═══════════════════════════════════════════
     # Story 043: Dark Mode Toggle

     **Status**: [Pending]
     **Task Type**: Component Development
     **Module**: Frontend

     ## Story
     As a user, I want to toggle dark mode
     so I can customize appearance

     ## Acceptance Criteria
     - [ ] Toggle in settings page
     - [ ] Persists across sessions
     - [ ] All components respect theme
     - [ ] Smooth transitions

     ## Tasks
     - [ ] Create ThemeToggle component [FE]
     - [ ] Add theme Redux slice [FE]
     - [ ] Apply theme globally [FE]
     - [ ] Persist to localStorage [FE]
     - [ ] Unit tests [FE]
     ═══════════════════════════════════════════

     Created: stories/story-043.md
     Registered: SQLite state machine

     Implement now? (yes/no)"

You: "yes"

Roo: [Updates stories/story-043.md]
     "Status updated to [I]
     Ready for Frontend Agent."

═══════════════════════════════════════════════════════
PHASE 2: Implementation
═══════════════════════════════════════════════════════

You: "act as Frontend Agent"

Roo: [Loads RX.CE-Framework/personas/frontend_agent.md]
     "I'm the Frontend Agent. Which story?"

You: "implement story-043"

Roo: [Reads stories/story-043.md]
     [Loads context from docs/frontend/index.md]

     "Loading context for Component Development:
     - component-hierarchy.md ✓
     - state-management-strategy.md ✓
     - styling-guidelines.md ✓

     Implementing...

     Created:
     - src/components/Settings/ThemeToggle.tsx
     - src/store/slices/themeSlice.ts
     - src/tests/ThemeToggle.test.tsx

     [Files created in your project]

     Updated stories/story-043.md:
     - Added context log
     - Added implementation notes
     - Status: [I] → [CR]

     Ready for code review."

═══════════════════════════════════════════════════════
PHASE 3: Code Review
═══════════════════════════════════════════════════════

You: "act as Code Review Agent"

Roo: [Loads RX.CE-Framework/personas/code_review_agent.md]
     "I'm the Code Review Agent. Which story?"

You: "review story-043"

Roo: [Reads updated stories/story-043.md]
     [Reviews code files]

     "Reviewing against standards...

     ✓ Code quality: Excellent
     ✓ TypeScript: Proper types
     ✓ Documentation: JSDoc present
     ✓ Standards: All checks passed

     Linters:
     ✓ ESLint: PASSED
     ✓ TypeScript: PASSED

     Updated stories/story-043.md:
     - Added review feedback
     - Status: [CR] → [T]

     Approved for testing."

═══════════════════════════════════════════════════════
PHASE 4: Testing
═══════════════════════════════════════════════════════

You: "act as Testing Agent"

Roo: [Loads RX.CE-Framework/personas/testing_agent.md]
     "I'm the Testing Agent. Which story?"

You: "test story-043"

Roo: [Creates integration tests]
     [Runs test suite]

     "Created: src/tests/ThemeToggle.integration.test.tsx

     Running tests...
     ✓ Unit tests: 5/5 passed
     ✓ Integration: 2/2 passed
     ✓ Coverage: 94%

     Updated stories/story-043.md:
     - Added test results
     - Status: [T] → [Q]

     Ready for QA."

═══════════════════════════════════════════════════════
PHASE 5: QA
═══════════════════════════════════════════════════════

You: "act as QA Agent"

Roo: [Loads RX.CE-Framework/personas/qa_agent.md]
     "I'm the QA Agent. Which story?"

You: "validate story-043"

Roo: [Validates acceptance criteria]

     "Validating acceptance criteria:
     ✓ Toggle in settings page
     ✓ Persists across sessions
     ✓ All components respect theme
     ✓ Smooth transitions

     Regression check:
     ✓ No regressions detected

     Updated stories/story-043.md:
     - Added QA approval
     - Status: [Q] → [Done]

     ✅ Story-043 complete and production-ready!"

═══════════════════════════════════════════════════════
DONE!
═══════════════════════════════════════════════════════
```

---

## Troubleshooting

### Problem: Agent doesn't load

**All Platforms:**
```
Solution: Be explicit in your request

✅ Good: "act as Hub Agent - read RX.CE-Framework/personas/hub_agent.md and follow its workflow"
❌ Weak: "be the hub agent"

If needed, reference the file directly:
- Copilot: "Read RX.CE-Framework/personas/hub_agent.md and act as that agent"
- Cursor: "@RX.CE-Framework/personas/hub_agent.md"
- Roo: "Read RX.CE-Framework/personas/hub_agent.md and follow it exactly"
```

---

### Problem: Agent skips context loading

**All platforms:**
```
Say explicitly:
"Before implementing, you MUST:
1. Read the story file completely
2. Read docs/[module]/index.md
3. Find the Task Type section
4. Load all required documents for that Task Type
5. Confirm what you loaded by updating the story file
Then implement following those patterns."
```

---

### Problem: Agent doesn't update story files

**Copilot/Cursor:**
```
These tools show you the content but don't write files automatically.
You need to copy the updated content and paste it into the file.

Workflow:
[Agent output] → [Copy] → [Paste to editor] → [Save]
```

**Roo Code:**
```
Roo can write files directly!
Say: "Update the story file directly at stories/story-042.md"
```

---

### Problem: Agent forgets context mid-conversation

**All platforms:**
```
Solution: Re-mention the agent file

"You're acting as Frontend Agent - read RX.CE-Framework/personas/frontend_agent.md again to refresh your instructions"

Or restart with a fresh agent activation.
```

---

### Problem: "act as" pattern not working

**GitHub Copilot:**
```
Check that .github/copilot-instructions.md exists and includes the agent activation pattern.

If Copilot doesn't respond to "act as", try:
"Load the Hub Agent persona from RX.CE-Framework/personas/hub_agent.md and follow its workflow"
```

**Cursor:**
```
Use @-mentions instead of "act as":
@RX.CE-Framework/personas/hub_agent.md create a story
```

**Roo Code:**
```
Ensure projectBrief.md and .roo/rules/framework-agents.md exist.
Start each session with: "read projectBrief.md"
```

**OpenAI Codex:**
```
Ensure AGENTS.md exists at project root or RX.CE-Framework/
If Codex doesn't respond to "act as", try:
"Read RX.CE-Framework/personas/hub_agent.md and follow that agent's workflow exactly"
```

---

### Problem: Too much manual work

**Time per story (estimated):**
- Codex CLI: ~15-25 minutes (depends on approval mode)
- Cursor: ~25-30 minutes
- Copilot: ~30-40 minutes
- Roo Code: ~20-30 minutes
- Claude Code: ~10-15 minutes (fully automated)

**If spending >45 minutes per story:**
→ Consider Claude Code for production work (native automation)

**Your options:**
1. **Keep current tool** - Good for learning and small projects
2. **Optimize workflow** - Use AGENTS.md, write better prompts
3. **Switch to Claude Code** - Full automation, zero manual intervention

---

## Quick Reference

### Agent Activation Commands

**Universal (all platforms) - 12 Agents Total:**

**Core Workflow Agents (8):**
```
"act as Hub Agent"                    (Orchestrates workflow, creates stories)
"act as System Design Agent"          (Full POC mode - creates design docs)
"act as Story Composer"               (Incremental mode - creates stories)
"act as Frontend Agent"               (Implements frontend code)
"act as Backend Agent"                (Implements backend code)
"act as Code Review Agent"            (Reviews code quality)
"act as Testing Agent"                (Runs integration tests)
"act as QA Agent"                     (Final validation)
```

**Parallel Testing Agents (2):**
```
"act as Frontend Unit Testing Agent"  (Parallel frontend unit tests)
"act as Backend Unit Testing Agent"   (Parallel backend unit tests)
```

**Note:** Frontend/Backend Unit Testing Agents are not manually invoked - they are auto-triggered at [CR] stage.

**Phase 2 Agents (2):**
```
"act as Brownfield Architect Agent"   (Legacy codebase analysis & refactoring)
"act as Ask Agent"                    (Framework Q&A, read-only diagnostics)
```

**Cursor (@-mention pattern) - 12 Agents Total:**

**Core Workflow Agents (8):**
```
@RX.CE-Framework/personas/hub_agent.md
@RX.CE-Framework/personas/system_design_agent.md
@RX.CE-Framework/personas/story_composer_agent.md
@RX.CE-Framework/personas/frontend_agent.md
@RX.CE-Framework/personas/backend_agent.md
@RX.CE-Framework/personas/code_review_agent.md
@RX.CE-Framework/personas/testing_agent.md
@RX.CE-Framework/personas/qa_agent.md
```

**Parallel Testing Agents (2):**
```
@RX.CE-Framework/personas/frontend_unit_testing_agent.md
@RX.CE-Framework/personas/backend_unit_testing_agent.md
```

**Note:** Unit testing agents are triggered automatically at [CR], not manually invoked.

**Phase 2 Agents (2):**
```
@RX.CE-Framework/personas/brownfield_architect_agent.md
@RX.CE-Framework/personas/ask_agent.md
```

**Reference the protocol:**
```
@RX.CE-Framework/PROTOCOL.md - State machine rules
@RX.CE-Framework/AGENTS.md - Agent coordination
@.claude/config.yml - Framework configuration
```

---

### Essential Framework Files

```
RX.CE-Framework/
├── PROTOCOL.md              ← State machine and rules
├── AGENTS.md                ← Agent coordination (2025 standard, lists all 12 agents)
├── personas/                ← 12 specialized agents
│   ├── hub_agent.md                      ← 1. Main orchestrator
│   ├── system_design_agent.md            ← 2. Design & architecture (POC mode)
│   ├── story_composer_agent.md           ← 3. Story creation (incremental)
│   ├── frontend_agent.md                 ← 4. Frontend implementation
│   ├── backend_agent.md                  ← 5. Backend implementation
│   ├── code_review_agent.md              ← 6. Code quality
│   ├── testing_agent.md                  ← 7. Test execution
│   ├── qa_agent.md                       ← 8. Final validation
│   ├── frontend_unit_testing_agent.md    ← 9. Parallel frontend unit tests (auto)
│   ├── backend_unit_testing_agent.md     ← 10. Parallel backend unit tests (auto)
│   ├── brownfield_architect_agent.md     ← 11. Legacy codebase analysis
│   └── ask_agent.md                      ← 12. Framework Q&A (read-only)
└── config.yml               ← Framework configuration

state/workflow.db            ← SQLite state machine (story tracking)
/stories/story-*.md          ← Individual stories
/docs/[module]/index.md      ← Context guides (after design approval)
```

---

### Platform-Specific Setup Files

**All files included in this repository (zero-setup experience):**

```
# GitHub Copilot (auto-loaded)
.github/copilot-instructions.md        ← Lists all 12 agents

# Cursor (auto-loaded)
.cursor/rules/framework-agents.mdc     ← Lists all 12 agents with @-mentions

# Roo Code (auto-loaded)
.roo/rules/framework-agents.md         ← Lists all 12 agents
projectBrief.md                        ← Project overview with numbered agent list

# OpenAI Codex CLI (auto-detected)
AGENTS.md → RX.CE-Framework/AGENTS.md (symlink or copy)
~/.codex/instructions.md (optional global config)

# Universal (works with all platforms)
RX.CE-Framework/AGENTS.md            ← Master list of 12 agents
```

---

**Questions?** Check [UNDERSTANDING_CONTEXT_ENGINEERING.md](UNDERSTANDING_CONTEXT_ENGINEERING.md) for core concepts.
