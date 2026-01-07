# Agent Communication Protocol

This is the universal operating contract for all agents. It defines core invariants, the shared story state machine, agent-to-agent handoff rules, and context isolation. Mode-specific workflows, documents, and artifacts live in Greenfield.md and Brownfield.md. Command details live in COMMANDS.md.

## 1. Scope & Core Invariants

- Single Source of Truth: Every unit of work is represented by a Story file under `/stories/story-*.md`. Agents read and write status, notes, and handoffs exclusively in that file.
- Stateless Operation: Agents start with empty context for each story, load only the required context from the file system, and clear it on completion or state change.
- Context Sources:
  - Pre-approval: Load monolithic design or analysis docs appropriate to the active mode.
  - Post-approval: Load shards strictly via `docs/shard-index.md`.
  - Do not retain memory across stories or sessions.
- Hub-Orchestrated Handoffs: All inter-agent communication is written in the Story file under `## Review & Testing Notes` using schemas from `docs/templates/handoff-schemas-template.md`. No direct spoke-to-spoke messaging; the Hub Agent manages routing and integration.
- Command Registry: Agents MUST load triggers and execution mappings from `config/agent_commands.yaml` (platform-native config if required). No hardcoded command logic.
- Triggering & Routing: The Hub Agent queries the SQLite state machine for status changes, loads `state/agents_roster.yaml` to determine which agents are eligible for the current state, and invokes them via `config/agent_commands.yaml`. Agents never self-trigger; they execute only on Hub invocation. At [CR], the Hub may fan out to parallel agents per roster and waits for all to finish before advancing.
- Roster Source of Truth: Agents and their roles/states are defined in `state/agents_roster.yaml`. Do not duplicate roster content here.

## 2. Story State Machine (Universal)

Default path (when all stages enabled):
```
[Pending] → [I] → [CR] → [T] → [Q] → [Done]
```
State summaries:
- [Pending] — awaiting initiation/approval or upstream dependencies
- [Paused] — temporarily halted due to dependency failure or resource contention; resumes on remediation
- [I] — implementation in progress (Frontend/Backend as applicable)
- [CR] — code review + unit testing (parallelized)
- [T] — integration/component testing
- [Q] — quality assurance/regression
- [Done] — completed and approved

Configurable stage skips: `.claude/config.yml` supports `skip_code_review`, `skip_testing`, and `skip_qa`; the Hub Agent computes and enforces the effective path (see `utils/config_simple.py`).

## 3. Artifact Locations (minimal)

Agents rely on these canonical locations; scaffolding files are excluded:
- Canonical directory baseline: see AGENTS.md Section "Directory Baseline"; agents MUST write only within those paths.
- `/stories/story-*.md` — source of truth for a unit of work
- `docs/shard-index.md` — shard registry (post-approval only)
- `docs/coding-standards.md` — active standards (MUST exist and be enforced)
- `frontend/src/`, `frontend/tests/` (if applicable)
- `backend/src/`, `backend/tests/` (if applicable)

Coding Standards:
- Implementation agents load `docs/coding-standards.md` before writing code.
- Code Review agent enforces standards and runs linters.
- Standards Override: A story may include `## Standards Override` with justification. Review acknowledges overrides.

## 4. Story Schema & Templates

Agents MUST create/update stories using `docs/templates/story-template.md`. Load the template verbatim and fill all required sections.

### Runtime Tracking (Story‑Only)

- Hub MUST record runtime state directly in the story header fields:
  - `Status` and `Phase` reflect the universal state machine
  - `Active Agent` indicates current owner at this phase
  - `Started`/`Updated` timestamps capture lifecycle
- On every handoff, Hub writes a structured entry under `## Handoffs` and logs outcomes under `## Review & Testing Notes`.
- The SQLite state machine provides project‑level status; no auxiliary tracker files are required.
- If any discrepancy occurs, Story files and SQLite database are authoritative; Hub updates the header fields to realign.

## 5. Dependencies & Pausing

- Explicit dependencies: downstream story cannot enter [I] until dependencies are [Done].
- Same-module implicit dependencies: downstream story can enter [I] only when upstream is at least [T].
- Parallel stories: may start at [CR] once prior story reaches [CR].
- If a dependency fails at review/testing, dependent stories move to [Paused] until remediation completes.

## 6. Context Isolation & Checkpoints

Rules:
1) One story per agent context at a time.
2) Mandatory reset before ANY work (new or remediation): clear loaded docs, working memory, and patterns; announce reset in the Story notes.
3) Checkpoint at [I] → [CR]: record loaded docs (with versions), key patterns, decisions, and task completion status.
4) Remediation restore ([CR] → [I] or [T] → [I]): clear context, restore from checkpoint, apply feedback from `## Review & Testing Notes` only.
5) Pause save ([I] → [Paused]): save progress, note partial work and resume point.

Context transitions:
```
[Pending] → [I]: fresh load from Story (pre-approval) or shards via `docs/shard-index.md` (post-approval)
[I] → [CR]: checkpoint and clear
[CR] → [I] / [T] → [I]: clear, restore from checkpoint, apply feedback
[Paused] → [I]: clear, restore, resume
```

## 7. Task Progress & Completion

- Use checkboxes in Story tasks: `[ ]` not started, `[~]` in progress, `[x]` complete (timestamp), `[!]` blocked (reason), `[⏸]` paused (reason).
- Gate to [CR]: ALL tasks must be `[x]` (no `[ ]` or `[~]`). Module scope applies (Frontend-only, Backend-only, or Full-Stack).
- If ANY task is blocked: the story cannot move to [CR] until resolved.
- Agents MUST verify:
```
if count_tasks('[x]') < count_all_tasks():
  BLOCK → remain at [I]
else:
  PROCEED → move to [CR]
```

## 8. Remediation Priority

When a story fails and returns to [I]:
- If another story in the same module is at [I], PAUSE it immediately and resume only after remediation reaches [T].
- Announce context reset and restoration from checkpoint in the Story notes.
- Apply fixes strictly based on `## Review & Testing Notes` feedback.

## 9. HITL Approval Gates (file-based)

Gate 1 — Design Artifact Approval:
- Trigger: System Design Agent produces initial design docs under `docs/`.
- Hub writes a header to each doc before review:
  - `Status: [PENDING_APPROVAL]` → human changes to `[APPROVED]` or `[REJECTED]`.
- On approval: Hub triggers sharding; agents load shards only via `docs/shard-index.md`.
- Constraint: No sharding or story creation until design docs are `[APPROVED]`.

Gate 2 — Final Project Sign-Off:
- Trigger: Hub detects all stories are `[Done]` in the SQLite state machine and QA approvals are recorded in Story notes.
- Action: Hub creates a mode-specific proofpoint and writes header:
  - Greenfield: `greenfield-proofpoint.md`
  - Brownfield: `brownfield-proofpoint.md`
  - Header: `Status: [PENDING_APPROVAL]` → human changes to `[APPROVED]` or `[REJECTED]`.
- Constraints:
  - Hub MUST pause at Gate 2 and MUST NOT mark completion or emit wrap‑up outputs until the proofpoint file exists and shows `Status: [APPROVED]`.
  - If status is `[REJECTED]`, Hub resumes remediation by reopening relevant stories and records reasons under `## Review & Testing Notes`.
  - Agents MUST treat the proofpoint as the single source of project sign‑off.

## 10. Mode References (not duplicated here)

- Greenfield.md — full POC workflow and sharding details.
- Brownfield.md — incremental `/story` and `/refactor` workflows and analysis artifacts.
- docs/CONTEXT_ENGINEERING.md — loader, registries, and isolation patterns.
