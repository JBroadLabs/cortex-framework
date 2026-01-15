**HUMAN REVIEW REQUIRED**

**Status**: [APPROVED]

To approve, change status to: [APPROVED]
To reject, change status to: [REJECTED]

---

# Coding Standards

**Version**: v1.0.0
**Status**: [STARTER_TEMPLATE]
**Tech Stack**: JavaScript
**Last Updated**: 2026-01-15

## Philosophy
Clean, readable, maintainable. Favor simplicity.

## JavaScript
**Docs**: JSDoc for public functions and classes
**Format**: Consistent spacing, 100 chars max line length
**Lint**: ESLint recommended rules
**Test**: Manual testing for POC (unit tests optional)
**Style**: `camelCase` for functions/variables, `PascalCase` for classes

## Code Organization
**Separation**: Keep DOM logic (game.js) separate from game logic (chess-engine.js)
**Modularity**: Each file has single responsibility
**Comments**: Explain why, not what
**Naming**: Descriptive names over short names

## HTML/CSS
**HTML**: Semantic elements, minimal inline styles
**CSS**: Class-based styling, avoid !important unless necessary
**Responsive**: Not required for POC, but plan for it

## File Naming
**Convention**: lowercase-with-hyphens for files
**Examples**: `chess-engine.js`, `index.html`, `styles.css`

## Functions
**Size**: Keep functions small (< 50 lines ideal)
**Parameters**: Max 4 parameters, use objects for more
**Returns**: Explicit return types in JSDoc
**Pure**: Prefer pure functions where possible

## Classes
**Constructor**: Initialize all properties
**Methods**: Public methods first, private methods last
**Naming**: Use descriptive method names

## Error Handling
**Validation**: Validate input at function boundaries
**Errors**: Log errors to console, fail gracefully
**Recovery**: Always allow game reset on error

## Comments
**Required**: Complex algorithms (checkmate detection, castling)
**Optional**: Self-explanatory code needs no comments
**Format**: Single line `//` for brief, multi-line `/* */` for detailed

## Constants
**Location**: Top of file or separate constants file
**Naming**: UPPER_SNAKE_CASE for true constants
**Usage**: Avoid magic numbers/strings

## Testing
**POC Phase**: Manual testing sufficient
**Future**: Unit tests for core logic (chess-engine.js)
**Coverage**: Focus on edge cases (castling, en passant, checkmate)

## Git Commits
**Format**: Imperative mood ("Add feature" not "Added feature")
**Size**: Small, focused commits
**Messages**: Descriptive commit messages

## Linter Commands
**JavaScript**: Use browser console for debugging (no build tools for POC)
**Future**: `eslint . && prettier --check .` when added

## Override
Add `## Standards Override` to implementation with justification if deviating from these standards.
