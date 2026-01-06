-- ============================================================================
-- MIGRATION 001: Add Parallelism & Dependency Support
-- ============================================================================
-- Applies to existing databases without data loss
-- Safe to run multiple times (uses IF NOT EXISTS)
-- ============================================================================

-- ============================================================================
-- 1. DEPENDENCY TRACKING
-- ============================================================================

-- Story-to-story dependencies
-- Types match framework docs (lines 27238-27241):
--   explicit: downstream waits for [Done]
--   same_module: downstream waits for [T]
--   different_module: downstream can start at [CR]
CREATE TABLE IF NOT EXISTS story_dependencies (
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

CREATE INDEX IF NOT EXISTS idx_dependencies_story ON story_dependencies(story_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_blocker ON story_dependencies(depends_on_story_id);

-- View: Which stories block this story?
CREATE VIEW IF NOT EXISTS story_blockers AS
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
CREATE VIEW IF NOT EXISTS blocked_stories AS
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
-- 2. PARALLEL LANE TRACKING
-- ============================================================================

-- Allows multiple agents to work on same story simultaneously
-- Example at [CR]: review lane + fe_tests lane + be_tests lane
CREATE TABLE IF NOT EXISTS story_lanes (
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

CREATE INDEX IF NOT EXISTS idx_lanes_story ON story_lanes(story_id);
CREATE INDEX IF NOT EXISTS idx_lanes_status ON story_lanes(status);
CREATE INDEX IF NOT EXISTS idx_lanes_active ON story_lanes(story_id, status) WHERE status = 'active';

-- View: Lane status for all stories
CREATE VIEW IF NOT EXISTS story_lane_status AS
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
CREATE VIEW IF NOT EXISTS stories_ready_to_advance AS
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
-- 3. CHECKPOINT SYSTEM
-- ============================================================================

-- Context checkpoints at [I] and [CR] for remediation
-- Framework docs (lines 27243-27258)
CREATE TABLE IF NOT EXISTS story_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id TEXT NOT NULL,
    phase TEXT NOT NULL,
    checkpoint_type TEXT NOT NULL CHECK (checkpoint_type IN ('implementation', 'code_review')),
    context_snapshot TEXT,  -- JSON: loaded docs, versions, patterns
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES stories(story_id) ON DELETE CASCADE,
    FOREIGN KEY (phase) REFERENCES phases(phase_id)
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_story ON story_checkpoints(story_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_phase ON story_checkpoints(story_id, phase);

-- ============================================================================
-- 4. REMEDIATION TRACKING
-- ============================================================================

-- Track test failures and remediation loops
-- Framework docs (lines 27273-27278)
CREATE TABLE IF NOT EXISTS remediations (
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

CREATE INDEX IF NOT EXISTS idx_remediations_story ON remediations(story_id);
CREATE INDEX IF NOT EXISTS idx_remediations_active ON remediations(story_id) WHERE resolved_at IS NULL;

-- ============================================================================
-- 5. WORKFLOW PRESETS
-- ============================================================================

-- Store workflow configurations (strict/fast/minimal)
CREATE TABLE IF NOT EXISTS workflow_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preset_name TEXT UNIQUE NOT NULL,
    description TEXT,
    workflow_path TEXT NOT NULL,  -- JSON: ["Pending", "I", "CR", "T", "Q", "Done"]
    parallel_at_cr BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Insert default presets
INSERT OR IGNORE INTO workflow_presets (preset_name, description, workflow_path, parallel_at_cr) VALUES
    ('strict', 'Full workflow with all quality gates', '["Pending", "I", "CR", "T", "Q", "Done"]', 1),
    ('fast', 'Skip code review and QA for rapid iteration', '["Pending", "I", "T", "Done"]', 0),
    ('minimal', 'Implementation only, no validation', '["Pending", "I", "Done"]', 0);

-- Active configuration
CREATE TABLE IF NOT EXISTS active_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO active_config (key, value) VALUES ('workflow_preset', 'strict');

-- ============================================================================
-- 6. MODIFY EXISTING TABLES (Additive - No Data Loss)
-- ============================================================================

-- Add lane_name to delegations table (defaults to 'main' for existing records)
--
-- Note: SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
-- This will be handled by workflow_engine.py _ensure_schema_updates() method
-- which checks if the column exists and adds it if needed.
--
-- Manual command (if needed):
-- ALTER TABLE delegations ADD COLUMN lane_name TEXT DEFAULT 'main';

-- ============================================================================
-- 7. ENHANCED VIEWS (Replace existing if needed)
-- ============================================================================

-- Drop and recreate pending_work view to include lane info
DROP VIEW IF EXISTS pending_work;
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

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Verify migration:
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
-- Should see: story_dependencies, story_lanes, story_checkpoints, remediations, workflow_presets
-- ============================================================================
