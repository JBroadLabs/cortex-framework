#!/bin/bash
# Analyze dependencies in CONTEXT ENGINEERING framework

echo "=== Dependency Analysis ==="
echo ""

if [ ! -d "stories" ]; then
    echo "No stories directory found"
    exit 1
fi

# Extract all dependencies
> /tmp/ce_deps.txt
for story in stories/*.md; do
    if [ -f "$story" ]; then
        name=$(basename "$story" .md)
        awk '/^dependencies:/,/^[a-z]/' "$story" | \
            grep -E "^  - story-" | \
            sed 's/^  - //' | sed 's/:.*$//' | \
            while read -r dep; do
                echo "$name -> $dep" >> /tmp/ce_deps.txt
            done
    fi
done

# Statistics
total_deps=$(wc -l < /tmp/ce_deps.txt)
echo "Total Dependencies: $total_deps"
echo ""

# Most referenced
echo "Most Referenced Stories:"
cut -d' ' -f3 /tmp/ce_deps.txt | sort | uniq -c | sort -rn | head -5 | \
    while read -r count story; do
        echo "  $count times: $story"
    done
echo ""

# Check circular dependencies
echo "Circular Dependencies:"
found=false
while read -r line; do
    a=$(echo "$line" | cut -d' ' -f1)
    b=$(echo "$line" | cut -d' ' -f3)
    if grep -q "^$b -> $a$" /tmp/ce_deps.txt; then
        echo "  ⚠️  $a ↔ $b"
        found=true
    fi
done < /tmp/ce_deps.txt
[ "$found" = false ] && echo "  ✅ None detected"
echo ""

# Check missing targets
echo "Missing Targets:"
found=false
cut -d' ' -f3 /tmp/ce_deps.txt | sort -u | while read -r dep; do
    if [ ! -f "stories/${dep}.md" ]; then
        echo "  ❌ $dep"
        found=true
    fi
done
[ "$found" = false ] && echo "  ✅ All targets exist"

rm -f /tmp/ce_deps.txt