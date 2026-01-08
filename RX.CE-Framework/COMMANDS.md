# Command Reference

Quick guide for interacting with the RX.CE-Framework.

---

## Primary Commands

### /greenfield

Full POC development from scratch with design phase.
- Loads Hub Agent in greenfield mode
- Creates design docs → HITL → sharding → stories
- See: `.claude/commands/greenfield.md`

### /story

Add features to existing codebase (incremental development).
- Loads Hub Agent in incremental mode
- Uses brownfield analysis to understand patterns
- Creates feature stories following existing conventions
- See: `.claude/commands/story.md`

### /refactor

Modernize legacy code with risk-managed refactoring.
- Loads Hub Agent in refactor mode
- Analyzes technical debt → plan → HITL → sharding → stories
- Phased execution with risk levels
- See: `.claude/commands/refactor.md`

### /ask

Get help and answers about the framework (read-only).
- Loads Ask Agent
- No modifications or workflow triggers
- See: `.claude/commands/ask.md`

## Deprecated Commands

### /hub (deprecated)

Use `/greenfield` instead.
- /hub still works but redirects to greenfield mode
- Will be removed in future version

---

## Commands Detail

### /greenfield - Full POC Development

**What it does**: Runs the complete POC workflow with full design phase.

**Syntax**: Just describe what you want to build

**Use when**:
- Starting a new project from scratch
- Need comprehensive design documentation
- Want structured approval gates
- Building a complete application

**Example**:
```
User: "Create a stock trading dashboard with real-time charts"

→ System Design Agent creates all design docs
→ HITL Gate 1: Human approves design
→ Hub creates stories from design
→ Implementation proceeds automatically
→ Testing and QA validation
→ HITL Gate 2: Final approval
```

**What happens**:
1. System Design Agent creates: `spec.md`, `architecture.md`, `design.md`, `frontend.md`, `backend.md`
2. Documents are automatically sharded into subdirectories
3. Human approves design (HITL Gate 1)
4. Hub creates stories from design documents
5. Full implementation workflow runs
6. Final human sign-off (HITL Gate 2)

---

### /story - Create Story Files

**What it does**: Analyzes existing codebase, then creates story file(s) that integrate with your current architecture.

**Syntax**: `/story [description of what you want]`

**Use when**:
- Adding features to existing codebase
- Bug fixes or enhancements
- You already have design patterns established
- Want to plan before implementing
- Quick iterations on existing project

**Examples**:
```
/story add CSV export button to dashboard
/story fix date picker bug in reports page
/story implement dark mode toggle
/story add user authentication with login and signup
```

**What happens**:

**First time using `/story` on a codebase**:
1. Hub checks for brownfield analysis (doesn't exist yet)
2. Brownfield Architect runs analysis-only mode (~4 min one-time cost):
   - Installs Flatty (if needed)
   - Flattens codebase to `analysis/flattened-codebase.md`
   - Analyzes architecture and patterns
   - Generates `analysis/brownfield-architecture.md`
3. Story Composer creates story file(s) using brownfield analysis
4. Stories registered in SQLite state machine with `[Pending]` status
5. Hub asks: **"Implement now? (yes/no)"**

**Subsequent uses (analysis exists)**:
1. Hub finds existing analysis
2. Hub asks: **"Use existing analysis? (yes/no)"**
   - If **yes**: Creates stories instantly (fast)
   - If **no**: Regenerates analysis (~4 min), then creates stories
3. Story Composer creates story file(s) using analysis
4. Hub asks: **"Implement now? (yes/no)"**

**If you respond "yes"**:
- Story status updates to `[I]`
- Implementation workflow begins (same as full POC)
- Follows existing protocol: Implementation → Code Review → Testing → QA → Done

**If you respond "no"**:
- Story stays at `[Pending]`
- You can review/edit the story file
- Later, Hub will prompt: "You have pending stories. Implement? (yes/no/select)"

**When to regenerate analysis**:
- Major refactoring since last analysis
- New modules or services added
- Architectural changes
- You're unsure (better safe than sorry)

**Analysis is cached**: Once generated, analysis is reused for speed unless you choose to regenerate.

---

### /refactor - Analyze Code & Create Refactoring Plans

**What it does**: Analyzes existing codebase, identifies technical debt, and creates a phased refactoring plan with risk assessments.

**Syntax**: `/refactor [scope or module description]`

**Use when**:
- Analyzing technical debt in existing code
- Planning modernization of legacy patterns
- Extracting shared utilities from duplicated code
- Improving code quality and maintainability
- Consolidating duplicated logic
- Optimizing performance bottlenecks
- Preparing for major architectural changes

**Examples**:
```
/refactor modernize authentication module
/refactor extract shared utilities
/refactor improve error handling in controllers
/refactor assess technical debt in backend
/refactor analyze entire codebase
```

**What happens**:
1. Brownfield Architect Agent activates
2. Auto-installs Flatty (if not present)
3. Flattens codebase into `analysis/flattened-codebase.md`
4. Analyzes code patterns, technical debt, code smells
5. Creates `analysis/brownfield-architecture.md` (detailed analysis)
6. Creates `analysis/refactoring-plan.md` (phased strategy)
7. Auto-shards documents if >500 lines (installs md-tree if needed)
8. Generates refactoring story files
9. Story state is automatically tracked in SQLite database
10. Hub presents plan for **human approval** (HITL Gate)

**Human Approval Gate**:
You must approve the refactoring plan before any implementation begins.

**To approve**: Open `analysis/refactoring-plan.md` and change:
```markdown
**Status**: [PENDING_APPROVAL]
```
to:
```markdown
**Status**: [APPROVED]
```

**To reject** (request revisions):
```markdown
**Status**: [REJECTED]

**Feedback**:
- Break Phase 2 into smaller stories
- Add more detail to rollback procedures
```

**After approval**:
- Refactoring stories move from `[Pending]` to ready for implementation
- Follow existing workflow: `[I]` → `[CR]` → `[T]` → `[Q]` → `[Done]`

**Zero setup required**: All tools (Flatty, md-tree) auto-install on first use.

---

## Interactive Prompts

After using `/story`, the Hub Agent will guide you through these prompts:

### Single Story Created
```
Hub: "✓ Created story-042.md: Add CSV Export Feature

     Implement now? (yes/no)"
```

**Responses**:
- `yes` - Start implementation immediately
- `no` or `later` - Keep story pending for later

---

### Multiple Stories Created
```
Hub: "✓ Created 3 stories:
     - story-043: Login Page
     - story-044: Signup Flow
     - story-045: Password Reset

     Implement now? (yes/no/select)"
```

**Responses**:
- `yes` - Implement all stories (respecting dependencies)
- `no` or `later` - Keep all stories pending
- `select` - Choose specific stories to implement

---

### Selecting Specific Stories
```
Hub: "Which stories would you like to implement?
     Enter story numbers (e.g., 043, 045):"
```

**Response example**:
```
User: "043, 045"
Hub: "Implementing stories 043 and 045..."
```

---

### Multiple Pending Stories (Hub reminds you)
```
Hub: "You have 3 pending stories:
     - story-042: CSV Export
     - story-043: PDF Export
     - story-044: Email Reports

     Implement all? (yes/no/select)"
```

---

## Common Workflows

### Workflow 1: Quick Feature Addition
```bash
User: "/story add CSV export button"

Hub: "ℹ️  No brownfield analysis found, running first-time analysis...
     [1/3] Installing Flatty... ✅
     [2/3] Flattening codebase... ✅ (2m 15s)
     [3/3] Generating architecture doc... ✅ (1m 30s)

     ✅ Analysis complete (~4 min total)
     ✅ Cached for future /story commands
     ✅ Created story-042.md: CSV Export Button
        - Integrates with existing ExportService
        - Follows established download pattern

     Implement now?"
User: "yes"
Hub: "Starting implementation..."
[Full automated workflow proceeds]
```

**Second use (with cached analysis)**:
```bash
User: "/story add PDF export button"

Hub: "📋 Existing brownfield analysis found: analysis/brownfield-architecture.md

     Use existing analysis? (yes/no)
       • yes - Create stories now (fast)
       • no  - Regenerate analysis first (~4 min)"

User: "yes"

Hub: "✅ Using existing analysis
     ✅ Created story-043.md: PDF Export Button
        - Mirrors CSV export pattern (story-042)
        - Uses same ExportService interface

     Implement now?"
```

---

### Workflow 2: Plan Multiple Features
```
User: "/story add CSV export"
Hub: "✓ Created story-042.md. Implement now?"
User: "no"

User: "/story add PDF export"
Hub: "✓ Created story-043.md. Implement now?"
User: "no"

User: "/story add email reports"
Hub: "✓ Created story-044.md
     You have 3 pending stories. Implement all?"
User: "select"
Hub: "Which stories? (042, 043, 044)"
User: "042, 044"
Hub: "Implementing stories 042 and 044..."
```

---

### Workflow 3: Complex Feature (Multiple Stories)
```
User: "/story add user authentication with login, signup, and password reset"

Hub: "✓ Created 3 stories:
     - story-043: Login Page & API [Pending]
     - story-044: Signup Flow [Pending] (depends on 043)
     - story-045: Password Reset [Pending] (depends on 043)

     Implement now?"
User: "yes"
Hub: "Implementing in dependency order:
     Starting with story-043..."
```

---

### Workflow 4: Refactor Existing Code
```bash
User: "/refactor extract shared authentication logic"

Hub: "Brownfield Mode activated.
     Triggering Brownfield Architect Agent (full refactoring mode)..."

Brownfield Architect: "🔧 Mode: Full Refactoring
                       Installing Flatty... ✅
                       Flattening codebase... ✅ (2m 15s)
                       Analyzing architecture... ✅ (1m 30s)
                       Identifying refactoring opportunities... ✅ (1m 45s)
                       Generating phased plan... ✅ (1m 15s)
                       Creating refactoring stories... ✅ (0m 45s)

                       ✅ Identified 3 controllers with duplicated auth logic
                       ✅ Detected 100 LOC of duplication
                       ✅ Created refactoring plan with 3 stories

                       Refactoring plan ready for review (~7 min total)"

Hub: "📋 Please review and approve refactoring plan
     File: analysis/refactoring-plan.md

     Summary:
     - Phase 1 (Weeks 1-2): 3 stories, Low risk
     - Expected outcome: Reduce duplication by 60%

     Approve and implement? (yes/no)"

[User reviews and approves plan]

Hub: "✅ Refactoring plan approved
     Ready to implement:
     - story-042: Extract Auth Service [Pending]

     Begin implementation? (yes/no)"

User: "yes"
Hub: "Starting implementation of story-042..."
[Full automated workflow proceeds]
```

---

### Workflow 5: New Project (Default)
```
User: "Create a stock trading dashboard with real-time charts and user portfolios"

Hub: "Starting Full POC Mode...
     Triggering System Design Agent..."
[Full design phase proceeds]
```

---

## Understanding Brownfield Architect Modes

Both `/story` and `/refactor` use the Brownfield Architect Agent, but in different modes:

| Aspect | `/story` (Analysis Mode) | `/refactor` (Refactor Mode) |
|--------|-------------------------|----------------------------|
| **Mode** | analysis-only | full-refactoring |
| **Purpose** | Get context for features | Plan tech debt reduction |
| **Outputs** | • flattened-codebase.md<br>• brownfield-architecture.md | • flattened-codebase.md<br>• brownfield-architecture.md<br>• refactoring-plan.md<br>• Story files |
| **Stops at** | Step 6 | Step 11 |
| **Duration** | ~4 minutes | ~7 minutes |
| **Human Approval** | Not required | Required |
| **Next Step** | Story Composer creates feature stories | Human reviews refactoring plan |
| **Use When** | Adding new features | Improving existing code quality |

**Key Difference:** `/story` only generates architectural context for feature development (faster), while `/refactor` generates complete improvement plans with phased stories (comprehensive).

**Why Two Modes?**
- Saves ~3 minutes per `/story` call (no unnecessary refactoring plan)
- Keeps artifacts focused on actual use case
- Analysis mode provides exactly what Story Composer needs, nothing more

---

## Tips

- **Default is safe**: No command = full design and documentation
- **Use `/story` for existing codebases**: Always includes brownfield analysis first
- **Use `/refactor` for tech debt**: Analyze existing code and plan improvements
- **First `/story` takes ~4 min**: One-time brownfield analysis (analysis mode)
- **First `/refactor` takes ~7 min**: Full analysis + refactoring plan (refactor mode)
- **Subsequent `/story` calls are instant**: Analysis is cached (if you say yes to reuse)
- **When unsure about analysis age**: Say "no" to regenerate - better safe than sorry
- **Natural responses**: Hub understands "yes", "no", "later", story numbers
- **Dependencies handled**: Hub implements stories in correct order
- **Review before building**: Say "no" to review story files first
- **Multiple stories**: Story Composer creates multiple files for complex features
- **Two modes, one agent**: Brownfield Architect adapts to /story (fast) or /refactor (comprehensive)

---

## What Happens After Implementation Starts

Once you say "yes" to implementation, the existing automated workflow takes over:

1. **[I] In Progress**: Implementation agent builds the feature
2. **[CR] Code Review**: Code review + unit tests run in parallel
3. **[T] Testing**: Integration and E2E tests execute
4. **[Q] QA**: Final validation by QA agent
5. **[Done]**: Story complete

This is the same workflow whether you used `/story` or the default full POC mode.

---

## Getting Help

- Not sure which command to use? → Use default (no command) for safety
- Want to add small feature? → Use `/story`
- Building new app? → Use default (no command)
- Have questions? → Ask the Hub Agent directly
