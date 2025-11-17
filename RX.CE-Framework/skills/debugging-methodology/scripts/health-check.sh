#!/bin/bash
# Quick health check for CONTEXT ENGINEERING framework

echo "=== Framework Health Check ==="
echo ""

# Check core structure
echo "Core Structure:"
for dir in RX.CE-Framework docs stories .claude/commands; do
    [ -d "$dir" ] && echo "  ✅ $dir/" || echo "  ❌ $dir/ MISSING"
done
echo ""

# Check core docs
echo "Core Documents:"
for doc in docs/system-design.md docs/frontend-spec.md docs/backend-spec.md; do
    if [ -f "$doc" ]; then
        size=$(wc -c < "$doc")
        [ "$size" -gt 100 ] && echo "  ✅ $doc" || echo "  ⚠️  $doc (small)"
    else
        echo "  ⚠️  $doc (missing)"
    fi
done
echo ""

# Check tracker
echo "State Tracker:"
if [ -f "RX.CE-Framework/state/story_tracker.json" ]; then
    if python3 -c "import json; json.load(open('RX.CE-Framework/state/story_tracker.json'))" 2>/dev/null; then
        echo "  ✅ Valid tracker"
        story=$(grep -o '"current_story": "[^"]*"' RX.CE-Framework/state/story_tracker.json | cut -d'"' -f4)
        phase=$(grep -o '"phase": "[^"]*"' RX.CE-Framework/state/story_tracker.json | cut -d'"' -f4)
        echo "  Current: $story @ $phase"
    else
        echo "  ❌ Invalid JSON"
    fi
else
    echo "  ❌ Tracker missing"
fi
echo ""

# Check stories
echo "Story Status:"
if [ -d "stories" ] && [ "$(ls -A stories/*.md 2>/dev/null)" ]; then
    total=$(ls stories/*.md 2>/dev/null | wc -l)
    blocked=$(grep -l "status: blocked" stories/*.md 2>/dev/null | wc -l)
    echo "  Total: $total"
    echo "  Blocked: $blocked"
    [ "$blocked" -gt 0 ] && echo "  ⚠️  Some stories blocked!"
else
    echo "  No stories found"
fi