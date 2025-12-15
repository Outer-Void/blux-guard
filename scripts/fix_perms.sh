#!/usr/bin/env bash
# Normalize executable permissions using the tracked manifest.
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$SCRIPT_DIR/perms_manifest.txt"

usage() {
    cat <<'EOF'
Usage: fix_perms.sh [--check]

Ensures all executable scripts listed in scripts/perms_manifest.txt have
the correct executable bit set. Use --check to run in dry-run mode.
EOF
}

check_only=false
if [ "${1:-}" = "--check" ]; then
    check_only=true
elif [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

if [ ! -f "$MANIFEST" ]; then
    echo "Manifest not found: $MANIFEST" >&2
    exit 1
fi

missing=0
needs_fix=0

while IFS= read -r entry; do
    # Skip blanks and comments
    [ -z "$entry" ] && continue
    case "$entry" in
        \#*) continue ;;
    esac

    target="$REPO_ROOT/$entry"

    if [ ! -e "$target" ]; then
        echo "Missing: $entry" >&2
        missing=$((missing + 1))
        continue
    fi

    if [ -x "$target" ]; then
        continue
    fi

    needs_fix=$((needs_fix + 1))
    if [ "$check_only" = true ]; then
        echo "Not executable: $entry"
    else
        chmod +x "$target"
        echo "Fixed permissions: $entry"
    fi
done < "$MANIFEST"

if [ "$check_only" = true ]; then
    if [ "$missing" -ne 0 ] || [ "$needs_fix" -ne 0 ]; then
        exit 1
    fi
    echo "All manifest entries have executable permissions."
else
    echo "Permission normalization complete."
fi
