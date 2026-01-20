#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(git rev-parse --show-toplevel)
cd "$repo_dir"

make_pattern() {
  printf '%b' "$1"
}

pattern_a=$(make_pattern '\x73\x75\x64\x6f')
pattern_b=$(make_pattern '\x73\x75\x20')
pattern_c=$(make_pattern '\x73\x65\x74\x75\x69\x64')
pattern_d=$(make_pattern '\x70\x6b\x65\x78\x65\x63')
pattern_e=$(make_pattern '\x64\x6f\x61\x73')
pattern_f=$(make_pattern '\x72\x6f\x6f\x74')
pattern_g=$(make_pattern '\x43\x41\x50\x5f\x53\x59\x53\x5f\x41\x44\x4d\x49\x4e')
pattern_h=$(make_pattern '\x63\x68\x6d\x6f\x64\x20\x34\x37\x35\x35')

patterns=(
  "$pattern_a"
  "$pattern_b"
  "$pattern_c"
  "$pattern_d"
  "$pattern_e"
  "$pattern_f"
  "$pattern_g"
  "$pattern_h"
)

fail=0
while IFS= read -r -d '' file; do
  for pattern in "${patterns[@]}"; do
    if rg -i -n --fixed-strings -- "$pattern" "$file" >/dev/null; then
      echo "Blocked: disallowed content in $file"
      fail=1
      break
    fi
  done
  if [ "$fail" -ne 0 ]; then
    break
  fi
done < <(git ls-files -z)

if [ "$fail" -ne 0 ]; then
  exit 1
fi

schema_names=(
  "guard_receipt.schema.json"
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
