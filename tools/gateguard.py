#!/usr/bin/env python3
"""Fails when a change touches a gate file, for pull requests into branches other than main.

Gate files are the paths that .github/CODEOWNERS gives an owner, except the
composition root, whose wiring changes are expected while a feature grows.
On main, branch protection sends gate changes to the owner. A feature branch
has no such protection, so CI runs this check on pull requests into it, and
gate changes go into their own pull request against main instead.

Usage:
  python3 tools/gateguard.py BASE     compare HEAD with BASE, such as HEAD^1 in CI

Exit codes: 0 no gate file changed, 1 gate files changed, 2 configuration error.
Needs Python 3.9 or later, Git, and nothing else.
"""

import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # importing archcheck must not leave __pycache__ in tools/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from archcheck import ConfigError, Project, load_json_with_comments  # noqa: E402


def owner_rules(path):
    """CODEOWNERS lines as (regex, has_owner). The last matching line decides, as on GitHub."""
    rules = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            fields = line.split("#", 1)[0].split()
            if fields:
                rules.append((pattern_regex(fields[0]), len(fields) > 1))
    return rules


def pattern_regex(pattern):
    anchored = pattern.startswith("/") or "/" in pattern.rstrip("/")
    directory = pattern.endswith("/")
    body, i, text = [], 0, pattern.strip("/")
    while i < len(text):
        if text.startswith("**/", i):
            body.append("(?:.*/)?")
            i += 3
        elif text.startswith("**", i):
            body.append(".*")
            i += 2
        elif text[i] == "*":
            body.append("[^/]*")
            i += 1
        elif text[i] == "?":
            body.append("[^/]")
            i += 1
        else:
            body.append(re.escape(text[i]))
            i += 1
    start = "^" if anchored else "^(?:.*/)?"
    end = "/.*$" if directory else "(?:/.*)?$"
    return re.compile(start + "".join(body) + end)


def is_owned(rules, path):
    owned = False
    for regex, has_owner in rules:
        if regex.match(path):
            owned = has_owner
    return owned


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    base = sys.argv[1]
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    if not root:
        print("Gate guard: not inside a Git repository.", file=sys.stderr)
        return 2
    codeowners = os.path.join(root, ".github", "CODEOWNERS")
    if not os.path.exists(codeowners):
        print("Gate guard: .github/CODEOWNERS is missing, so the gate files are unknown.", file=sys.stderr)
        return 2
    try:
        project = Project(root, load_json_with_comments(os.path.join(root, "architecture.json")))
    except (ConfigError, OSError) as error:
        print(f"Gate guard: {error}", file=sys.stderr)
        return 2

    diff = subprocess.run(["git", "diff", "--name-only", "--no-renames", base, "HEAD"],
                          cwd=root, capture_output=True, text=True)
    if diff.returncode != 0:
        print(f"Gate guard: git diff against '{base}' failed: {diff.stderr.strip()}", file=sys.stderr)
        return 2

    rules = owner_rules(codeowners)
    gates = []
    for path in diff.stdout.split():
        module = project.module_for_path(path)
        if module is not None and "composition" in project.kinds.get(module.kind, {}):
            continue
        if is_owned(rules, path):
            gates.append(path)

    if not gates:
        print("Gate guard passed: no gate file changed.")
        return 0
    print(f"Gate guard: this pull request changes {len(gates)} gate file{'' if len(gates) == 1 else 's'}.\n")
    for path in gates:
        print(f"  {path}")
    print("\nGate files define the checks, and this branch has no owner review. Move these changes into "
          "their own pull request against main, where the owner reviews them, then merge main into this branch.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
