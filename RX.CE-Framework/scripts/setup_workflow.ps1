# Setup script for SQLite workflow state machine
# PowerShell version for Windows

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$FRAMEWORK_DIR = Split-Path -Parent $SCRIPT_DIR
$ROOT_DIR = Split-Path -Parent $FRAMEWORK_DIR

Write-Host "=== Setting up RX.CE-Framework Workflow State Machine ===" -ForegroundColor Cyan
Write-Host ""

# Create state directory
$STATE_DIR = Join-Path $FRAMEWORK_DIR "state"
if (-not (Test-Path $STATE_DIR)) {
    New-Item -ItemType Directory -Path $STATE_DIR | Out-Null
}

# Check for schema file
$SCHEMA_FILE = Join-Path $FRAMEWORK_DIR "state\schema.sql"
if (-not (Test-Path $SCHEMA_FILE)) {
    Write-Host "❌ Schema file not found: $SCHEMA_FILE" -ForegroundColor Red
    Write-Host "   Please create the schema file first."
    exit 1
}

# Initialize database
$DB_FILE = Join-Path $FRAMEWORK_DIR "state\workflow.db"
if (Test-Path $DB_FILE) {
    Write-Host "⚠️  Database already exists: $DB_FILE" -ForegroundColor Yellow
    $reply = Read-Host "   Reinitialize? (y/N)"
    if ($reply -match "^[Yy]$") {
        Remove-Item $DB_FILE
        Write-Host "   Removed existing database"
    } else {
        Write-Host "   Keeping existing database"
        exit 0
    }
}

# Check if sqlite3 is available
$sqlite3 = Get-Command sqlite3 -ErrorAction SilentlyContinue
if (-not $sqlite3) {
    Write-Host "❌ sqlite3 not found in PATH" -ForegroundColor Red
    Write-Host "   Please install SQLite3 from https://www.sqlite.org/download.html"
    Write-Host "   Or use Python to initialize: python scripts/workflow_engine.py init"
    exit 1
}

# Create database
Write-Host "Creating database..."
Get-Content $SCHEMA_FILE | sqlite3 $DB_FILE
Write-Host "✅ Database created: $DB_FILE" -ForegroundColor Green

# Verify tables
Write-Host ""
Write-Host "Verifying tables..."
$tables = sqlite3 $DB_FILE ".tables"
Write-Host "   Tables: $tables"

Write-Host "✅ Workflow engine ready" -ForegroundColor Green

# Scan for existing stories and register them
Write-Host ""
Write-Host "Scanning for existing stories..."
$STORIES_DIR = Join-Path $ROOT_DIR "stories"
if (Test-Path $STORIES_DIR) {
    $storyFiles = Get-ChildItem -Path $STORIES_DIR -Filter "story-*.md"
    foreach ($storyFile in $storyFiles) {
        $story_id = $storyFile.BaseName

        # Extract title from first heading
        $content = Get-Content $storyFile.FullName -First 5
        $titleLine = $content | Where-Object { $_ -match "^#" } | Select-Object -First 1
        if ($titleLine) {
            $title = ($titleLine -replace "^#+\s*", "").Substring(0, [Math]::Min(100, ($titleLine -replace "^#+\s*", "").Length))
        } else {
            $title = $story_id
        }

        # Register in database
        try {
            python3 "$FRAMEWORK_DIR\scripts\workflow_engine.py" register $story_id $title 2>$null
            Write-Host "   Registered: $story_id"
        } catch {
            # Ignore errors (story might already exist)
        }
    }
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start:"
Write-Host "  python3 RX.CE-Framework/scripts/workflow_engine.py status   # View story status"
Write-Host "  python3 RX.CE-Framework/scripts/workflow_engine.py next     # See next actions"
Write-Host "  python3 RX.CE-Framework/scripts/workflow_engine.py pending  # Check pending delegations"
Write-Host ""
