#!/bin/bash
echo "🔍 Verifying Repomix installation and functionality..."
echo ""

# Check if node/npm is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi
echo "✅ npm found: $(npm --version)"

# Check if Repomix is installed
if ! command -v repomix &> /dev/null; then
    echo "📦 Repomix not installed, installing now..."
    npm install -g repomix
fi

if command -v repomix &> /dev/null; then
    echo "✅ Repomix is ready"
    echo "   Location: $(which repomix)"
    echo "   Version: $(repomix --version 2>/dev/null || echo 'version check not available')"
    echo ""
    echo "✨ You can now use the /refactor and /story commands!"
    echo ""
    echo "Example usage:"
    echo "  claude code hub '/refactor modernize authentication'"
    echo "  repomix --style markdown --output test.md"
else
    echo "❌ Repomix installation failed"
    echo "Try manual installation:"
    echo "  npm install -g repomix"
    exit 1
fi
