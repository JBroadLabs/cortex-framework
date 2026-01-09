# Quick Start Guide

This guide helps you get up and running with the RX.CE Framework using Claude Code.

## Commands

The framework exposes several commands that load specialized agents.

### Primary Commands

```bash
# New Project (Full POC) - Greenfield Mode
/greenfield "Create a stock trading dashboard"

# Existing Project (Incremental) - Brownfield Mode
/story add CSV export button

# Refactoring (Brownfield) - Refactor Mode
/refactor extract shared auth logic
```

### Advisory Command

Use the `/ask` command for questions and diagnostics:

```bash
/ask "why is story-042 blocked?"
/ask "explain the project structure"
/ask "project status"
```

## Configuration

The framework uses workflow presets for configuration. See mode files (`RX.CE-Framework/modes/`) for workflow details.

## Directory Structure

- `.claude/commands/`: Custom agent commands
- `.claude/agents/`: Agent instruction files
- `rx-hackathon/RX.CE-Framework/`: Framework core files
