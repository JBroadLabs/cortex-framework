# Quick Start Guide

This guide helps you get up and running with the RX.CE Framework using Claude Code.

## Commands

The framework exposes several commands via the Hub Agent.

### Hub Agent (Primary)

Use the `hub` command for all primary interactions:

```bash
# New Project (Full POC)
claude code hub "Create a stock trading dashboard"

# Existing Project (Incremental)
claude code hub "/story add CSV export button"

# Refactoring (Brownfield)
claude code hub "/refactor extract shared auth logic"
```

### Ask Agent (Advisory)

Use the `ask` command for questions and diagnostics:

```bash
claude code ask "why is story-042 blocked?"
claude code ask "explain the project structure"
```

## Configuration

The framework is zero-config by default, but you can customize it in `.claude/config.yml`.

See `.claude/config.yml` for available settings like skipping review stages or adjusting test coverage thresholds.

## Directory Structure

- `.claude/commands/`: Custom agent commands
- `.claude/config.yml`: Framework configuration
- `rx-hackathon/RX.CE-Framework/`: Framework core files
