# Shard Index - Simple Chess Game POC

## Overview

This index provides context loading guidance for the Simple Chess Game POC.

**Note**: Due to the minimal scope of this POC, documents remain in their monolithic form. No subdirectory sharding is required.

---

## Document Registry

| Document | Purpose | When to Load |
|----------|---------|--------------|
| [spec.md](spec.md) | Functional requirements, acceptance criteria | Story planning, QA validation |
| [architecture.md](architecture.md) | System architecture, data models, APIs | All implementation tasks |
| [design.md](design.md) | High-level design, user journey | Understanding overall approach |
| [frontend.md](frontend.md) | UI implementation details | Frontend implementation tasks |
| [backend.md](backend.md) | Game logic implementation | Backend/engine implementation |
| [coding-standards.md](coding-standards.md) | Code conventions | All implementation, code review |

---

## Context Loading by Task Type

### For UI/Board Implementation
1. `frontend.md` (required)
2. `coding-standards.md` (required)
3. `spec.md` (for requirements reference)

### For Chess Engine Implementation
1. `backend.md` (required)
2. `architecture.md` (for data models)
3. `coding-standards.md` (required)

### For Integration Work
1. `architecture.md` (required)
2. `frontend.md` (UI contract)
3. `backend.md` (engine contract)

### For Code Review
1. `coding-standards.md` (required)
2. `spec.md` (for acceptance criteria)

### For QA/Testing
1. `spec.md` (acceptance criteria)
2. `design.md` (test scenarios)

---

## File Structure (Target)

```
chess-game/
├── index.html          # Main HTML structure
├── styles.css          # Board and piece styling
├── js/
│   ├── game.js         # Game controller (UI events, DOM updates)
│   └── chess-engine.js # Chess logic (rules, validation, state)
└── README.md           # Setup instructions
```
