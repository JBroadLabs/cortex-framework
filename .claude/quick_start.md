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

### Deprecated Commands

- `/hub [description]` - Use `/greenfield` instead (still works but redirects to greenfield mode)

## Configuration

The framework is zero-config by default, but you can customize it in `.claude/config.yml`.

See `.claude/config.yml` for available settings like skipping review stages or adjusting test coverage thresholds.

## Directory Structure

- `.claude/commands/`: Custom agent commands
- `.claude/config.yml`: Framework configuration
- `rx-hackathon/RX.CE-Framework/`: Framework core files
