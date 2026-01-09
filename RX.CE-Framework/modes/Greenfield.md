# Greenfield Mode (Full POC)

## 1. Overview
Greenfield handles net-new projects from scratch. It emphasizes full design upfront, strict context isolation, and an orchestrated build–review–test–QA cycle with Human‑in‑the‑Loop gates.
- Trigger: Full POC mode is selected (default) or session set to `mode=greenfield` by the Hub Agent.

## 2. Context Sources 
Approved inputs loaded by agents when `mode=greenfield`:
- Monolithic design docs (pre‑sharding): `docs/spec.md`, `docs/architecture.md`, `docs/design.md`, `docs/frontend.md`, `docs/backend.md`, `docs/coding-standards.md`
- Sharded docs (post HITL approval): `docs/design/`, `docs/architecture/`, `docs/frontend/`, `docs/backend/` via `docs/shard-index.md`
- Project state: SQLite database (`state/workflow.db`) and story files (`stories/`)
- Test artifacts: unit/integration/E2E suites and reports
- Note: In early Greenfield phases, test artifacts may not exist; they are created as implementation and testing proceed.
Agents must not load brownfield analysis artifacts when `mode=greenfield`.

## 3. Key Activities
- Discovery — Validate scope/constraints; enforce greenfield isolation.
- Analysis — Produce comprehensive design and architecture.
- Planning — Decompose approved design into stories; update task board and statuses.
- Implementation — Build, review, and test features according to standards and story flow.
- Approval — Gate sharding via HITL; finalize QA and produce sign-off proofpoint.

## 4. End-to-End Workflow
1) Initiation
   - Full POC Mode (default): Hub confirms scope and triggers System Design Agent
2) Design
   - System Design Agent produces `spec.md`, `architecture.md`, `design.md`, `frontend.md`, `backend.md`, `coding-standards.md`
3) Human-in-the-Loop (HITL) Design Approval
   - Hub requests approval of monolithic documents for easier review
4) Document Sharding
   - Upon approval, the Hub triggers sharding; the System Design Agent shards approved documents into directories and updates index files:
     - `docs/design/index.md`
     - `docs/architecture/index.md`
     - `docs/frontend/index.md`
     - `docs/backend/index.md`
   - Each shard directory MUST include `index.md` as the entrypoint for context loading.
5) Story Creation
   - Hub delegates to Story Composer Agent to create stories from approved design
   - Story Composer loads sharded design docs via `docs/shard-index.md`
   - Story Composer creates `stories/story-XXX.md` files with `[Pending]` status
   - All stories MUST be created from `docs/templates/story-template.md` and include all required sections in the canonical order
   - Use consistent naming: `stories/story-XXX.md` (zero-padded)
   - Hub registers stories in SQLite state machine and maintains project state
   - Default: every 10 stories (configurable), Hub triggers Reflector Agent to analyze Context Feedback
6) Implementation & Parallel Review/Testing
   - Frontend/Backend implement stories and write unit tests
   - Transition to `[CR]` triggers parallel Code Review + Frontend/Backend Unit Testing
   - Testing Agent runs integration tests when components become available
   - All inter-agent communication is written in the Story under `## Review & Testing Notes` using schemas from `docs/templates/handoff-schemas-template.md`. The Hub Agent orchestrates routing and integration.
7) Final QA
   - QA Agent performs holistic end-to-end validation against Story & Acceptance Criteria:
     - Runs the entire automated test suite to ensure no regressions
     - (If applicable) interacts with the running application to simulate user workflows
     - On approval: append '### QA Results' under '## Review & Testing Notes' in the Story
     - On rejection: return the current story to `[I]` for remediation. If the issue is out-of-scope or discovered as a new defect, create a new story using consistent naming (e.g., `stories/story-002-bug-fix.md`) and link the dependency.
   - Triggered by Hub when ready for final validation (see personas/qa_agent.md)
8) Project Sign-off
   - Hub confirms all tasks `[Done]` and QA approvals recorded in Story notes
   - Hub creates `greenfield-proofpoint.md` with header: `Status: [PENDING_APPROVAL]`
   - Hub MUST pause here and MUST NOT mark completion or emit wrap‑up outputs until status is `[APPROVED]`

## 5. Implementation Execution Model

## 5.1 Shared Implementation Workflow
Universal story execution once implementation begins:

[Pending] → [I] → [CR] → [T] → [Q] → [Done]
           ↑               ↑
    Implementation    Parallel Execution
    (Frontend/       (Code Review +
     Backend)         Unit Tests)

## 5.2 Parallel Execution Workflow
When a story transitions to `[CR]` status, **three agents execute simultaneously**

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

## 5.3 Parallelism Types - Important Distinction

The framework supports TWO types of parallelism at different granularities:

### 5.3.1 Within-Story Parallelism (Lane-Based)
**Scope**: Inside a single story at [CR] phase
**Always Active**: Automatically triggered when story reaches [CR]
**Managed By**: `lane_name` column in `delegations` table

```
[I] Implementation Complete
    ↓
[CR] Code Review Stage (3 parallel lanes)
    ├─→ Lane: code-review (Code Review Agent)
    ├─→ Lane: frontend-test (Frontend Testing Agent)
    └─→ Lane: backend-test (Backend Testing Agent)
    ↓
[T] All lanes complete, proceed to Integration Testing
```

**Key Points**:
- No configuration needed - always active
- Hub waits for ALL lanes to complete before advancing
- Managed by `story_lanes` table
- Failure in any lane pauses the story

### 5.3.2 Cross-Story Parallelism (Dependency-Based)
**Scope**: Multiple stories executing simultaneously
**Conditional**: Based on dependency graph
**Managed By**: `story_dependencies` table

```
Story A [Pending] → [I] → [CR] → [T] → [Q] → [Done]
Story B [Pending] ────────────────────────────────→ [I] (blocked until A done)
Story C [Pending] → [I] → [CR] → [T] → [Q] → [Done] (independent, parallel to A)
```

**Key Points**:
- Requires dependency-free or satisfied dependencies
- Determined by Story Composer during story creation
- Conservative detection: if unsure, create dependency (safer)
- Hub checks dependencies before starting delegation

**Scheduling Rules**:
- **Tier 1**: Explicit dependencies - must be sequential
- **Tier 2**: Same module - prefer sequential (optional parallel if safe)
- **Tier 3**: Different modules - can be parallel

Both parallelism types use the same state machine but operate at different scopes.

---

## 6. Context Loading & Shards

**Shard Registry:**
- Agents load shards strictly via `docs/shard-index.md` (post-approval only)
- Each shard directory contains `index.md` with:
  - Cross-cutting concerns (ALWAYS READ FIRST)
  - Task Type-specific loading sequences
  - Links to relevant shards

**Smart Context Loading (Precision Over Coverage):**
- Load 3-5 documents per story, not entire codebase
- Start with `index.md` to determine which shards are relevant
- Follow Task Type loading sequences for consistent patterns

**Example - API Implementation Task:**
1. `docs/backend/index.md` (find relevant shards)
2. `docs/backend/framework-patterns.md` (cross-cutting)
3. `docs/backend/api-specifications.md` (task-specific)
4. `docs/backend/database-schema.md` (if data access needed)

**Result:** 3-4 documents instead of 50k+ lines

## 6.1 Smart Index Files

Each sharded directory includes an `index.md` file that enables precision context loading. These are created by System Design Agent during Step 9.

**Index File Structure:**

```markdown
# [Module] Index

## Shards in This Directory
- [List of .md files with brief descriptions]

---

## Context Loading Guide

### Cross-Cutting Concerns (ALWAYS READ FIRST)
These documents contain standards that apply to ALL work in this module:
- `framework-patterns.md` - Core patterns and conventions
- `logging-strategy.md` - Error handling and observability

### Task-Specific Sections
Read these based on your specific task type:
- `api-specifications.md` - API endpoint details
- `database-schema.md` - Data models and relationships
- `component-library.md` - UI component patterns

### Context Loading by Task Type

**For API Implementation:**
1. framework-patterns.md (required)
2. logging-strategy.md (required)
3. api-specifications.md (required)
4. database-schema.md (if data access needed)

**For UI Component:**
1. framework-patterns.md (required)
2. component-library.md (required)
3. state-management.md (if state needed)

**For Database Work:**
1. framework-patterns.md (required)
2. database-schema.md (required)
3. api-specifications.md (for API contracts)
```

**Why This Matters:**
- Agents load 3-5 documents instead of entire codebase
- Consistent patterns because same docs loaded for same task type
- "Precision over coverage" - the framework's competitive advantage

## 7. HITL Gates 
- Gate 1 — Design Approval:
  - System Design Agent produces monolithic docs under `docs/`.
  - Hub writes `Status: [PENDING_APPROVAL]` headers on each document prior to HITL review. Example header:
    - Status: [PENDING_APPROVAL]
    - Version: v1.0.0
    - Last Updated: YYYY‑MM‑DD
  - Human changes status to `[APPROVED]`/`[REJECTED]`. On approval, the Hub triggers sharding. No story creation until docs are `[APPROVED]`.
- Gate 2 — Final Sign‑Off:
97)  - When all stories in the SQLite database are `[Done]` and QA approvals are recorded, the Hub creates `greenfield-proofpoint.md` with `Status: [PENDING_APPROVAL]` and awaits final human approval. If `[REJECTED]`, resume remediation and update Story notes with reasons.

## 8. Deliverables
1) Proof‑of‑Concept (POC) — Functional prototype aligned to `docs/spec.md`.
2) Core Documentation
   - SQLite state machine (`state/workflow.db`) — Project state tracking
   - `docs/spec.md` — Functional and non‑functional requirements
   - `docs/design/` — Sharded high‑level overview + index
   - `docs/architecture/` — Sharded system architecture + index
   - `docs/frontend/` — Sharded frontend plan + index
   - `docs/backend/` — Sharded backend plan + index
   - `docs/coding-standards.md` — MUST exist; implementation and review agents enforce it.
   - `docs/shard-index.md` — Registry of shards (post‑approval only)
   - `stories/` — Story files decomposing the work
   - `README.md` — Setup, run, and testing instructions
   - `greenfield-proofpoint.md` — Final sign-off summary
3. Quality & Testing Artifacts
   - Complete unit, integration, and end-to-end test suite
   - Test report including coverage metrics and known issues

## 9. Phase 1 Completion Criteria
Phase 1 completes when:
1) All stories in the SQLite database are `[Done]`
2) QA Agent validates the POC with successful regression suite
3) All deliverables are produced and internally consistent
4) `greenfield-proofpoint.md` is marked `[APPROVED]` by a human
