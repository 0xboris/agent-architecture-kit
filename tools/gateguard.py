#!/usr/bin/env python3
"""Fails when a pull request loosens a check that needs no owner.

.github/CODEOWNERS sends changes to the files that define the checks to the
owner. Two kinds of change can only tighten a check, so they need no owner,
and this guard keeps them that way:

- architecture-baseline.json may lose entries and lower counts, never gain them.
- checks/ may gain new checks. Changing or deleting one can loosen it.

Usage:
  python3 tools/gateguard.py BASE     compare HEAD with BASE, such as HEAD^1 in CI

Exit codes: 0 nothing loosened, 1 something loosened, 2 configuration error.
Needs Python 3.9 or later, Git, and nothing else.
"""

import json
import subprocess
import sys

BASELINE = "architecture-baseline.json"
CHECKS = "checks/"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def baseline_at(root, revision):
    shown = git(root, "show", f"{revision}:{BASELINE}")
    if shown.returncode != 0:
        return None
    return json.loads(shown.stdout)


def raised_entries(old, new):
    return sorted(f"{key}: {old.get(key, 0)} -> {count}" for key, count in new.items() if count > old.get(key, 0))


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    base = sys.argv[1]
    root = git(".", "rev-parse", "--show-toplevel").stdout.strip()
    if not root:
        print("Gate guard: not inside a Git repository.", file=sys.stderr)
        return 2
    diff = git(root, "diff", "--name-status", "--no-renames", base, "HEAD")
    if diff.returncode != 0:
        print(f"Gate guard: git diff against '{base}' failed: {diff.stderr.strip()}", file=sys.stderr)
        return 2

    problems = []
    for line in diff.stdout.splitlines():
        status, path = line.split("\t", 1)
        if path.startswith(CHECKS) and status != "A":
            verb = "deletes" if status == "D" else "changes"
            problems.append(f"{verb} the existing check {path}. Add a new check instead, "
                            "or ask the owner to change this one.")
        if path == BASELINE and status != "D":
            try:
                old = baseline_at(root, base)
                new = baseline_at(root, "HEAD")
            except json.JSONDecodeError as error:
                print(f"Gate guard: {BASELINE} is not valid JSON: {error}", file=sys.stderr)
                return 2
            if old is not None and new is not None:
                for entry in raised_entries(old, new):
                    problems.append(f"raises the baseline ({entry}). Fix the violation instead.")

    if not problems:
        print("Gate guard passed: no check was loosened.")
        return 0
    print(f"Gate guard: this pull request loosens {len(problems)} check{'' if len(problems) == 1 else 's'}.\n")
    for problem in problems:
        print(f"  It {problem}")
    print("\nThe baseline may only go down, and checks/ may only gain new checks. "
          "Changes that loosen a check are the owner's to make.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
