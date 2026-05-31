#!/bin/bash
# Setup script for SQLite workflow state machine

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$FRAMEWORK_DIR")"

echo "=== Setting up Cortex-Framework Workflow State Machine ==="
echo ""

# Create state directory
mkdir -p "$FRAMEWORK_DIR/state"

# Check for schema file
SCHEMA_FILE="$FRAMEWORK_DIR/state/schema.sql"
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Schema file not found: $SCHEMA_FILE"
    echo "   Please create the schema file first."
    exit 1
fi

# Initialize database
DB_FILE="$FRAMEWORK_DIR/state/workflow.db"
if [ -f "$DB_FILE" ]; then
    echo "⚠️  Database already exists: $DB_FILE"
    read -p "   Reinitialize? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$DB_FILE"
        echo "   Removed existing database"
    else
        echo "   Keeping existing database"
        exit 0
    fi
fi

# Create database
echo "Creating database..."
sqlite3 "$DB_FILE" < "$SCHEMA_FILE"
echo "✅ Database created: $DB_FILE"

# Verify tables
echo ""
echo "Verifying tables..."
TABLES=$(sqlite3 "$DB_FILE" ".tables")
echo "   Tables: $TABLES"

# Make workflow engine executable
chmod +x "$FRAMEWORK_DIR/scripts/workflow_engine.py"
echo "✅ Workflow engine ready"

# Scan for existing stories and register them
echo ""
echo "Scanning for existing stories..."
STORIES_DIR="$ROOT_DIR/stories"
if [ -d "$STORIES_DIR" ]; then
    for story_file in "$STORIES_DIR"/story-*.md; do
        if [ -f "$story_file" ]; then
            story_id=$(basename "$story_file" .md)
            # Extract title from first heading
            title=$(head -5 "$story_file" | grep -m1 "^#" | sed 's/^#\+ //' | head -c 100)
            if [ -z "$title" ]; then
                title="$story_id"
            fi

            # Register in database
            python3 "$FRAMEWORK_DIR/scripts/workflow_engine.py" register "$story_id" "$title" 2>/dev/null || true
            echo "   Registered: $story_id"
        fi
    done
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Quick start:"
echo "  python3 Cortex-Framework/scripts/workflow_engine.py status   # View story status"
echo "  python3 Cortex-Framework/scripts/workflow_engine.py next     # See next actions"
echo "  python3 Cortex-Framework/scripts/workflow_engine.py pending  # Check pending delegations"
echo ""
