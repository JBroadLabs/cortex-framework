# Greenfield Mode (Full POC)

## 1. Overview
Greenfield handles net-new projects from scratch. It emphasizes full design upfront, strict context isolation, and an orchestrated build–review–test–QA cycle with Human‑in‑the‑Loop gates.
- Trigger: Full POC mode is selected (default) or session set to `mode=greenfield` by the Hub Agent.

## 2. Context Sources 
Approved inputs loaded by agents when `mode=greenfield`:
- Monolithic design docs (pre‑sharding): `docs/spec.md`, `docs/architecture.md`, `docs/design.md`, `docs/frontend.md`, `docs/backend.md`, `docs/coding-standards.md`
- Sharded docs (post HITL approval): `docs/design/`, `docs/architecture/`, `docs/frontend/`, `docs/backend/` via `docs/shard-index.md`
- Project task board and stories: `TASK.md`, `stories/`
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
5) Decomposition & Task Board Creation
   - Hub decomposes design into `stories/` (e.g., `stories/story-001.md`) with `[Pending]` status
   - All stories MUST be created from `docs/templates/story-template.md` and include all required sections in the canonical order.
   - Use consistent naming: `stories/story-XXX.md` (zero-padded).
   - Hub creates and maintains `TASK.md` overview
   - Default: every 10 stories (configurable), Hub triggers Reflector Agent to analyze Context Feedback across stories and produce evidence-based delta proposals. For small projects, this may be reduced; for large projects, Hub may trigger it on a rolling cadence.
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
   - Hub confirms all tasks `[Done]`, creates `greenfield-proofpoint.md`, awaits final approval

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
## 6. Artifact Registration & Shards
- Newly created artifacts must be registered in `state/artifacts.greenfield.json`.
- Agents MUST query `state/artifacts.greenfield.json` to retrieve the latest artifact list prior to loading context.
- Agents load shards strictly via `docs/shard-index.md` once approved.
- Minimal context loads are preferred; use shard indices and summaries.

## 7. HITL Gates 
- Gate 1 — Design Approval:
  - System Design Agent produces monolithic docs under `docs/`.
  - Hub writes `Status: [PENDING_APPROVAL]` headers on each document prior to HITL review. Example header:
    - Status: [PENDING_APPROVAL]
    - Version: v1.0.0
    - Last Updated: YYYY‑MM‑DD
  - Human changes status to `[APPROVED]`/`[REJECTED]`. On approval, the Hub triggers sharding. No story creation until docs are `[APPROVED]`.
- Gate 2 — Final Sign‑Off:
  - When all stories in `TASK.md` are `[Done]`, the Hub creates `greenfield-proofpoint.md` and awaits final human approval.

## 8. Deliverables
1) Proof‑of‑Concept (POC) — Functional prototype aligned to `docs/spec.md`.
2) Core Documentation
   - `TASK.md` — Master task board
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
1) All tasks in `TASK.md` are `[Done]`
2) QA Agent validates the POC with successful regression suite
3) All deliverables are produced and internally consistent
4) `greenfield-proofpoint.md` is marked `[APPROVED]` by a human

