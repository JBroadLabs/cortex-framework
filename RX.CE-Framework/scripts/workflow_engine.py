#!/usr/bin/env python3
"""
RX.CE-Framework Workflow Engine
SQLite-backed state machine with immutable audit trail.

This engine MUST be called by Hub agent for all workflow operations.
Direct state manipulation is prevented by database constraints.
"""

import sqlite3
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the framework root directory (parent of scripts directory)
FRAMEWORK_ROOT = Path(__file__).parent.parent
DB_PATH = FRAMEWORK_ROOT / "state" / "workflow.db"
SCHEMA_PATH = FRAMEWORK_ROOT / "state" / "schema.sql"
STORIES_DIR = Path("stories")  # This is relative to project root

class Phase(Enum):
    PENDING = "Pending"
    IMPLEMENTATION = "I"
    CODE_REVIEW = "CR"
    TESTING = "T"
    QA = "Q"
    DONE = "Done"
    BLOCKED = "Blocked"
    PAUSED = "Paused"

class DelegationStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class NextAction:
    story_id: str
    story_title: str
    current_phase: str
    next_phase: str
    next_agent: str
    action_description: str
    readiness: str

@dataclass
class PendingDelegation:
    txn_id: str
    story_id: str
    story_title: str
    from_phase: str
    to_phase: str
    agent: str
    started_at: str
    age_minutes: float

@dataclass
class DelegationResult:
    success: bool
    txn_id: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict] = None

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

class WorkflowEngine:
    """SQLite-backed workflow state machine."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self):
        """Create database and schema if not exists."""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_schema()

        # Ensure schema is up to date
        self._ensure_schema_updates()

    def _init_schema(self):
        """Initialize database with schema."""
        schema_path = SCHEMA_PATH
        if not schema_path.exists():
            # Try relative to script
            schema_path = Path(__file__).parent.parent / "state" / "schema.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        conn = sqlite3.connect(self.db_path)
        conn.executescript(schema_sql)
        conn.close()
        print(f"[OK] Database initialized: {self.db_path}")

    def _ensure_schema_updates(self):
        """
        Ensure schema is up to date with migrations.
        Adds lane_name column to delegations if it doesn't exist.
        """
        conn = self._get_conn()
        try:
            # Check if lane_name column exists in delegations table
            columns = conn.execute("PRAGMA table_info(delegations)").fetchall()
            column_names = [col[1] for col in columns]

            if 'lane_name' not in column_names:
                print("[!] Adding lane_name column to delegations table...")
                conn.execute("ALTER TABLE delegations ADD COLUMN lane_name TEXT DEFAULT 'main'")
                conn.commit()
                print("[OK] lane_name column added")
        finally:
            conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    # ========================================================================
    # STORY MANAGEMENT
    # ========================================================================

    def register_story(self, story_id: str, title: str,
                       story_file_path: str) -> DelegationResult:
        """Register a new story in the state machine."""
        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO stories (story_id, title, story_file_path, phase)
                VALUES (?, ?, ?, 'Pending')
            """, (story_id, title, story_file_path))
            conn.commit()
            return DelegationResult(
                success=True,
                message=f"Story {story_id} registered in state machine"
            )
        except sqlite3.IntegrityError as e:
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()

    def get_story_status(self, story_id: str) -> Optional[Dict]:
        """Get current status of a story."""
        conn = self._get_conn()
        try:
            row = conn.execute("""
                SELECT * FROM story_status WHERE story_id = ?
            """, (story_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_stories(self) -> List[Dict]:
        """Get status of all stories."""
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM story_status").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    # ========================================================================
    # HUB INTERFACE - These are what Hub MUST call
    # ========================================================================

    def hub_get_next_action(self, story_id: str) -> Optional[NextAction]:
        """
        Get the next action Hub should take for a story.

        Hub MUST call this to know what to do. Cannot be bypassed.
        """
        conn = self._get_conn()
        try:
            row = conn.execute("""
                SELECT * FROM next_actions WHERE story_id = ?
            """, (story_id,)).fetchone()

            if not row:
                return None

            return NextAction(
                story_id=row['story_id'],
                story_title=row['title'],
                current_phase=row['current_phase'],
                next_phase=row['next_phase'],
                next_agent=row['next_agent'],
                action_description=row['action_description'],
                readiness=row['readiness']
            )
        finally:
            conn.close()

    def hub_get_all_next_actions(self) -> List[NextAction]:
        """Get next actions for all active stories."""
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM next_actions").fetchall()
            return [NextAction(
                story_id=row['story_id'],
                story_title=row['title'],
                current_phase=row['current_phase'],
                next_phase=row['next_phase'],
                next_agent=row['next_agent'],
                action_description=row['action_description'],
                readiness=row['readiness']
            ) for row in rows]
        finally:
            conn.close()

    def hub_get_pending_delegations(self) -> List[PendingDelegation]:
        """
        Get all pending delegations that need attention.

        Hub MUST check this at start of every interaction.
        """
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM pending_work").fetchall()
            return [PendingDelegation(
                txn_id=row['txn_id'],
                story_id=row['story_id'],
                story_title=row['story_title'],
                from_phase=row['from_phase'],
                to_phase=row['to_phase'],
                agent=row['delegated_to_agent'],
                started_at=row['started_at'],
                age_minutes=row['age_minutes']
            ) for row in rows]
        finally:
            conn.close()

    def hub_start_delegation(self, story_id: str,
                             to_agent: str,
                             lane_name: str = 'main') -> DelegationResult:
        """
        Start a delegation transaction with optional lane support.

        Args:
            story_id: Story being delegated
            to_agent: Agent receiving delegation
            lane_name: Lane name for parallel work (default: 'main')
                      Use 'review', 'fe_tests', 'be_tests' for [CR] parallelism

        Returns:
            DelegationResult with success/failure and txn_id
        """
        conn = self._get_conn()
        try:
            # STEP 1: CHECK DEPENDENCIES FIRST
            if not self._check_dependencies(conn, story_id):
                blockers = self._get_blocking_stories(conn, story_id)
                return DelegationResult(
                    success=False,
                    error=f"Story {story_id} blocked by: {', '.join(blockers)}"
                )

            # STEP 2: Get current story state
            story = conn.execute("""
                SELECT phase FROM stories WHERE story_id = ?
            """, (story_id,)).fetchone()

            if not story:
                return DelegationResult(
                    success=False,
                    error=f"Story {story_id} not found in state machine"
                )

            current_phase = story['phase']

            # STEP 3: Find valid transition
            transition = conn.execute("""
                SELECT to_phase FROM valid_transitions
                WHERE from_phase = ? AND required_agent = ?
            """, (current_phase, to_agent)).fetchone()

            if not transition:
                return DelegationResult(
                    success=False,
                    error=f"No valid transition from [{current_phase}] using {to_agent}"
                )

            to_phase = transition['to_phase']

            # STEP 4: Check for existing pending delegation IN THIS LANE
            # CHANGED: Was checking all delegations, now lane-specific
            existing = conn.execute("""
                SELECT txn_id FROM delegations
                WHERE story_id = ? AND lane_name = ? AND status = 'pending'
            """, (story_id, lane_name)).fetchone()

            if existing:
                return DelegationResult(
                    success=False,
                    error=f"Story {story_id} lane '{lane_name}' already has pending delegation: {existing['txn_id']}"
                )

            # STEP 5: Generate transaction ID with lane
            txn_id = f"txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{story_id}_{lane_name}"

            # STEP 6: Create delegation record with lane
            conn.execute("""
                INSERT INTO delegations
                (txn_id, story_id, from_phase, to_phase, delegated_to_agent, lane_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (txn_id, story_id, current_phase, to_phase, to_agent, lane_name))

            # STEP 7: Update story's current agent
            conn.execute("""
                UPDATE stories SET current_agent = ?
                WHERE story_id = ?
            """, (to_agent, story_id))

            # STEP 8: Create or update lane tracking (if using lanes)
            if lane_name != 'main':
                conn.execute("""
                    INSERT OR REPLACE INTO story_lanes
                    (story_id, lane_name, phase, agent, status, started_at)
                    VALUES (?, ?, ?, ?, 'active', datetime('now'))
                """, (story_id, lane_name, to_phase, to_agent))

            conn.commit()

            return DelegationResult(
                success=True,
                txn_id=txn_id,
                message=f"Delegation started: {to_agent} on {story_id} (lane: {lane_name})"
            )

        except sqlite3.IntegrityError as e:
            conn.rollback()
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()

    def _check_dependencies(self, conn, story_id: str) -> bool:
        """
        Check if story's dependencies are satisfied.
        Returns True if story can proceed.
        """
        blocked = conn.execute("""
            SELECT COUNT(*) as count FROM story_blockers
            WHERE blocked_story_id = ? AND block_status = 'BLOCKED'
        """, (story_id,)).fetchone()

        return blocked['count'] == 0

    def _get_blocking_stories(self, conn, story_id: str) -> List[str]:
        """Get list of story IDs blocking this story."""
        blockers = conn.execute("""
            SELECT blocker_story_id, blocker_phase, dependency_type
            FROM story_blockers
            WHERE blocked_story_id = ? AND block_status = 'BLOCKED'
        """, (story_id,)).fetchall()

        return [f"{b['blocker_story_id']} ({b['blocker_phase']}, {b['dependency_type']})"
                for b in blockers]

    def add_dependency(self, story_id: str, depends_on: str,
                       dep_type: str, reason: str = None) -> DelegationResult:
        """
        Add a dependency between stories.

        Args:
            story_id: Story that depends on another
            depends_on: Story ID that must complete first
            dep_type: 'explicit', 'same_module', or 'different_module'
            reason: Optional explanation
        """
        if dep_type not in ['explicit', 'same_module', 'different_module']:
            return DelegationResult(
                success=False,
                error=f"Invalid dependency type: {dep_type}"
            )

        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO story_dependencies
                (story_id, depends_on_story_id, dependency_type, reason)
                VALUES (?, ?, ?, ?)
            """, (story_id, depends_on, dep_type, reason))
            conn.commit()

            return DelegationResult(
                success=True,
                message=f"Dependency added: {story_id} depends on {depends_on} ({dep_type})"
            )
        except sqlite3.IntegrityError as e:
            return DelegationResult(
                success=False,
                error=f"Dependency already exists or invalid story IDs: {e}"
            )
        finally:
            conn.close()

    def hub_complete_delegation(self, txn_id: str,
                                evidence_hash: str,
                                evidence_location: str = None) -> DelegationResult:
        """
        Complete a delegation transaction.

        Hub MUST call this AFTER subagent completes and evidence is verified.
        Cannot complete without evidence_hash.
        """
        conn = self._get_conn()
        try:
            # Get delegation details
            delegation = conn.execute("""
                SELECT * FROM delegations WHERE txn_id = ?
            """, (txn_id,)).fetchone()

            if not delegation:
                return DelegationResult(
                    success=False,
                    error=f"Delegation {txn_id} not found"
                )

            if delegation['status'] != 'pending':
                return DelegationResult(
                    success=False,
                    error=f"Delegation {txn_id} is not pending (status: {delegation['status']})"
                )

            # Update delegation status (trigger will validate evidence_hash)
            conn.execute("""
                UPDATE delegations
                SET status = 'completed',
                    completed_at = datetime('now'),
                    evidence_hash = ?,
                    evidence_location = ?
                WHERE txn_id = ?
            """, (evidence_hash, evidence_location, txn_id))

            # Now advance the story phase (triggers will validate this is allowed)
            story_id = delegation['story_id']
            to_phase = delegation['to_phase']

            conn.execute("""
                UPDATE stories
                SET phase = ?, current_agent = 'hub-agent'
                WHERE story_id = ?
            """, (to_phase, story_id))

            # Update lane status if using lanes
            lane_name = delegation['lane_name'] if delegation and delegation['lane_name'] else 'main'
            if lane_name and lane_name != 'main':
                conn.execute("""
                    UPDATE story_lanes
                    SET status = 'completed',
                        completed_at = datetime('now')
                    WHERE story_id = ? AND lane_name = ?
                """, (story_id, lane_name))

            conn.commit()

            return DelegationResult(
                success=True,
                txn_id=txn_id,
                message=f"Delegation {txn_id} completed. Story {story_id} now in [{to_phase}]"
            )

        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            # Log violation attempt
            conn.execute("""
                INSERT INTO audit_log (event_type, txn_id, details)
                VALUES ('violation_attempt', ?, ?)
            """, (txn_id, json.dumps({'error': error_msg})))
            conn.commit()
            return DelegationResult(success=False, error=error_msg)
        finally:
            conn.close()

    def hub_fail_delegation(self, txn_id: str, reason: str) -> DelegationResult:
        """Mark a delegation as failed."""
        conn = self._get_conn()
        try:
            # First get delegation details to update lane
            delegation = conn.execute("""
                SELECT story_id, lane_name FROM delegations WHERE txn_id = ?
            """, (txn_id,)).fetchone()

            # Update delegation status
            conn.execute("""
                UPDATE delegations
                SET status = 'failed',
                    completed_at = datetime('now'),
                    failure_reason = ?
                WHERE txn_id = ? AND status = 'pending'
            """, (reason, txn_id))

            if conn.total_changes == 0:
                return DelegationResult(
                    success=False,
                    error=f"Delegation {txn_id} not found or not pending"
                )

            # Update lane status if using lanes
            lane_name = delegation['lane_name'] if delegation and delegation['lane_name'] else 'main'
            if lane_name and lane_name != 'main':
                conn.execute("""
                    UPDATE story_lanes
                    SET status = 'failed',
                        completed_at = datetime('now'),
                        failure_reason = ?
                    WHERE story_id = ? AND lane_name = ?
                """, (reason, delegation['story_id'], lane_name))

            conn.commit()
            return DelegationResult(
                success=True,
                message=f"Delegation {txn_id} marked as failed: {reason}"
            )
        finally:
            conn.close()

    # ========================================================================
    # EVIDENCE VERIFICATION
    # ========================================================================

    def verify_agent_evidence(self, story_id: str,
                              agent: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify that an agent has left evidence in the story file.

        Returns: (found, evidence_hash, evidence_location)
        """
        # Get story file path
        conn = self._get_conn()
        try:
            row = conn.execute("""
                SELECT story_file_path FROM stories WHERE story_id = ?
            """, (story_id,)).fetchone()

            if not row:
                return False, None, None

            story_path = Path(row['story_file_path'])
        finally:
            conn.close()

        if not story_path.exists():
            # Try with stories directory prefix
            story_path = STORIES_DIR / f"{story_id}.md"

        if not story_path.exists():
            return False, None, None

        with open(story_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Define expected evidence sections per agent
        evidence_patterns = {
            'code-review-agent': r'###\s*Code Review\s*(Results)?.*?(?=\n##|\Z)',
            'testing-agent': r'###\s*Testing\s*(Results)?.*?(?=\n##|\Z)',
            'qa-agent': r'###\s*(QA|Quality Assurance)\s*(Results|Validation)?.*?(?=\n##|\Z)',
            'frontend-agent': r'###\s*Implementation\s*(Notes|Progress)?.*?(?=\n##|\Z)',
            'backend-agent': r'###\s*Implementation\s*(Notes|Progress)?.*?(?=\n##|\Z)',
            'frontend-unit-testing-agent': r'###\s*(Frontend\s*)?Unit\s*Test.*?(?=\n##|\Z)',
            'backend-unit-testing-agent': r'###\s*(Backend\s*)?Unit\s*Test.*?(?=\n##|\Z)',
        }

        pattern = evidence_patterns.get(agent)
        if not pattern:
            return False, None, None

        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if not match:
            return False, None, None

        evidence_text = match.group(0)
        evidence_hash = hashlib.sha256(evidence_text.encode()).hexdigest()[:16]
        evidence_location = evidence_text[:50].strip()

        return True, evidence_hash, evidence_location

    # ========================================================================
    # AUDIT & REPORTING
    # ========================================================================

    def get_audit_log(self, story_id: str = None,
                      limit: int = 50) -> List[Dict]:
        """Get audit log entries."""
        conn = self._get_conn()
        try:
            if story_id:
                rows = conn.execute("""
                    SELECT * FROM audit_log
                    WHERE story_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (story_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM audit_log
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_workflow_summary(self) -> Dict:
        """Get summary of current workflow state."""
        conn = self._get_conn()
        try:
            stories = conn.execute("""
                SELECT phase, COUNT(*) as count
                FROM stories
                GROUP BY phase
            """).fetchall()

            pending = conn.execute("""
                SELECT COUNT(*) as count FROM delegations WHERE status = 'pending'
            """).fetchone()

            completed_today = conn.execute("""
                SELECT COUNT(*) as count FROM delegations
                WHERE status = 'completed'
                AND date(completed_at) = date('now')
            """).fetchone()

            return {
                'stories_by_phase': {row['phase']: row['count'] for row in stories},
                'pending_delegations': pending['count'],
                'completed_today': completed_today['count']
            }
        finally:
            conn.close()

    # ========================================================================
    # CHECKPOINT FUNCTIONS
    # ========================================================================

    def create_checkpoint(self, story_id: str, phase: str,
                         context_data: dict = None) -> DelegationResult:
        """
        Create a context checkpoint for remediation restore.
        Call this when advancing [I] → [CR].

        Args:
            story_id: Story to checkpoint
            phase: Current phase ('I' or 'CR')
            context_data: Dict with loaded docs, versions, patterns
        """
        checkpoint_type = 'implementation' if phase == 'I' else 'code_review'

        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO story_checkpoints
                (story_id, phase, checkpoint_type, context_snapshot)
                VALUES (?, ?, ?, ?)
            """, (story_id, phase, checkpoint_type,
                  json.dumps(context_data) if context_data else None))
            conn.commit()

            return DelegationResult(
                success=True,
                message=f"Checkpoint created for {story_id} at [{phase}]"
            )
        finally:
            conn.close()

    def get_latest_checkpoint(self, story_id: str, phase: str = None) -> Optional[Dict]:
        """
        Get the most recent checkpoint for a story.

        Args:
            story_id: Story to get checkpoint for
            phase: Optional phase filter ('I' or 'CR')
        """
        conn = self._get_conn()
        try:
            if phase:
                row = conn.execute("""
                    SELECT * FROM story_checkpoints
                    WHERE story_id = ? AND phase = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (story_id, phase)).fetchone()
            else:
                row = conn.execute("""
                    SELECT * FROM story_checkpoints
                    WHERE story_id = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (story_id,)).fetchone()

            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    # ========================================================================
    # REMEDIATION HANDLING
    # ========================================================================

    def handle_phase_failure(self, story_id: str, failed_phase: str,
                             failure_reason: str) -> DelegationResult:
        """
        Generic handler for phase failures. Returns story to [I] for remediation.

        Args:
            story_id: Story that failed
            failed_phase: Phase where failure occurred ('CR', 'T', or 'Q')
            failure_reason: Description of what failed

        Returns:
            DelegationResult with success status and metadata
        """
        if failed_phase not in ('CR', 'T', 'Q'):
            return DelegationResult(
                success=False,
                error=f"Invalid failed_phase: {failed_phase}. Must be CR, T, or Q."
            )

        conn = self._get_conn()
        try:
            # 1. Get current story state
            story = conn.execute("""
                SELECT phase, attempt_count FROM stories WHERE story_id = ?
            """, (story_id,)).fetchone()

            if not story:
                return DelegationResult(success=False, error=f"Story {story_id} not found")

            if story['phase'] != failed_phase:
                return DelegationResult(
                    success=False,
                    error=f"Story {story_id} is in phase [{story['phase']}], not [{failed_phase}]"
                )

            # 2. Check attempt count - circuit breaker
            new_attempt_count = story['attempt_count'] + 1
            if new_attempt_count > 5:
                print(f"WARNING: Story {story_id} has failed {new_attempt_count} times")

            # 3. Get checkpoint from [I] phase if available
            checkpoint = self.get_latest_checkpoint(story_id, 'I')
            checkpoint_id = checkpoint['id'] if checkpoint else None

            # 4. Find and pause same-module dependents (only for T and Q failures)
            paused_ids = []
            if failed_phase in ('T', 'Q'):
                dependents = conn.execute("""
                    SELECT d.story_id
                    FROM story_dependencies d
                    JOIN stories s ON d.story_id = s.story_id
                    WHERE d.depends_on_story_id = ?
                      AND d.dependency_type = 'same_module'
                      AND s.phase NOT IN ('Done', 'Paused', 'Blocked')
                """, (story_id,)).fetchall()

                paused_ids = [d['story_id'] for d in dependents]

                for dep_id in paused_ids:
                    conn.execute("""
                        UPDATE stories SET phase = 'Paused', current_agent = NULL
                        WHERE story_id = ?
                    """, (dep_id,))

            # 5. Create remediation record
            conn.execute("""
                INSERT INTO remediations
                (story_id, failed_phase, failure_reason, returned_to_phase,
                 checkpoint_id, paused_dependents)
                VALUES (?, ?, ?, 'I', ?, ?)
            """, (story_id, failed_phase, failure_reason, checkpoint_id,
                  json.dumps(paused_ids) if paused_ids else None))

            # 6. Update story: revert to [I], increment attempt count
            conn.execute("""
                UPDATE stories
                SET phase = 'I',
                    current_agent = 'hub-agent',
                    attempt_count = ?,
                    last_failure_phase = ?,
                    last_failure_at = datetime('now')
                WHERE story_id = ?
            """, (new_attempt_count, failed_phase, story_id))

            conn.commit()

            return DelegationResult(
                success=True,
                message=f"Story {story_id} reverted from [{failed_phase}] to [I]. Attempt #{new_attempt_count}",
                metadata={
                    'attempt_count': new_attempt_count,
                    'paused_stories': paused_ids,
                    'checkpoint_id': checkpoint_id,
                    'failed_phase': failed_phase
                }
            )

        except Exception as e:
            conn.rollback()
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()

    def handle_test_failure(self, story_id: str, failure_reason: str) -> DelegationResult:
        """
        Handle test failure: return to [I], pause same-module dependents.
        Wrapper around handle_phase_failure() for backward compatibility.
        """
        return self.handle_phase_failure(story_id, 'T', failure_reason)

    def handle_code_review_failure(self, story_id: str, failure_reason: str) -> DelegationResult:
        """Handle code review failure: return to [I] for fixes."""
        return self.handle_phase_failure(story_id, 'CR', failure_reason)

    def handle_qa_rejection(self, story_id: str, failure_reason: str) -> DelegationResult:
        """Handle QA rejection: return to [I] for fixes."""
        return self.handle_phase_failure(story_id, 'Q', failure_reason)

    def resolve_remediation(self, story_id: str, notes: str = None) -> DelegationResult:
        """Mark remediation as resolved and resume paused dependents."""
        conn = self._get_conn()
        try:
            # Get active remediation
            remediation = conn.execute("""
                SELECT id, paused_dependents FROM remediations
                WHERE story_id = ? AND resolved_at IS NULL
                ORDER BY started_at DESC LIMIT 1
            """, (story_id,)).fetchone()

            if not remediation:
                return DelegationResult(
                    success=False,
                    error=f"No active remediation found for {story_id}"
                )

            # Mark remediation as resolved
            conn.execute("""
                UPDATE remediations
                SET resolved_at = datetime('now'),
                    resolution_notes = ?
                WHERE id = ?
            """, (notes, remediation['id']))

            # Resume paused dependents
            paused_ids = json.loads(remediation['paused_dependents']) if remediation['paused_dependents'] else []
            for dep_id in paused_ids:
                conn.execute("""
                    UPDATE stories SET phase = 'Pending'
                    WHERE story_id = ? AND phase = 'Paused'
                """, (dep_id,))

            conn.commit()

            return DelegationResult(
                success=True,
                message=f"Remediation resolved. Resumed stories: {paused_ids}"
            )

        except Exception as e:
            conn.rollback()
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()

    def get_story_health(self, story_id: str) -> Optional[Dict]:
        """Get health status for a story."""
        conn = self._get_conn()
        try:
            row = conn.execute("""
                SELECT * FROM story_health WHERE story_id = ?
            """, (story_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_stuck_stories(self) -> List[Dict]:
        """Get all stories that have failed multiple times."""
        conn = self._get_conn()
        try:
            rows = conn.execute("""
                SELECT * FROM story_health
                WHERE health_status != 'HEALTHY'
                ORDER BY attempt_count DESC
            """).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    # ========================================================================
    # LANE MANAGEMENT FUNCTIONS
    # ========================================================================

    def get_story_lanes(self, story_id: str) -> List[Dict]:
        """Get all lanes for a story."""
        conn = self._get_conn()
        try:
            rows = conn.execute("""
                SELECT * FROM story_lane_status WHERE story_id = ?
            """, (story_id,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def check_lanes_complete(self, story_id: str) -> bool:
        """
        Check if all lanes for a story are completed.
        Returns True if story can advance to next phase.
        """
        conn = self._get_conn()
        try:
            result = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM story_lanes
                WHERE story_id = ?
            """, (story_id,)).fetchone()

            # If no lanes, story isn't using lane system
            if result['total'] == 0:
                return True

            # All lanes must be completed
            return result['total'] == result['completed']

        finally:
            conn.close()

    def get_failed_lanes(self, story_id: str) -> List[Dict]:
        """Get lanes that have failed for a story."""
        conn = self._get_conn()
        try:
            rows = conn.execute("""
                SELECT lane_name, agent, failure_reason, started_at
                FROM story_lanes
                WHERE story_id = ? AND status = 'failed'
            """, (story_id,)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    # ========================================================================
    # CONTEXT LEARNING SYSTEM
    # ========================================================================

    def record_story_completion(self, story_id: str) -> DelegationResult:
        """
        Record story completion and check if reflector should trigger.

        Returns: DelegationResult with metadata.should_trigger_reflector = True if count reaches threshold
        """
        conn = self._get_conn()
        try:
            # Increment counter
            conn.execute("""
                UPDATE learning_metrics
                SET completed_stories = completed_stories + 1,
                    updated_at = datetime('now')
                WHERE id = 1
            """)

            # Get current count and threshold
            metrics = conn.execute("""
                SELECT completed_stories, next_reflector_at, last_reflector_batch
                FROM learning_metrics WHERE id = 1
            """).fetchone()

            completed = metrics['completed_stories']
            trigger_at = metrics['next_reflector_at']
            last_batch = metrics['last_reflector_batch']

            should_trigger = (completed >= trigger_at)

            if should_trigger:
                # Update for next trigger
                next_batch = last_batch + 1
                conn.execute("""
                    UPDATE learning_metrics
                    SET last_reflector_batch = ?,
                        next_reflector_at = next_reflector_at + 10,
                        last_reflector_run = datetime('now')
                    WHERE id = 1
                """, (next_batch,))

                conn.commit()

                return DelegationResult(
                    success=True,
                    message=f"Story {story_id} completion recorded ({completed} total) - TRIGGER REFLECTOR",
                    metadata={
                        'should_trigger_reflector': True,
                        'batch_number': next_batch,
                        'completed_count': completed,
                        'story_range_start': completed - 9,
                        'story_range_end': completed
                    }
                )
            else:
                conn.commit()
                return DelegationResult(
                    success=True,
                    message=f"Story {story_id} completion recorded ({completed}/{trigger_at})",
                    metadata={
                        'should_trigger_reflector': False,
                        'completed_count': completed,
                        'next_trigger_at': trigger_at
                    }
                )
        except Exception as e:
            conn.rollback()
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()

    def parse_context_feedback(self, story_id: str) -> Optional[Dict]:
        """
        Extract Context Feedback section from story file and parse it.

        Returns: {
            'helpful': ['doc-name-1', 'doc-name-2'],
            'misleading': [{'doc': 'doc-name', 'reason': 'explanation'}],
            'missing': ['pattern 1', 'pattern 2']
        }
        """
        from pathlib import Path
        import re

        story_file = Path('stories') / f"{story_id}.md"
        if not story_file.exists():
            return None

        content = story_file.read_text()

        # Extract Context Feedback section
        feedback_match = re.search(
            r'## Context Feedback\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if not feedback_match:
            return None

        feedback_text = feedback_match.group(1)

        # Parse helpful docs
        helpful_match = re.search(r'\*\*Helpful\*\*:\s*([^\n]+)', feedback_text)
        helpful = []
        if helpful_match:
            helpful = [d.strip() for d in helpful_match.group(1).split(',') if d.strip() and d.strip().lower() != 'none']

        # Parse misleading docs (with reasons)
        misleading_match = re.search(r'\*\*Misleading\*\*:\s*([^\n]+)', feedback_text)
        misleading = []
        if misleading_match:
            misleading_text = misleading_match.group(1).strip()
            if misleading_text.lower() != 'none':
                for item in misleading_text.split(','):
                    item = item.strip()
                    if '(' in item and ')' in item:
                        doc_name, reason = item.split('(', 1)
                        misleading.append({
                            'doc': doc_name.strip(),
                            'reason': reason.rstrip(')').strip()
                        })
                    elif item:
                        misleading.append({'doc': item, 'reason': 'no reason given'})

        # Parse missing patterns
        missing_match = re.search(r'\*\*Missing\*\*:\s*\n(.*?)(?=\n\*\*|\Z)', feedback_text, re.DOTALL)
        missing = []
        if missing_match:
            for line in missing_match.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    pattern = line[2:].strip()
                    if pattern.lower() != 'none':
                        missing.append(pattern)
                elif line and line.lower() != 'none':
                    missing.append(line)

        return {
            'helpful': helpful,
            'misleading': misleading,
            'missing': missing
        }

    def store_context_feedback(self, story_id: str, agent: str) -> DelegationResult:
        """
        Parse and store context feedback from story file.
        Called by Hub after agent completion.
        """
        import json

        feedback = self.parse_context_feedback(story_id)

        if not feedback:
            return DelegationResult(
                success=False,
                error=f"No Context Feedback section found in {story_id}"
            )

        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO context_feedback
                (story_id, agent, helpful_docs, misleading_docs, missing_patterns)
                VALUES (?, ?, ?, ?, ?)
            """, (
                story_id,
                agent,
                json.dumps(feedback['helpful']),
                json.dumps(feedback['misleading']),
                json.dumps(feedback['missing'])
            ))
            conn.commit()

            return DelegationResult(
                success=True,
                message=f"Context feedback stored for {story_id}",
                metadata=feedback
            )
        except Exception as e:
            conn.rollback()
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()

    def parse_issues_encountered(self, story_id: str) -> Optional[List[Dict]]:
        """
        Extract Issues Encountered section from story file and parse it.

        Returns: List of {
            'title': 'Issue title',
            'problem': 'Problem description',
            'solution': 'Solution applied',
            'prevention': 'How to prevent'
        }
        """
        from pathlib import Path
        import re

        story_file = Path('stories') / f"{story_id}.md"
        if not story_file.exists():
            return None

        content = story_file.read_text()

        # Extract Issues Encountered section
        issues_match = re.search(
            r'## Issues Encountered\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL
        )

        if not issues_match:
            return []  # Section exists but empty is okay

        issues_text = issues_match.group(1).strip()

        if not issues_text or issues_text.lower() == 'none':
            return []

        issues = []

        # Parse individual issues (format: **Title**\n- Problem:...\n- Solution:...\n- Prevention:...)
        issue_blocks = re.split(r'\n\*\*([^*]+)\*\*\n', issues_text)

        for i in range(1, len(issue_blocks), 2):
            if i + 1 < len(issue_blocks):
                title = issue_blocks[i].strip()
                content_block = issue_blocks[i + 1]

                # Extract problem, solution, prevention
                problem_match = re.search(r'- Problem:\s*(.+?)(?=\n-|\Z)', content_block, re.DOTALL)
                solution_match = re.search(r'- Solution:\s*(.+?)(?=\n-|\Z)', content_block, re.DOTALL)
                prevention_match = re.search(r'- Prevention:\s*(.+?)(?=\n-|\Z)', content_block, re.DOTALL)

                if problem_match and solution_match:
                    issues.append({
                        'title': title,
                        'problem': problem_match.group(1).strip(),
                        'solution': solution_match.group(1).strip(),
                        'prevention': prevention_match.group(1).strip() if prevention_match else ''
                    })

        return issues

    def store_issues_encountered(self, story_id: str, agent: str) -> DelegationResult:
        """
        Parse and store issues encountered from story file.
        Called by Hub after agent completion.
        """
        issues = self.parse_issues_encountered(story_id)

        if issues is None:
            return DelegationResult(
                success=True,
                message=f"No Issues Encountered section in {story_id} (optional)"
            )

        if not issues:
            return DelegationResult(
                success=True,
                message=f"No issues documented in {story_id} (that's fine)"
            )

        conn = self._get_conn()
        try:
            for issue in issues:
                conn.execute("""
                    INSERT INTO issues_encountered
                    (story_id, agent, issue_title, problem, solution, prevention)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    story_id,
                    agent,
                    issue['title'],
                    issue['problem'],
                    issue['solution'],
                    issue['prevention']
                ))
            conn.commit()

            return DelegationResult(
                success=True,
                message=f"{len(issues)} issues stored for {story_id}",
                metadata={'issue_count': len(issues)}
            )
        except Exception as e:
            conn.rollback()
            return DelegationResult(success=False, error=str(e))
        finally:
            conn.close()


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for workflow engine."""
    import sys

    engine = WorkflowEngine()

    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "status":
        stories = engine.get_all_stories()
        print("\n=== Story Status ===\n")
        for s in stories:
            print(f"  {s['story_id']}: [{s['phase']}] - {s['title']}")
            print(f"    Agent: {s['current_agent'] or 'hub'}, Pending: {s['pending_delegations']}")
        print()

    elif command == "next":
        actions = engine.hub_get_all_next_actions()
        print("\n=== Next Actions ===\n")
        for a in actions:
            print(f"  {a.story_id}: [{a.current_phase}] -> [{a.next_phase}]")
            print(f"    Agent: {a.next_agent}")
            print(f"    Status: {a.readiness}")
        print()

    elif command == "pending":
        pending = engine.hub_get_pending_delegations()
        print("\n=== Pending Delegations ===\n")
        if not pending:
            print("  No pending delegations")
        for p in pending:
            print(f"  {p.txn_id}")
            print(f"    Story: {p.story_id} ({p.story_title})")
            print(f"    Agent: {p.agent}")
            print(f"    Age: {p.age_minutes:.1f} minutes")
        print()

    elif command == "summary":
        summary = engine.get_workflow_summary()
        print("\n=== Workflow Summary ===\n")
        print("Stories by phase:")
        for phase, count in summary['stories_by_phase'].items():
            print(f"  [{phase}]: {count}")
        print(f"\nPending delegations: {summary['pending_delegations']}")
        print(f"Completed today: {summary['completed_today']}")
        print()

    elif command == "audit":
        story_id = sys.argv[2] if len(sys.argv) > 2 else None
        entries = engine.get_audit_log(story_id, limit=20)
        print("\n=== Audit Log ===\n")
        for e in entries:
            print(f"  [{e['timestamp']}] {e['event_type']}")
            print(f"    Story: {e['story_id']}, Agent: {e['agent_id']}")
            if e['details']:
                print(f"    Details: {e['details']}")
        print()

    elif command == "init":
        # Re-initialize database
        if engine.db_path.exists():
            engine.db_path.unlink()
        engine._init_schema()
        print("Database re-initialized")

    elif command == "register":
        if len(sys.argv) < 4:
            print("Usage: workflow_engine.py register <story_id> <title>")
            return
        story_id = sys.argv[2]
        title = sys.argv[3]
        result = engine.register_story(story_id, title, f"stories/{story_id}.md")
        print(result.message if result.success else f"Error: {result.error}")

    elif command == "lanes":
        # Show lane status for a story
        if len(sys.argv) < 3:
            print("Usage: workflow_engine.py lanes <story_id>")
            return

        story_id = sys.argv[2]
        lanes = engine.get_story_lanes(story_id)

        print(f"\n=== Lanes for {story_id} ===\n")
        if not lanes:
            print("  No lanes (story not using parallel execution)")
        else:
            for lane in lanes:
                status_icon = {
                    'active': '[>]',
                    'completed': '[OK]',
                    'failed': '[X]',
                    'paused': '[||]'
                }.get(lane['status'], '[?]')

                print(f"  {status_icon} {lane['lane_name']:<12} {lane['agent']:<30} {lane['status']:<10}")
                if lane['failure_reason']:
                    print(f"     Reason: {lane['failure_reason']}")
                print(f"     Active: {lane['hours_active']:.1f} hours")
        print()

    elif command == "health":
        # Check for stale lanes
        conn = engine._get_conn()
        try:
            stale = conn.execute("""
                SELECT story_id, lane_name, agent, hours_active
                FROM story_lane_status
                WHERE status = 'active' AND hours_active > 2
            """).fetchall()

            print("\n=== Health Check ===\n")
            if not stale:
                print("  [OK] All lanes healthy")
            else:
                print(f"  [!]  {len(stale)} stale lane(s) detected:\n")
                for s in stale:
                    print(f"     {s['story_id']}/{s['lane_name']}: {s['agent']}")
                    print(f"     Active for {s['hours_active']:.1f} hours - likely stuck\n")
            print()
        finally:
            conn.close()

    elif command == "dependencies":
        # Show dependencies for a story
        if len(sys.argv) < 3:
            print("Usage: workflow_engine.py dependencies <story_id>")
            return

        story_id = sys.argv[2]
        conn = engine._get_conn()
        try:
            blockers = conn.execute("""
                SELECT * FROM story_blockers WHERE blocked_story_id = ?
            """, (story_id,)).fetchall()

            print(f"\n=== Dependencies for {story_id} ===\n")
            if not blockers:
                print("  No dependencies")
            else:
                for b in blockers:
                    status_icon = '[OK]' if b['block_status'] == 'UNBLOCKED' else '[X]'
                    print(f"  {status_icon} {b['blocker_story_id']} ({b['dependency_type']})")
                    print(f"     Status: {b['blocker_phase']} - {b['block_status']}")
                    if b['reason']:
                        print(f"     Reason: {b['reason']}")
            print()
        finally:
            conn.close()

    elif command == "add-dependency":
        # Add dependency between stories
        if len(sys.argv) < 5:
            print("Usage: workflow_engine.py add-dependency <story_id> <depends_on> <type> [reason]")
            print("Types: explicit, same_module, different_module")
            return

        story_id = sys.argv[2]
        depends_on = sys.argv[3]
        dep_type = sys.argv[4]
        reason = sys.argv[5] if len(sys.argv) > 5 else None

        result = engine.add_dependency(story_id, depends_on, dep_type, reason)
        if result.success:
            print(f"[OK] {result.message}")
        else:
            print(f"[ERROR] {result.error}")

    elif command == "checkpoint":
        # Show checkpoints for a story
        if len(sys.argv) < 3:
            print("Usage: workflow_engine.py checkpoint <story_id>")
            return

        story_id = sys.argv[2]
        checkpoint = engine.get_latest_checkpoint(story_id)

        print(f"\n=== Latest Checkpoint for {story_id} ===\n")
        if not checkpoint:
            print("  No checkpoints found")
        else:
            print(f"  Phase: [{checkpoint['phase']}]")
            print(f"  Type: {checkpoint['checkpoint_type']}")
            print(f"  Created: {checkpoint['created_at']}")
            if checkpoint['context_snapshot']:
                print(f"  Context: {checkpoint['context_snapshot'][:100]}...")
        print()

    elif command == "learning_metrics":
        # Show learning system status
        conn = engine._get_conn()
        metrics = conn.execute("SELECT * FROM learning_metrics WHERE id = 1").fetchone()
        conn.close()

        print("\n" + "="*50)
        print("CONTEXT LEARNING METRICS")
        print("="*50)
        print(f"Completed Stories: {metrics['completed_stories']}")
        print(f"Next Reflector At: {metrics['next_reflector_at']} stories")
        print(f"Last Reflector Run: {metrics['last_reflector_run'] or 'Never'}")
        print(f"Total Batches: {metrics['last_reflector_batch']}")
        print(f"Deltas Proposed: {metrics['total_deltas_proposed']}")
        print(f"Deltas Approved: {metrics['total_deltas_approved']}")
        print("="*50 + "\n")

    elif command == "feedback":
        # View feedback for a specific story
        if len(sys.argv) < 3:
            print("Usage: workflow_engine.py feedback <story_id>")
            sys.exit(1)

        feedback = engine.parse_context_feedback(sys.argv[2])

        if feedback:
            print(f"\nContext Feedback for {sys.argv[2]}:")
            print(f"Helpful: {', '.join(feedback['helpful']) if feedback['helpful'] else 'None'}")
            print(f"Misleading: {len(feedback['misleading'])} doc(s)")
            for item in feedback['misleading']:
                print(f"  - {item['doc']}: {item['reason']}")
            print(f"Missing: {len(feedback['missing'])} pattern(s)")
            for pattern in feedback['missing']:
                print(f"  - {pattern}")
        else:
            print(f"No feedback found for {sys.argv[2]}")

    else:
        print_usage()

def print_usage():
    print("""
RX.CE-Framework Workflow Engine

Usage:
    workflow_engine.py status                                - Show all story statuses
    workflow_engine.py next                                  - Show next actions for all stories
    workflow_engine.py pending                               - Show pending delegations
    workflow_engine.py summary                               - Show workflow summary
    workflow_engine.py audit [story_id]                      - Show audit log
    workflow_engine.py register <id> <title>                 - Register new story
    workflow_engine.py lanes <story_id>                      - Show lane status for a story
    workflow_engine.py health                                - Check for stale/stuck lanes
    workflow_engine.py dependencies <story_id>               - Show dependencies blocking a story
    workflow_engine.py add-dependency <story> <blocker> <type> [reason]
                                                             - Add dependency (types: explicit, same_module, different_module)
    workflow_engine.py checkpoint <story_id>                 - Show latest checkpoint for a story
    workflow_engine.py learning_metrics                      - Show context learning system metrics
    workflow_engine.py feedback <story_id>                   - View context feedback for a story
    workflow_engine.py init                                  - Re-initialize database
    """)

if __name__ == "__main__":
    main()
