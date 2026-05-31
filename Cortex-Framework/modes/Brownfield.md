# Brownfield Mode (Incremental and Refactor)

## 1. Overview
Brownfield handles existing codebases. It provides two workflows tailored for ongoing systems:
- Incremental Development Mode: add features using the `/story` command
- Refactor Mode: perform comprehensive refactoring using the `/refactor` command

Trigger: `mode=brownfield` is set by the Hub Agent or implicitly via `/story` and `/refactor` command routing.
Brownfield requires an initial analysis of the current codebase to create shared context for agents and stories. Strict context isolation, artifact registration, and the orchestrated build–review–test–QA cycle with Human‑in‑the‑Loop (HITL) gates apply universally (see AGENTS and PROTOCOL).

## 2. Context Sources (Brownfield)
Approved inputs loaded by agents when `mode=brownfield`:
- Analysis artifacts: `analysis/flattened-codebase.md`, `analysis/brownfield-architecture.md`, `analysis/refactoring-plan.md` (refactor mode)
- Sharded analysis documents (if present): `analysis/**` via local index files
- Project state: SQLite database (`state/workflow.db`) and story files (`stories/`)
- Test artifacts: unit/integration/E2E suites and reports
- Coding standards: `docs/coding-standards.md` (MUST exist; implementation and review agents enforce it)

Agents must not load greenfield-specific monolithic or sharded design documents when mode=brownfield.

### 2.1 Analysis Prerequisites & Outputs
On first use (or when analysis is missing), the Brownfield Architect runs analysis-only mode and generates:
- analysis/flattened-codebase.md — auto-generated snapshot of the codebase structure
- analysis/brownfield-architecture.md — technical debt and architecture assessment
- analysis/refactoring-plan.md — phased strategy with risk levels (in refactor mode)

These artifacts form the canonical brownfield context. They may be sharded under `analysis/` when size thresholds are exceeded; shards MUST have index files for safe context loading.

## 3. Key Activities
- Discovery — Validate scope/constraints; enforce brownfield isolation from greenfield docs.
- Analysis — Produce brownfield architecture assessment and (if applicable) refactoring plan.
- Planning — Decompose analysis into incremental feature stories or refactor stories; update task board and statuses.
- Implementation — Build, review, and test features/refactors according to standards and story flow.
- Approval — HITL approval for refactor plan; finalize QA and produce sign-off proofpoint.

## 4. End-to-End Workflow
4.1 Incremental (`/story`) and 4.2 Refactor (`/refactor`) workflows share the same implementation execution once stories enter `[I]`; differences lie in analysis and approval steps.

### 4.1 Incremental Development Mode (/story)
Users can add features to existing codebases using the `/story` command without going through the full design phase.

Workflow:
1) Story Creation — User provides `/story [request]`
2) Analysis Load — Story Composer Agent loads `analysis/brownfield-architecture.md` first (required)
3) Targeted Analysis — Story Composer:
   - Analyzes the user request
   - Scans the existing codebase for patterns
   - Reviews previous stories for consistency
   - Determines the appropriate Task Type
4) Story Generation — Creates story file(s) with:
   - Canonical schema from PROTOCOL templates
   - Task Type from the standard list
   - References to existing code patterns
   - Initial status `[Pending]`
5) User Decision — Hub prompts: "Implement now? (yes/no/select)"
6) Implementation (if yes) — Follow the shared workflow from `[I]` → `[Done]`
7) Final QA — QA Agent validates against Acceptance Criteria and regression suite
8) Project Sign‑Off — Hub confirms all tasks `[Done]`, creates `brownfield-proofpoint.md`, awaits final approval

### 4.2 Refactor (`/refactor`)

**End-to-End Workflow:**

1) **Initiation**
   - User provides `/refactor [scope]`
   - Hub triggers Brownfield Architect in refactor mode

2) **Analysis Phase** (Steps 1-6 of Brownfield Architect)
   - Flatten codebase → `analysis/flattened-codebase.md`
   - Analyze architecture → `analysis/brownfield-architecture.md`
   - Identify technical debt and refactoring opportunities

3) **Planning Phase** (Steps 7-10 of Brownfield Architect)
   - Create phased refactoring plan → `analysis/refactoring-plan.md`
   - Generate refactoring stories with risk levels (LOW/MEDIUM/HIGH)
   - Stories created in `stories/` directory with `[Pending]` status

4) **HITL Gate 1 - Plan Approval** (Step 11)
   - Hub writes `Status: [PENDING_APPROVAL]` header on refactoring-plan.md
   - Human reviews monolithic documents (easier to read than shards)
   - Human changes status to `[APPROVED]` or `[REJECTED]`
   - **CRITICAL**: No sharding occurs until plan is `[APPROVED]`

5) **Post-Approval Sharding** (Steps 12-16, ONLY after HITL approval)
   - Install md-tree parser if needed
   - Shard large documents (>500 lines):
     - `analysis/brownfield-architecture.md` → `analysis/architecture/`
     - `analysis/refactoring-plan.md` → `analysis/refactoring/`
   - Enhance index files with Task Type loading guides
   - Create `analysis/shard-index.md` registry

6) **Implementation**
   - Stories flow through universal state machine: `[Pending] → [I] → [CR] → [T] → [Q] → [Done]`
   - Agents load context via `analysis/shard-index.md`
   - Phased execution: LOW risk → MEDIUM risk → HIGH risk

7) **Final QA**
   - QA Agent validates with regression suite

8) **HITL Gate 2 - Final Sign-Off**
   - Hub creates `brownfield-proofpoint.md` with `Status: [PENDING_APPROVAL]`
   - Human final approval required

**Why HITL Before Sharding:**
- Humans review MONOLITHIC documents (easier to read, full context)
- Sharding is an OPTIMIZATION for agents (3-5 docs vs 50k+ lines)
- If plan rejected, no wasted sharding effort
- Mirrors greenfield workflow for consistency

## 5. Implementation Execution Model

### 5.1 Shared Implementation Workflow
Universal story execution once implementation begins:

[Pending] → [I] → [CR] → [T] → [Q] → [Done]
           ↑               ↑
    Implementation    Parallel Execution
    (Frontend/       (Code Review +
     Backend)         Unit Tests)

### 5.2 Parallelism in Brownfield Workflows

The framework supports TWO distinct types of parallelism:

#### 5.2.1 Within-Story Parallelism (Lane-Based at [CR] Phase)

When a story transitions to `[CR]` status, three agents execute simultaneously:

```
[I] Implementation Complete
    ↓
[CR] Code Review Stage (PARALLEL LANES)
    ├─→ Code Review Agent (quality, standards, linters)
    ├─→ Frontend Unit Testing Agent (if frontend changes)
    └─→ Backend Unit Testing Agent (if backend changes)
    ↓ (Hub waits for ALL lanes)
[T] Integration Testing (if all pass)
```

**Characteristics**:
- **Always Active**: Automatically triggered at [CR] phase
- **Scope**: Within single story boundary
- **Wait Strategy**: Hub blocks until ALL three lanes complete
- **Database**: Tracked via `story_lanes` table with `lane_name` column
- **Applies To**: Both incremental (`/story`) and refactor (`/refactor`) modes

**Purpose**: Fast feedback - get quality, frontend tests, and backend tests results simultaneously instead of sequentially.

#### 5.2.2 Cross-Story Parallelism (Dependency-Based Scheduling)

Multiple stories can execute in parallel when dependencies allow:

```
story-045 (Login API)    [I] → [CR] → [T] → [Q] → [Done]
story-046 (Signup Flow)  [Pending] ────────────────────→ [I] (blocked by 045)
story-047 (User Profile) [I] → [CR] → [T] → [Q] → [Done] (parallel to 045)
```

**Characteristics**:
- **Conditional**: Only if dependencies satisfied or absent
- **Scope**: Across multiple stories
- **Wait Strategy**: Stories blocked until dependencies reach [Done]
- **Database**: Tracked via `story_dependencies` table
- **Detection**: Determined by Story Composer during creation

**Dependency Types**:
1. **Explicit**: User-specified sequence ("then", "after")
2. **Same Module**: Stories modify same component (prefer sequential)
3. **Different Module**: Cross-module dependencies (allow parallel if independent)

**Scheduling Rules** (see PROTOCOL.md Section 9.1):
- Tier 1 (Explicit): Always sequential
- Tier 2 (Same Module): Sequential unless proven safe
- Tier 3 (Different Module): Parallel unless data dependencies exist

**Conservative Principle**: When unsure, Story Composer creates dependency (safety over speed).

#### 5.2.3 Combined Example

```
Story A: Refactor Auth Module
    [I] → [CR] ← 3 parallel lanes (within-story)
              ↓
          [T] → [Q] → [Done]

Story B: Add Social Login (depends on A)
    [Pending] ──────────────────────→ [I] (waits for A)

Story C: Refactor Logger (independent)
    [I] → [CR] ← 3 parallel lanes
              ↓
          [T] → [Q] → [Done] (parallel to A)
```

**Key Insight**: Within-story lanes and cross-story scheduling are independent. Story A and Story C both use lane-based parallelism internally WHILE executing in parallel to each other externally.

## 6. Context Loading & Shards

**Shard Registry:**
- In refactor mode, agents load shards via `analysis/shard-index.md` (post-HITL only)
- In incremental mode (`/story`), agents load monolithic analysis docs directly
- Each shard directory contains `index.md` with:
  - Cross-cutting concerns (ALWAYS READ FIRST)
  - Task Type-specific loading sequences
  - Links to relevant shards

**Smart Context Loading (Precision Over Coverage):**
- Load 3-5 documents per story, not entire codebase
- Start with `index.md` to determine which shards are relevant
- Follow Task Type loading sequences for consistent patterns

**Example - Refactoring Task:**
1. `analysis/architecture/index.md` (find relevant shards)
2. `analysis/architecture/current-patterns.md` (cross-cutting)
3. `analysis/architecture/technical-debt.md` (task-specific)
4. `analysis/refactoring/phase-1-plan.md` (current phase)

**Result:** 3-4 documents instead of 50k+ lines

**Incremental Mode (`/story`):**
- No sharding - load monolithic analysis docs
- `analysis/brownfield-architecture.md` + `analysis/flattened-codebase.md`
- Story Composer uses these to understand existing patterns

## 6.1 Smart Index Files (Refactor Mode Only)

In refactor mode, after HITL approval, sharded directories include `index.md` files that enable precision context loading. These are created by Brownfield Architect during Steps 14-15.

**Index File Structure:**

```markdown
# [Analysis Module] Index

## Shards in This Directory
- [List of .md files with brief descriptions]

---

## Context Loading Guide

### Cross-Cutting Concerns (ALWAYS READ FIRST)
These documents contain patterns that apply to ALL refactoring work:
- `current-architecture.md` - Existing system patterns
- `code-patterns.md` - Established conventions to follow
- `technical-debt.md` - Known issues to address or avoid

### Task-Specific Sections
Read these based on your specific refactoring task:
- `api-layer.md` - API refactoring details
- `database-layer.md` - Schema migration patterns
- `frontend-components.md` - UI refactoring patterns

### Context Loading by Task Type

**For API Refactoring:**
1. current-architecture.md (required)
2. code-patterns.md (required)
3. api-layer.md (required)
4. database-layer.md (if data access changes)

**For Database Refactoring:**
1. current-architecture.md (required)
2. database-layer.md (required)
3. api-layer.md (for API contract changes)
```

**Why This Matters:**
- Agents load 3-5 documents instead of 50k+ line codebase
- Consistent refactoring because same patterns loaded for same task type
- Reduces token usage dramatically while improving accuracy

## 7. HITL Gates
- Gate 1 — Refactor Plan Approval:
  - Brownfield Architect produces `analysis/refactoring-plan.md` with phased strategy and risk levels.
  - Hub requests approval; human sets status to `[APPROVED]` or `[REJECTED]`.
  - On approval: Hub moves corresponding refactor stories to `[Pending]`; implementation may proceed.
- Gate 2 — Final Sign‑Off:
125)  - When all stories in the SQLite database are `[Done]` and QA approvals are recorded, the Hub creates `brownfield-proofpoint.md` with `Status: [PENDING_APPROVAL]` and awaits final human approval. The Hub MUST NOT finalize or wrap up until status is `[APPROVED]`.

## 8. Deliverables
1) Brownfield Analysis
   - `analysis/flattened-codebase.md` — Auto-generated snapshot
   - `analysis/brownfield-architecture.md` — Architecture and technical debt assessment
   - `analysis/refactoring-plan.md` — Phased strategy with risk levels (refactor mode)
2) Core Project Artifacts
   - SQLite state machine (`state/workflow.db`) — Project state tracking
   - `stories/` — Feature and refactor story files following PROTOCOL schema
   - `docs/coding-standards.md` — MUST exist; implementation and review agents enforce it
3) Quality & Testing Artifacts
   - Complete unit, integration, and end-to-end test suite (reuse existing first; add gaps only)
   - Test report including coverage metrics and known issues
4) Proofpoint
   - `brownfield-proofpoint.md` — Final sign-off summary

## 9. Phase Completion Criteria
Phase completes when:
1) All stories in the SQLite database are `[Done]`
2) QA Agent validates the application with successful regression suite
3) All deliverables are produced and internally consistent
4) `brownfield-proofpoint.md` is marked `[APPROVED]` by a human
