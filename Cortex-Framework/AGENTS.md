# Multi-Agent Development Framework — Universal Agent Guidance

## 1. Purpose
- Defines universal governance and operating rules for all agents and personas across Greenfield and Brownfield modes.
- Mandatory reading for every agent before performing any task.
- The Hub Agent is the single orchestrator and sole human-facing agent. It owns command routing, task board management, and Human‑in‑the‑Loop (HITL) gates.

## 2. Protocol States
- Follow the universal story state machine defined in PROTOCOL.md (single source of truth).
- The Hub Agent computes the effective path and enforces transitions; configuration may skip [CR], [T], or [Q] stages.

## 3. Modes & Commands
- Mode selection is explicit and per session: mode=greenfield or mode=brownfield.
- Commands and primary routing:
  1) /greenfield (mode=greenfield) → System Design Agent (all workflow agents participate)
  2) /story (mode=incremental) → Story Composer Agent (then implementation agents)
  3) /refactor (mode=refactor) → Brownfield Architect Agent (then implementation agents)
  4) /ask (read-only) → Ask Agent (no state changes)

**Command → Mode Mapping:**
- User types `/greenfield` → Hub Agent receives `mode=greenfield` → Loads Greenfield.md
- User types `/story` → Hub Agent receives `mode=incremental` → Loads Brownfield.md
- User types `/refactor` → Hub Agent receives `mode=refactor` → Loads Brownfield.md
- User types `/ask` → Ask Agent loads (read-only, no mode context)

**Example Usage:**
```bash
# Full POC from scratch
/greenfield "Create a stock trading dashboard with real-time charts"

# Add features to existing code
/story "Add user authentication with email verification"

# Refactor legacy code
/refactor "Modernize authentication to use JWT tokens"

# Get help
/ask "How does dependency management work?"
```
- See Greenfield.md and Brownfield.md for mode‑specific workflows and artifacts.

## 4. Universal Rules (applies to all agents)
1) Task Decomposition — Break large tasks into atomic, verifiable steps before execution.
2) Consistency — Follow folder structure, naming conventions, and coding standards defined in mode docs and PROTOCOL.md.
3) Critical & Useful Output — Produce artifacts that are accurate, actionable, and necessary for subsequent stages. Avoid redundancy.
4) Test Discovery First — Reuse existing tests before authoring new ones; only add tests to cover missing acceptance criteria or gaps.
5) Separation of Concerns — Modify only files within assigned scope; keep interfaces and boundaries clean.
6) Skills Integration — Apply relevant implementation skills (API design, data modeling, error handling, security, etc.) without explicit invocation.
7) HITL Gates — Pause and await approval at required gates; the Hub Agent enforces these.

## 5. Context Engineering (universal patterns)
1) Explicit Mode Routing — Mode flag determines sources, agents, and artifacts for the session.
2) Context Loader — Load only context sources declared for the current mode (see Greenfield.md, Brownfield.md, PROTOCOL.md for interfaces and registries).
3) Shard Navigation — Load context via mode-appropriate shard index:
   - Greenfield: `docs/shard-index.md` (post-HITL approval)
   - Brownfield refactor: `analysis/shard-index.md` (post-HITL approval)
   - Brownfield incremental: Load monolithic analysis docs directly
4) Smart Agent Filtering — Invoke only agents that declare support for the active mode; the Hub Agent enforces this during routing.
5) Minimal Context Loads — Prefer sharded indices and summaries over monolithic documents; reserve full loads for HITL design reviews.

## 6. Routing & Parallelization
1) At [CR], up to three agents may run in parallel for faster feedback:
   - Code Review Agent (quality, standards, linters)
   - Frontend Unit Testing Agent (if frontend changes)
   - Backend Unit Testing Agent (if backend changes)
2) The Hub Agent waits for all parallel agents to complete before advancing the story to [T].
3) Limit repo‑wide scans to Brownfield analysis and refactor workflows; avoid elsewhere.

## 7. Compliance Checklist (every agent must verify)
1) Follow PROTOCOL.md schemas for stories, outputs, and handoffs.
2) Update story state and notes atomically and correctly.
3) Perform test discovery and reuse before adding new tests.
4) Keep changes within assigned scope; maintain boundaries.
5) Link outputs to source context (spec/design/story references).
6) Respect HITL gates; request approval when required.

## 8. Orchestration Rules (Hub & Spoke)
1) Hub Agent is the single point of contact with the human user.
2) Hub delegates tasks to Specialist Agents (Spokes) and synthesizes results.
3) Spokes operate in strict context isolation and report only to the Hub.
4) No direct communication between Spokes; the Hub manages integration.

## 9. Agents Roster (cross‑links)
- Roster Version: 0.1.0
- Schema Version: 1.0.0
- List of agents and persona references (see Cortex‑Framework/personas/* for detailed responsibilities):
  1) Hub Agent (hub-agent) — personas/hub_agent.md — States: [Pending], [I], [CR], [T], [Q], [Done]
  2) Story Composer Agent (story-composer-agent) — personas/story_composer_agent.md — States: [Pending], [I]
  3) System Design Agent (system-design-agent) — personas/system_design_agent.md — States: [I], [CR]
  4) Frontend Agent (frontend-agent) — personas/frontend_agent.md — States: [I], [CR]
  5) Backend Agent (backend-agent) — personas/backend_agent.md — States: [I], [CR]
  6) Code Review Agent (code-review-agent) — personas/code_review_agent.md — States: [CR]
  7) Frontend Unit Testing Agent (frontend-unit-testing-agent) — personas/frontend_unit_testing_agent.md — States: [CR], [T]
  8) Backend Unit Testing Agent (backend-unit-testing-agent) — personas/backend_unit_testing_agent.md — States: [CR], [T]
  9) Testing Agent (testing-agent) — personas/testing_agent.md — States: [T], [Q]
  10) QA Agent (qa-agent) — personas/qa_agent.md — States: [Q], [Done]
  11) Ask Agent (ask-agent) — personas/ask_agent.md — States: [Pending], [I], [CR], [T], [Q], [Done] (read‑only)
  12) Reflector Agent (reflector-agent) — personas/reflector_agent.md — States: [CR], [T], [Q], [Done]
  13) Brownfield Architect Agent (brownfield-architect-agent) — personas/brownfield_architect_agent.md — States: [Pending], [I], [CR]

---

### Brownfield Architect Agent

**File:** `.claude/agents/brownfield-architect-agent.md`

**Purpose:** Legacy codebase analysis and refactoring planning

**Modes:**
1. **Analysis Mode** (`/story` trigger)
   - Steps 1-6 only
   - Creates flattened-codebase.md and brownfield-architecture.md
   - No sharding (Story Composer gets monolithic docs)

2. **Refactor Mode** (`/refactor` trigger)
   - Steps 1-11: Analysis → Planning → Stories → HITL
   - Steps 12-16: Sharding → Index enhancement → Shard registry
   - Creates analysis/shard-index.md for context loading

**Key Feature:** Post-HITL sharding mirrors greenfield workflow for consistent context engineering.

---

## 10. Standardized Repository Structure (Agent Output Locations Only)

Use this canonical structure to know where agent-generated files must live. Framework scaffolding (e.g., README.md, PROTOCOL.md, config/*, personas/*, templates/*) is intentionally excluded here.

```
state/workflow.db           # SQLite state machine tracking project status (managed by Hub)

stories/                    # Story Composer outputs
└── story-*.md              # unit of work; canonical source of truth

docs/                       # System Design outputs (Greenfield)
├── spec.md                 # functional & UI/UX specification (monolithic)
├── architecture.md         # system architecture (monolithic)
├── design.md               # high‑level design (monolithic)
├── frontend.md             # frontend implementation plan (monolithic)
├── backend.md              # backend implementation plan (monolithic)
├── coding-standards.md     # quality standards (MUST exist and be enforced)
├── design/                 # sharded high‑level overview (post HITL approval)
│   └── index.md            # entrypoint for context loading
├── architecture/           # sharded system architecture (post HITL approval)
│   └── index.md
├── frontend/               # sharded frontend plan (post HITL approval)
│   └── index.md
├── backend/                # sharded backend plan (post HITL approval)
│   └── index.md
└── shard-index.md          # registry of shards (post‑approval only)

analysis/                   # Brownfield additions
└── brownfield-architecture.md  # architecture assessment (required in brownfield)

greenfield-proofpoint.md           # Greenfield: final sign‑off summary (created by Hub at project completion)
brownfield-proofpoint.md           # Brownfield: final sign‑off summary (created by Hub at project completion)

(optional/modules)
frontend/                   # Frontend Agent and tests
├── src/                    # implementation
└── tests/                  # unit/integration/E2E

backend/                    # Backend Agent and tests
├── src/                    # implementation
└── tests/                  # unit/integration/E2E
```

Notes:
- Modules (frontend/, backend/) are included only when relevant to the project.
- All agent artifacts must reference their supporting Story to ensure traceability.
- In Greenfield, docs/*.md are created first; after approval they are sharded into docs/*/ with index.md and tracked via docs/shard-index.md.

## 11. Cross‑References (mode‑specific details)
1) Greenfield.md — full end‑to‑end POC workflow and deliverables.
2) Brownfield.md — analysis, refactor planning, and incremental (/story) workflows.
3) PROTOCOL.md — story schemas, handoffs, and state invariants.
4) docs/CONTEXT_LEARNING.md — context learning system, feedback collection, and troubleshooting guide maintenance.
5) config/agent_commands.yaml — command triggers and execution mappings.
6) state/agents_roster.yaml — authoritative agent roster and protocol roles.
