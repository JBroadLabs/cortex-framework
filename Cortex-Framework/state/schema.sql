-- Cortex-Framework Workflow State Machine
-- Immutable, constraint-enforced state management

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Valid workflow phases (enumeration table)
CREATE TABLE phases (
    phase_id TEXT PRIMARY KEY,
    phase_order INTEGER NOT NULL UNIQUE,
    description TEXT
);

INSERT INTO phases (phase_id, phase_order, description) VALUES
    ('Pending', 0, 'Story created, awaiting implementation'),
    ('I', 1, 'Implementation in progress'),
    ('CR', 2, 'Code review in progress'),
    ('T', 3, 'Testing in progress'),
    ('Q', 4, 'QA validation in progress'),
    ('Done', 5, 'Story complete'),
    ('Blocked', -1, 'Story blocked by dependency or issue'),
    ('Paused', -2, 'Story paused due to dependency failure');

-- Valid agents (enumeration table)
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    can_advance_to TEXT  -- CSV of phases this agent can advance story to
);

INSERT INTO agents (agent_id, agent_name, can_advance_to) VALUES
    ('hub-agent', 'Hub Agent', NULL),
    ('system-design-agent', 'System Design Agent', 'I'),
    ('story-composer-agent', 'Story Composer Agent', 'Pending'),
    ('frontend-agent', 'Frontend Agent', 'CR'),
    ('backend-agent', 'Backend Agent', 'CR'),
    ('code-review-agent', 'Code Review Agent', 'T'),
    ('frontend-unit-testing-agent', 'Frontend Unit Testing Agent', 'T'),
    ('backend-unit-testing-agent', 'Backend Unit Testing Agent', 'T'),
    ('testing-agent', 'Testing Agent', 'Q'),
    ('qa-agent', 'QA Agent', 'Done'),
    ('ask-agent', 'Ask Agent', NULL),
    ('reflector-agent', 'Reflector Agent', NULL),
    ('brownfield-architect-agent', 'Brownfield Architect Agent', 'I');

-- Valid state transitions (what's allowed)
CREATE TABLE valid_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_phase TEXT NOT NULL,
    to_phase TEXT NOT NULL,
    required_agent TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (from_phase) REFERENCES phases(phase_id),
    FOREIGN KEY (to_phase) REFERENCES phases(phase_id),
    FOREIGN KEY (required_agent) REFERENCES agents(agent_id),
    UNIQUE(from_phase, to_phase, required_agent)
);

INSERT INTO valid_transitions (from_phase, to_phase, required_agent, description) VALUES
    ('Pending', 'I', 'frontend-agent', 'Frontend implementation'),
    ('Pending', 'I', 'backend-agent', 'Backend implementation'),
    ('I', 'CR', 'code-review-agent', 'Code review after implementation'),
    ('CR', 'T', 'testing-agent', 'Testing after code review'),
    ('CR', 'T', 'frontend-unit-testing-agent', 'Frontend unit testing'),
    ('CR', 'T', 'backend-unit-testing-agent', 'Backend unit testing'),
    ('T', 'Q', 'qa-agent', 'QA validation after testing'),
    ('Q', 'Done', 'hub-agent', 'Final completion by Hub'),

    -- REVERT TRANSITIONS (Hub reverts story to implementation for fixes)
    ('CR', 'I', 'hub-agent', 'Hub reverts to implementation after CR requests changes'),
    ('T', 'I', 'hub-agent', 'Hub reverts to implementation after test failure'),
    ('Q', 'I', 'hub-agent', 'Hub reverts to implementation after QA rejection'),

    -- PAUSE/RESUME TRANSITIONS (For dependency failure handling)
    ('I', 'Paused', 'hub-agent', 'Pause implementation for dependency remediation'),
    ('CR', 'Paused', 'hub-agent', 'Pause code review for dependency remediation'),
    ('T', 'Paused', 'hub-agent', 'Pause testing for dependency remediation'),
    ('Q', 'Paused', 'hub-agent', 'Pause QA for dependency remediation'),
    ('Paused', 'Pending', 'hub-agent', 'Resume story after dependency resolved');

-- ============================================================================
-- STORY TRACKING
-- ============================================================================

-- Stories table
CREATE TABLE stories (
    story_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    phase TEXT NOT NULL DEFAULT 'Pending',
    current_agent TEXT,
    story_file_path TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 1,
    last_failure_phase TEXT,
    last_failure_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (phase) REFERENCES phases(phase_id),
    FOREIGN KEY (current_agent) REFERENCES agents(agent_id)
);

-- Trigger: Update timestamp on story change
CREATE TRIGGER stories_updated_at
AFTER UPDATE ON stories
BEGIN
    UPDATE stories SET updated_at = datetime('now') WHERE story_id = NEW.story_id;
END;

-- ============================================================================
-- DELEGATION TRANSACTIONS
-- ============================================================================

-- Delegation transactions (the core of state enforcement)
CREATE TABLE delegations (
    txn_id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    from_phase TEXT NOT NULL,
    to_phase TEXT NOT NULL,
    delegated_to_agent TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'abandoned')),
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    evidence_hash TEXT,  -- SHA256 of agent's output section in story file
    evidence_location TEXT,  -- e.g., "### Code Review Results"
    failure_reason TEXT,
    lane_name TEXT DEFAULT 'main',  -- For parallel execution at [CR]
    FOREIGN KEY (story_id) REFERENCES stories(story_id),
    FOREIGN KEY (from_phase) REFERENCES phases(phase_id),
    FOREIGN KEY (to_phase) REFERENCES phases(phase_id),
    FOREIGN KEY (delegated_to_agent) REFERENCES agents(agent_id)
);

-- Index for finding pending delegations
CREATE INDEX idx_delegations_pending ON delegations(status) WHERE status = 'pending';
CREATE INDEX idx_delegations_story ON delegations(story_id);

-- ============================================================================
-- AUDIT LOG (Immutable)
-- ============================================================================

-- Append-only audit log
CREATE TABLE audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    event_type TEXT NOT NULL CHECK (event_type IN (
        'story_created', 'delegation_started', 'delegation_completed',
        'delegation_failed', 'phase_changed', 'violation_attempt'
    )),
    story_id TEXT,
    agent_id TEXT,
    txn_id TEXT,
    from_state TEXT,
    to_state TEXT,
    details TEXT,  -- JSON blob for additional context
    FOREIGN KEY (story_id) REFERENCES stories(story_id),
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- Prevent deletion from audit log
CREATE TRIGGER audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'Audit log is immutable - deletions not allowed');
END;

-- Prevent updates to audit log
CREATE TRIGGER audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'Audit log is immutable - updates not allowed');
END;

-- ============================================================================
-- ENFORCEMENT TRIGGERS
-- ============================================================================

-- Trigger: Validate phase transition is allowed
CREATE TRIGGER validate_phase_transition
BEFORE UPDATE OF phase ON stories
WHEN NEW.phase != OLD.phase
BEGIN
    SELECT RAISE(ABORT, 'Invalid phase transition - not in valid_transitions table')
    WHERE NOT EXISTS (
        SELECT 1 FROM valid_transitions
        WHERE from_phase = OLD.phase AND to_phase = NEW.phase
    );
END;

-- Trigger: Require completed delegation before phase change
CREATE TRIGGER require_delegation_for_transition
BEFORE UPDATE OF phase ON stories
WHEN NEW.phase != OLD.phase AND NEW.phase != 'Blocked'
BEGIN
    SELECT RAISE(ABORT, 'Phase transition requires completed delegation')
    WHERE NOT EXISTS (
        SELECT 1 FROM delegations
        WHERE story_id = NEW.story_id
          AND from_phase = OLD.phase
          AND to_phase = NEW.phase
          AND status = 'completed'
    );
END;

-- Trigger: Log phase changes
CREATE TRIGGER log_phase_change
AFTER UPDATE OF phase ON stories
WHEN NEW.phase != OLD.phase
BEGIN
    INSERT INTO audit_log (event_type, story_id, from_state, to_state)
    VALUES ('phase_changed', NEW.story_id, OLD.phase, NEW.phase);
END;

-- Trigger: Log new stories
CREATE TRIGGER log_story_created
AFTER INSERT ON stories
BEGIN
    INSERT INTO audit_log (event_type, story_id, to_state, details)
    VALUES ('story_created', NEW.story_id, NEW.phase,
            json_object('title', NEW.title, 'file', NEW.story_file_path));
END;

-- Trigger: Log delegation start
CREATE TRIGGER log_delegation_started
AFTER INSERT ON delegations
BEGIN
    INSERT INTO audit_log (event_type, story_id, agent_id, txn_id, from_state, to_state)
    VALUES ('delegation_started', NEW.story_id, NEW.delegated_to_agent,
            NEW.txn_id, NEW.from_phase, NEW.to_phase);
END;

-- Trigger: Log delegation completion
CREATE TRIGGER log_delegation_completed
AFTER UPDATE OF status ON delegations
WHEN NEW.status = 'completed' AND OLD.status = 'pending'
BEGIN
    INSERT INTO audit_log (event_type, story_id, agent_id, txn_id, details)
    VALUES ('delegation_completed', NEW.story_id, NEW.delegated_to_agent,
            NEW.txn_id, json_object('evidence_hash', NEW.evidence_hash));
END;

-- Trigger: Prevent completing delegation without evidence
CREATE TRIGGER require_evidence_for_completion
BEFORE UPDATE OF status ON delegations
WHEN NEW.status = 'completed' AND OLD.status = 'pending'
BEGIN
    SELECT RAISE(ABORT, 'Cannot complete delegation without evidence_hash')
    WHERE NEW.evidence_hash IS NULL OR NEW.evidence_hash = '';
END;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Current state of all stories
CREATE VIEW story_status AS
SELECT
    s.story_id,
    s.title,
    s.phase,
    s.current_agent,
    s.story_file_path,
    s.updated_at,
    (SELECT COUNT(*) FROM delegations d
     WHERE d.story_id = s.story_id AND d.status = 'pending') as pending_delegations,
    (SELECT COUNT(*) FROM delegations d
     WHERE d.story_id = s.story_id AND d.status = 'completed') as completed_delegations
FROM stories s;

-- View: Pending delegations that need attention
CREATE VIEW pending_work AS
SELECT
    d.txn_id,
    d.story_id,
    s.title as story_title,
    d.from_phase,
    d.to_phase,
    d.delegated_to_agent,
    d.lane_name,
    d.started_at,
    ROUND((julianday('now') - julianday(d.started_at)) * 24 * 60, 1) as age_minutes
FROM delegations d
JOIN stories s ON d.story_id = s.story_id
WHERE d.status = 'pending'
ORDER BY d.started_at;

-- View: What Hub should do next for each story
CREATE VIEW next_actions AS
SELECT
    s.story_id,
    s.title,
    s.phase as current_phase,
    vt.to_phase as next_phase,
    vt.required_agent as next_agent,
    vt.description as action_description,
    CASE
        WHEN EXISTS (SELECT 1 FROM delegations d
                     WHERE d.story_id = s.story_id AND d.status = 'pending')
        THEN 'WAIT - delegation in progress'
        WHEN EXISTS (SELECT 1 FROM story_blockers sb
                     WHERE sb.blocked_story_id = s.story_id
                     AND sb.block_status = 'BLOCKED')
        THEN 'BLOCKED - dependencies not met'
        ELSE 'READY - can delegate'
    END as readiness
FROM stories s
JOIN valid_transitions vt ON s.phase = vt.from_phase
WHERE s.phase NOT IN ('Done', 'Blocked', 'Paused');

-- View: Story health status for detecting stuck stories
CREATE VIEW story_health AS
SELECT
    s.story_id,
    s.title,
    s.phase,
    s.attempt_count,
    s.last_failure_phase,
    s.last_failure_at,
    COUNT(r.id) as total_remediations,
    MAX(r.started_at) as most_recent_failure,
    CASE
        WHEN s.attempt_count >= 5 THEN 'STUCK - requires human review'
        WHEN s.attempt_count >= 3 THEN 'AT_RISK - multiple failures'
        ELSE 'HEALTHY'
    END as health_status
FROM stories s
LEFT JOIN remediations r ON s.story_id = r.story_id
GROUP BY s.story_id;

-- ============================================================================
-- DEPENDENCY TRACKING
-- ============================================================================

-- Story-to-story dependencies
-- Types:
--   explicit: downstream waits for [Done]
--   same_module: downstream waits for [T]
--   different_module: downstream can start at [CR]
CREATE TABLE story_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    depends_on_story_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL CHECK (dependency_type IN ('explicit', 'same_module', 'different_module')),
    reason TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_story_id) REFERENCES stories(story_id) ON DELETE CASCADE,
    UNIQUE(story_id, depends_on_story_id)
);

CREATE INDEX idx_dependencies_story ON story_dependencies(story_id);
CREATE INDEX idx_dependencies_blocker ON story_dependencies(depends_on_story_id);

-- View: Which stories block this story?
CREATE VIEW story_blockers AS
SELECT
    d.story_id as blocked_story_id,
    s.title as blocked_story_title,
    s.phase as blocked_story_phase,
    d.depends_on_story_id as blocker_story_id,
    s2.title as blocker_story_title,
    s2.phase as blocker_phase,
    d.dependency_type,
    d.reason,
    CASE d.dependency_type
        WHEN 'explicit' THEN
            CASE WHEN s2.phase = 'Done' THEN 'UNBLOCKED' ELSE 'BLOCKED' END
        WHEN 'same_module' THEN
            CASE WHEN s2.phase IN ('T', 'Q', 'Done') THEN 'UNBLOCKED' ELSE 'BLOCKED' END
        WHEN 'different_module' THEN
            CASE WHEN s2.phase IN ('CR', 'T', 'Q', 'Done') THEN 'UNBLOCKED' ELSE 'BLOCKED' END
    END as block_status
FROM story_dependencies d
JOIN stories s ON d.story_id = s.story_id
JOIN stories s2 ON d.depends_on_story_id = s2.story_id;

-- View: Stories currently blocked
CREATE VIEW blocked_stories AS
SELECT
    blocked_story_id,
    blocked_story_title,
    blocked_story_phase,
    GROUP_CONCAT(blocker_story_id || ' (' || blocker_phase || ')') as blocking_stories,
    COUNT(*) as blocker_count
FROM story_blockers
WHERE block_status = 'BLOCKED'
GROUP BY blocked_story_id;

-- ============================================================================
-- PARALLEL LANE TRACKING
-- ============================================================================

-- Allows multiple agents to work on same story simultaneously
-- Example at [CR]: review lane + fe_tests lane + be_tests lane
CREATE TABLE story_lanes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    lane_name TEXT NOT NULL,  -- 'review', 'fe_tests', 'be_tests', 'main'
    phase TEXT NOT NULL,
    agent TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'paused')),
    started_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    failure_reason TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE,
    FOREIGN KEY (phase) REFERENCES phases(phase_id),
    UNIQUE(story_id, lane_name)
);

CREATE INDEX idx_lanes_story ON story_lanes(story_id);
CREATE INDEX idx_lanes_status ON story_lanes(status);
CREATE INDEX idx_lanes_active ON story_lanes(story_id, status) WHERE status = 'active';

-- View: Lane status for all stories
CREATE VIEW story_lane_status AS
SELECT
    sl.story_id,
    s.title as story_title,
    s.phase as story_phase,
    sl.lane_name,
    sl.phase as lane_phase,
    sl.agent,
    sl.status,
    sl.failure_reason,
    ROUND((julianday('now') - julianday(sl.started_at)) * 24, 1) as hours_active
FROM story_lanes sl
JOIN stories s ON sl.story_id = s.story_id
ORDER BY sl.story_id, sl.lane_name;

-- View: Stories ready to advance (all lanes completed)
CREATE VIEW stories_ready_to_advance AS
SELECT
    s.story_id,
    s.title,
    s.phase as current_phase,
    COUNT(sl.id) as total_lanes,
    SUM(CASE WHEN sl.status = 'completed' THEN 1 ELSE 0 END) as completed_lanes,
    SUM(CASE WHEN sl.status = 'failed' THEN 1 ELSE 0 END) as failed_lanes,
    SUM(CASE WHEN sl.status = 'active' THEN 1 ELSE 0 END) as active_lanes
FROM stories s
LEFT JOIN story_lanes sl ON s.story_id = sl.story_id
GROUP BY s.story_id
HAVING total_lanes > 0;

-- ============================================================================
-- CHECKPOINT SYSTEM
-- ============================================================================

-- Context checkpoints at [I] and [CR] for remediation
CREATE TABLE story_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    phase TEXT NOT NULL,
    checkpoint_type TEXT NOT NULL CHECK (checkpoint_type IN ('implementation', 'code_review')),
    context_snapshot TEXT,  -- JSON: loaded docs, versions, patterns
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE,
    FOREIGN KEY (phase) REFERENCES phases(phase_id)
);

CREATE INDEX idx_checkpoints_story ON story_checkpoints(story_id);
CREATE INDEX idx_checkpoints_phase ON story_checkpoints(story_id, phase);

-- ============================================================================
-- REMEDIATION TRACKING
-- ============================================================================

-- Track test failures and remediation loops
CREATE TABLE remediations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    failed_phase TEXT NOT NULL,
    failure_reason TEXT NOT NULL,
    returned_to_phase TEXT NOT NULL,
    checkpoint_id INTEGER,
    paused_dependents TEXT,  -- JSON array of story_ids
    started_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    resolution_notes TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE,
    FOREIGN KEY (checkpoint_id) REFERENCES story_checkpoints(id)
);

CREATE INDEX idx_remediations_story ON remediations(story_id);
CREATE INDEX idx_remediations_active ON remediations(story_id) WHERE resolved_at IS NULL;

-- ============================================================================
-- CONTEXT LEARNING SYSTEM
-- ============================================================================

-- Track story completions for reflector triggering
CREATE TABLE IF NOT EXISTS learning_metrics (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton table
    completed_stories INTEGER DEFAULT 0,
    last_reflector_batch INTEGER DEFAULT 0,
    next_reflector_at INTEGER DEFAULT 10,
    last_reflector_run TEXT,
    total_deltas_proposed INTEGER DEFAULT 0,
    total_deltas_approved INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Initialize singleton row
INSERT OR IGNORE INTO learning_metrics (id, completed_stories) VALUES (1, 0);

-- Store context feedback from completed stories
CREATE TABLE IF NOT EXISTS context_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    helpful_docs TEXT,      -- JSON array of doc names
    misleading_docs TEXT,   -- JSON array of {doc, reason}
    missing_patterns TEXT,  -- JSON array of pattern descriptions
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_feedback_story ON context_feedback(story_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON context_feedback(created_at);

-- Store issues encountered from completed stories
CREATE TABLE IF NOT EXISTS issues_encountered (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    issue_title TEXT NOT NULL,
    problem TEXT NOT NULL,
    solution TEXT NOT NULL,
    prevention TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_issues_story ON issues_encountered(story_id);
CREATE INDEX IF NOT EXISTS idx_issues_created ON issues_encountered(created_at);

-- Track delta application history (updated to track both types)
CREATE TABLE IF NOT EXISTS delta_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_number INTEGER NOT NULL,
    delta_type TEXT NOT NULL CHECK (delta_type IN ('context', 'troubleshooting')),
    delta_file_path TEXT NOT NULL,
    total_deltas INTEGER NOT NULL,
    approved_deltas INTEGER NOT NULL,
    rejected_deltas INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'applied', 'rejected', 'archived')),
    applied_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_delta_batch ON delta_history(batch_number);
CREATE INDEX IF NOT EXISTS idx_delta_type ON delta_history(delta_type);
