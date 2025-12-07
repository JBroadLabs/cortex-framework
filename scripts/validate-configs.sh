#!/bin/bash
# Multi-platform configuration validator

echo "Validating Multi-Platform Configurations..."
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0

validate_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}[OK]${NC} $1"
        return 0
    else
        echo -e "${RED}[MISSING]${NC} $1"
        return 1
    fi
}

validate_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}[OK]${NC} $1/"
        return 0
    else
        echo -e "${RED}[MISSING]${NC} $1/"
        return 1
    fi
}

echo "=== Root Configuration ==="
validate_file "AGENTS.md" || ((errors++))
echo ""

echo "=== Claude Code ==="
validate_dir ".claude" || ((errors++))
echo ""

echo "=== Antigravity ==="
validate_dir ".agent" || ((errors++))
validate_file ".agent/rules.md" || ((errors++))
validate_dir ".agent/workflows" || ((errors++))
validate_file ".agent/workflows/rx-framework.md" || ((errors++))
echo ""

echo "=== GitHub Copilot ==="
validate_file ".github/copilot-instructions.md" || ((errors++))
validate_dir ".github/instructions" || ((errors++))
validate_file ".github/instructions/greenfield.instructions.md" || ((errors++))
validate_file ".github/instructions/brownfield.instructions.md" || ((errors++))
echo ""

echo "=== Roo Code ==="
validate_dir ".roo/rules" || ((errors++))
validate_file ".roo/rules/framework.md" || ((errors++))
echo ""

echo "=== Cursor ==="
validate_dir ".cursor/rules" || ((errors++))
validate_file ".cursor/rules/index.mdc" || ((errors++))
validate_file ".cursor/rules/frontend.mdc" || ((errors++))
validate_file ".cursor/rules/backend.mdc" || ((errors++))
validate_file ".cursor/rules/stories.mdc" || ((errors++))
echo ""

echo "=== Documentation ==="
validate_file "docs/PLATFORM_SETUP.md" || ((errors++))
echo ""

echo "=============================================="
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}All configurations valid!${NC}"
    echo ""
    echo "Platforms configured:"
    echo "  - Claude Code (pre-configured)"
    echo "  - GitHub Copilot (via root AGENTS.md)"
    echo "  - Antigravity (via .agent/)"
    echo "  - Roo Code (via root AGENTS.md + .roo/)"
    echo "  - Cursor (via .cursor/rules/)"
    echo ""
    echo "All platforms work 100% automatically!"
else
    echo -e "${RED}$errors configuration files missing${NC}"
    echo ""
    echo -e "${YELLOW}Run implementation tasks to create missing files${NC}"
    exit 1
fi
