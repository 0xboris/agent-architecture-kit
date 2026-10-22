#!/usr/bin/env bash
# Runs the project checks in checks/ as BASE has them, against the files of HEAD.
# CI runs it before any code from the pull request runs, so a pull request cannot
# change an existing check, or what it sees, before the check runs.
#
# Usage: tools/run-base-checks.sh BASE      such as HEAD^1 in CI
set -euo pipefail
base=${1:?Usage: tools/run-base-checks.sh BASE}
cd "$(git rev-parse --show-toplevel)"
copy=$(mktemp -d)
trap 'rm -rf "$copy"' EXIT

if ! git cat-file -e "$base:checks" 2> /dev/null; then
  echo "The base has no project checks."
  exit 0
fi
git archive "$base" checks | tar -x -C "$copy"

status=0
for project_check in "$copy"/checks/*; do
  [ -f "$project_check" ] && [ -x "$project_check" ] || continue
  if "$project_check"; then
    echo "ok    $(basename "$project_check") (as the base has it)"
  else
    echo "FAIL  $(basename "$project_check") (as the base has it)"
    status=1
  fi
done
exit $status
