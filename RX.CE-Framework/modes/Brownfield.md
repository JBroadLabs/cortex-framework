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
- Project task board and stories: `TASK.md`, `stories/`
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

### 4.2 Refactor Mode (/refactor)
Users can analyze existing codebases and create refactoring plans using the `/refactor` command.

Workflow:
1) Refactor Command — User provides `/refactor [scope]`
2) Brownfield Analysis — Brownfield Architect Agent:
   - Flattens the codebase (e.g., Repomix)
   - Analyzes code patterns and technical debt
   - Detects code smells and architectural issues
   - Identifies refactoring opportunities
3) Document Generation — Creates analysis artifacts:
   - `analysis/flattened-codebase.md` (auto-generated snapshot)
   - `analysis/brownfield-architecture.md` (current state assessment)
   - `analysis/refactoring-plan.md` (phased strategy with risk levels)
4) Sharding (if needed)
   - Shard documents into subdirectories under `analysis/`
   - Update index files to guide safe context loading
5) Refactor Story Generation — Creates refactoring story files with:
   - Canonical schema from PROTOCOL templates
   - Refactoring Task Type
   - Risk Level assessment
   - Rollback plans
   - Initial status `[Pending]` (awaiting approval)
6) HITL Approval — Hub prompts the user to review and approve the plan; human sets status to `[APPROVED]` or `[REJECTED]`
7) Implementation (if approved) — Follow the shared workflow from `[I]` → `[Done]`
8) Final QA & Sign‑Off — QA Agent validates; Hub creates `brownfield-proofpoint.md` with header `Status: [PENDING_APPROVAL]` and MUST pause until `[APPROVED]`; if `[REJECTED]`, resume remediation and record reasons in Story notes

## 5. Implementation Execution Model

### 5.1 Shared Implementation Workflow
Universal story execution once implementation begins:

[Pending] → [I] → [CR] → [T] → [Q] → [Done]
           ↑               ↑
    Implementation    Parallel Execution
    (Frontend/       (Code Review +
     Backend)         Unit Tests)

### 5.2 Parallel Execution Workflow
When a story transitions to `[CR]` status, three agents execute simultaneously for faster feedback:

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
The Hub Agent waits for all parallel agents to complete before advancing the story to `[T]`.

## 6. Artifact Registration & Shards
- Newly created artifacts must be registered in `state/artifacts.brownfield.json`.
- Agents MUST query `state/artifacts.brownfield.json` to retrieve the latest artifact list prior to loading context.
- Brownfield analysis documents may be sharded under `analysis/` when size thresholds are exceeded; load shards via index files.
- Minimal context loads are preferred; use analysis indices and summaries.

## 7. HITL Gates
- Gate 1 — Refactor Plan Approval:
  - Brownfield Architect produces `analysis/refactoring-plan.md` with phased strategy and risk levels.
  - Hub requests approval; human sets status to `[APPROVED]` or `[REJECTED]`.
  - On approval: Hub moves corresponding refactor stories to `[Pending]`; implementation may proceed.
- Gate 2 — Final Sign‑Off:
125)  - When all stories in `TASK.md` are `[Done]` and QA approvals are recorded, the Hub creates `brownfield-proofpoint.md` with `Status: [PENDING_APPROVAL]` and awaits final human approval. The Hub MUST NOT finalize or wrap up until status is `[APPROVED]`.

## 8. Deliverables
1) Brownfield Analysis
   - `analysis/flattened-codebase.md` — Auto-generated snapshot
   - `analysis/brownfield-architecture.md` — Architecture and technical debt assessment
   - `analysis/refactoring-plan.md` — Phased strategy with risk levels (refactor mode)
2) Core Project Artifacts
   - `TASK.md` — Master task board
   - `stories/` — Feature and refactor story files following PROTOCOL schema
   - `docs/coding-standards.md` — MUST exist; implementation and review agents enforce it
3) Quality & Testing Artifacts
   - Complete unit, integration, and end-to-end test suite (reuse existing first; add gaps only)
   - Test report including coverage metrics and known issues
4) Proofpoint
   - `brownfield-proofpoint.md` — Final sign-off summary

## 9. Phase Completion Criteria
Phase completes when:
1) All tasks in `TASK.md` are `[Done]`
2) QA Agent validates the application with successful regression suite
3) All deliverables are produced and internally consistent
4) `brownfield-proofpoint.md` is marked `[APPROVED]` by a human
