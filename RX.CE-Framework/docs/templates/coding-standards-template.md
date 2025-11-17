# Coding Standards Template

Use this as a starter when initializing docs/coding-standards.md. Agents will load and enforce these standards automatically; users can freely customize.

**Version**: 1.0.0
**Status**: [STARTER_TEMPLATE / ACTIVE]
**Tech Stack**: [Auto-detected languages]

## General Standards
- Use clear, self-documenting names.
- Prefer pure functions and small modules.
- Write tests for critical paths and edge cases.
- Avoid global mutable state; prefer dependency injection.
- Document public APIs and complex logic.

## Python Standards
- Follow PEP8 with line length 100.
- Use type hints; run mypy in CI.
- Use black for formatting and flake8 for linting.
- Prefer pathlib to os.path.

## JavaScript Standards
- Use ES modules; prefer const/let over var.
- Enable ESLint with recommended rules.
- Use Prettier for formatting.
- Prefer async/await over callbacks.

## TypeScript Standards
- Strict mode enabled.
- Define explicit types for public functions.
- Avoid any; use unknown when necessary.
- Use tsconfig paths for imports when appropriate.

## Linter Execution
- Python: `black . && flake8 && mypy` (configurable)
- JS/TS: `eslint . && prettier --check .` (configurable)

## Standards Override
When standards must be temporarily violated, add a `## Standards Override` section in the relevant story with justification and scope. Code Review Agent will allow progress with noted exceptions.