#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(git rev-parse --show-toplevel)
cd "$repo_dir"

python scripts/physics_no_root.py

schema_names=(
  "request_envelope.schema.json"
  "discernment_report.schema.json"
)

base_ref=${GITHUB_BASE_REF:-main}
if git show-ref --verify --quiet "refs/remotes/origin/$base_ref"; then
  base_commit=$(git merge-base "origin/$base_ref" HEAD)
else
  base_commit=$(git rev-parse HEAD~1 2>/dev/null || echo "")
fi

if [ -n "$base_commit" ]; then
  changed=$(git diff --name-only "$base_commit"...HEAD)
  for name in "${schema_names[@]}"; do
    if printf '%s\n' "$changed" | rg -n --fixed-strings -- "$name" >/dev/null; then
      echo "Blocked: Phase 0 schema change detected: $name"
      exit 1
    fi
  done
fi
