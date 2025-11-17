# Handoff Templates

Agents should use these templates to append entries under "## Review & Testing Notes" in each story. Users can modify wording, but agents must preserve the required fields.

---

## Implementation Handoff

### Handoff from [Frontend/Backend] Agent (Task [Task_Number])

- **Summary of Changes**: [String]
- **Link to Code**: [String/URL]
- **How to Test**: [String]

---

## Code Review Feedback

### Feedback from Code Review Agent (Task [Task_Number])

- **Status**: [APPROVED|REJECTED]
- **Comments**: [String]

---

## Unit Test Results

### Results from [Frontend/Backend] Unit Testing Agent (Task [Task_Number])

- **Status**: [PASSED|FAILED]
- **Commit**: `commit_hash`
- **Summary**: `X/Y tests passed.`
- **Details** (if FAILED):
  - **Test**: `name_of_failing_test`
  - **Error**: `Error message or assertion failure.`

---

## Testing Results

### Results from Testing Agent (Task [Task_Number])

- **Status**: [PASSED|FAILED]
- **Details**: [String: Log output or failure details]