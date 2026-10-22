#!/usr/bin/env python3
"""Fails when a pull request loosens a check without an exception the owner approves.

.github/CODEOWNERS sends changes to the files that define the checks to the
owner. Some files need no owner, because most changes to them only tighten a
check: architecture-baseline.json, the project checks in checks/, and the
glossary. This guard catches the changes to them that loosen a check:

- architecture-baseline.json gains an entry or a higher count, including
  when it comes back after a pull request deleted it.
- an existing file in checks/ changes, loses its executable bit, or goes away.
- the glossary loses a term, which modules without business meaning may then use.

Such a pull request passes only when it also changes AGENTS.md, where the
exception is recorded, and the base branch's CODEOWNERS gives AGENTS.md an
owner, so that the owner reviews it. In GitHub Actions, each loosening is
also posted as an annotation on the pull request.

Usage:
  python3 tools/gateguard.py BASE     compare HEAD with BASE, such as HEAD^1 in CI

Exit codes: 0 nothing loosened, or the owner reviews it. 1 loosened without
the owner. 2 configuration error. Needs Python 3.9 or later, Git, and nothing else.
"""

import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # importing archcheck must not leave __pycache__ in tools/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from archcheck import ConfigError, parse_json_with_comments  # noqa: E402

BASELINE = "architecture-baseline.json"
CHECKS = "checks/"
CODEOWNERS = ".github/CODEOWNERS"
EXCEPTIONS = "AGENTS.md"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def file_at(root, revision, path):
    shown = git(root, "show", f"{revision}:{path}")
    return shown.stdout if shown.returncode == 0 else None


def changed_files(root, base):
    """(status, path) pairs. -z keeps paths with unusual characters unquoted."""
    diff = git(root, "diff", "-z", "--name-status", "--no-renames", base, "HEAD")
    if diff.returncode != 0:
        raise ConfigError(f"git diff against '{base}' failed: {diff.stderr.strip()}")
    fields = diff.stdout.split("\0")
    return list(zip(fields[0::2], fields[1::2]))


def baseline_raises(root, base):
    new_text = file_at(root, "HEAD", BASELINE)
    if new_text is None:
        return []
    old_text = file_at(root, base, BASELINE)
    if old_text is None and file_at(root, base, "tools/gateguard.py") is None:
        return []
    old = parse_json_with_comments(old_text, f"{base}:{BASELINE}") if old_text is not None else {}
    new = parse_json_with_comments(new_text, BASELINE)
    return [f"raises the baseline ({key}: {old.get(key, 0)} -> {count})"
            for key, count in sorted(new.items()) if count > old.get(key, 0)]


def glossary_path(root, base):
    config = file_at(root, base, "architecture.json")
    if config is None:
        return None
    return parse_json_with_comments(config, f"{base}:architecture.json").get("glossary")


def glossary_removals(root, base, glossary):
    def terms(text):
        return {line[3:].strip() for line in (text or "").splitlines() if line.startswith("## ")}
    removed = terms(file_at(root, base, glossary)) - terms(file_at(root, "HEAD", glossary))
    return [f"removes the glossary term '{term}', which modules without business meaning may then use"
            for term in sorted(removed)]


def owner_rules(text):
    """CODEOWNERS lines as (regex, has_owner). The last matching line decides, as on GitHub."""
    rules = []
    for line in text.splitlines():
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
    root = git(".", "rev-parse", "--show-toplevel").stdout.strip()
    if not root:
        print("Gate guard: not inside a Git repository.", file=sys.stderr)
        return 2
    try:
        changes = changed_files(root, base)
        changed = {path for _, path in changes}
        problems = []
        for status, path in changes:
            if path.startswith(CHECKS) and status != "A":
                verb = "deletes" if status == "D" else "changes"
                problems.append((path, f"{verb} the existing check {path}"))
            if path == BASELINE:
                problems += [(BASELINE, problem) for problem in baseline_raises(root, base)]
        glossary = glossary_path(root, base)
        if glossary in changed:
            problems += [(glossary, problem) for problem in glossary_removals(root, base, glossary)]
    except ConfigError as error:
        print(f"Gate guard: {error}", file=sys.stderr)
        return 2

    if not problems:
        print("Gate guard passed: no check was loosened.")
        return 0
    rules = owner_rules(file_at(root, base, CODEOWNERS) or "")
    recorded = EXCEPTIONS in changed and is_owned(rules, EXCEPTIONS)
    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    print(f"Gate guard: this pull request loosens {len(problems)} check{'' if len(problems) == 1 else 's'}.\n")
    for path, problem in problems:
        print(f"  It {problem}.")
        if annotate:
            print(f"::{'warning' if recorded else 'error'} file={path}::This pull request {problem}.")
    if recorded:
        print(f"\nIt also changes {EXCEPTIONS}, where the exception is recorded, so the owner reviews it.")
        return 0
    print(f"\nTo loosen a check, record the exception in the table in {EXCEPTIONS}, with its reason and the "
          f"date it expires, in the same pull request. {EXCEPTIONS} is a gate file, so the owner reviews it. "
          "Otherwise fix the violation, or add a new check.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
