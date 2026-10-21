#!/usr/bin/env python3
"""Lists the changes on a branch that loosen a rule, so that they wait for the owner.

The architecture check, the linter, and the tests stop code that breaks a rule.
This check looks at changes to the rules themselves. A change that keeps every
rule or makes one stricter passes. A change that loosens one fails, and the gates
workflow lets it merge once the owner approves the pull request's current head.

It compares the merge base with BASE against the working tree:

- architecture.json: an import, package, file, or pattern that a kind now allows,
  a call or term it no longer bans, a higher size limit, and any change to the
  module map or to what the check scans.
- architecture-baseline.json: a violation that it accepts more times.
- Every package.json: a change outside the dependency lists, such as scripts or
  subpath imports, and a removed compiler, linter, or test runner.
- Added source lines that silence the linter or the type checker, or skip a test.

A file that this check cannot judge, such as ./check or tools/, is listed in
.github/CODEOWNERS instead, so every change to it needs the owner.

Usage:
  python3 tools/gatecheck.py [BASE]    BASE defaults to origin's default branch

Exit codes: 0 nothing loosens a rule, 1 something does, 2 a git or configuration error.
Needs Python 3.9 or later and nothing else.
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from archcheck import ConfigError, is_set_reference, parse_json_with_comments  # noqa: E402

CONFIG = "architecture.json"
BASELINE = "architecture-baseline.json"

PACKAGE_INFO_KEYS = {"name", "version", "description", "private", "license", "author", "keywords",
                     "repository", "homepage", "bugs", "contributors", "funding"}
PACKAGE_DEPENDENCY_KEYS = {"dependencies", "devDependencies", "optionalDependencies", "peerDependencies"}
# Removing one of these turns a step of ./check off or makes it weaker.
TOOLING_PACKAGES = {"typescript", "oxlint", "oxlint-tsgolint", "eslint", "typescript-eslint", "vitest"}

SOURCE_EXTENSIONS = (".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".go", ".swift")
SILENCERS = [
    (re.compile(r"\b(?:oxlint|eslint)-disable"), "silences the linter"),
    (re.compile(r"//\s*nolint\b"), "silences the linter"),
    (re.compile(r"swiftlint:disable"), "silences the linter"),
    (re.compile(r"@ts-(?:ignore|nocheck|expect-error)\b"), "silences the type checker"),
    (re.compile(r"\b(?:it|test|describe|suite)\.(?:skip|todo|only)\s*\("), "skips tests"),
    (re.compile(r"\{\s*(?:skip|todo)\s*:\s*true"), "skips a test"),
    (re.compile(r"\bt\.Skip(?:f|Now)?\s*\("), "skips a test"),
    (re.compile(r"\bXCTSkip"), "skips a test"),
]


class GitError(Exception):
    pass


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def default_base():
    try:
        return git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD").strip()
    except GitError:
        return "origin/main"


def base_json(base, path):
    try:
        text = git("show", f"{base}:{path}")
    except GitError:
        return None
    return parse_json_with_comments(text, f"{path} at the merge base")


def head_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return parse_json_with_comments(f.read(), path)


def code(value):
    return f"`{value}`"


# ------------------------------------------------------- architecture.json

def added(old, new):
    return sorted(set(new or []) - set(old or []), key=str)


def removed(old, new):
    return sorted(set(old or []) - set(new or []), key=str)


def compare_architecture(old, new, report):
    for key in sorted(set(old) | set(new)):
        if key in ("kinds", "externalSets", "forbiddenCallSets"):
            continue
        if key in ("testFiles", "ignore"):
            for pattern in added(old.get(key), new.get(key)):
                report(f"{code(key)} adds {code(pattern)}, so the check exempts more files.")
        elif key == "modules":
            if old.get(key) != new.get(key):
                report("The module map changed, so a directory may now belong to a kind with fewer rules.")
        elif old.get(key) != new.get(key):
            report(f"{code(key)} changed, which changes what the check scans or how it resolves imports.")

    old_kinds, new_kinds = old.get("kinds", {}), new.get("kinds", {})
    for name, old_kind in old_kinds.items():
        if name not in new_kinds:
            report(f"The kind {code(name)} was removed.")
            continue
        compare_kind(f"The kind {code(name)}", old_kind, new_kinds[name], report)

    compare_external_sets(old, new, report)
    old_calls, new_calls = old.get("forbiddenCallSets", {}), new.get("forbiddenCallSets", {})
    for name, calls in old_calls.items():
        kept = {call.get("pattern") for call in new_calls.get(name, [])}
        for call in calls:
            if call.get("pattern") not in kept:
                report(f"The call set {code('@' + name)} no longer bans {code(call.get('pattern'))}.")


def compare_kind(label, old, new, report):
    for entry in added(old.get("mayImport"), new.get("mayImport")):
        report(f"{label} may now import {code(entry)}.")
    old_external, new_external = old.get("external", {}), new.get("external", {})
    for entry in added(old_external.get("allow"), new_external.get("allow")):
        report(f"{label} now allows the package {code(entry)}.")
    for entry in removed(old_external.get("deny"), new_external.get("deny")):
        report(f"{label} no longer denies the package {code(entry)}.")
    for key in sorted((set(old_external) | set(new_external)) - {"allow", "deny"}):
        if old_external.get(key) != new_external.get(key):
            report(f"{label} changed {code('external.' + key)}.")
    for entry in removed(old.get("forbiddenCalls"), new.get("forbiddenCalls")):
        report(f"{label} no longer forbids {code(entry)}.")

    old_terms, new_terms = old.get("bannedTerms"), new.get("bannedTerms")
    if isinstance(old_terms, list) and isinstance(new_terms, list):
        for term in removed(old_terms, new_terms):
            report(f"{label} no longer bans the term {code(term)}.")
    elif old_terms is not None and old_terms != new_terms:
        report(f"{label} changed {code('bannedTerms')} from {code(old_terms)} to {code(new_terms)}.")

    if "publicEntry" in old:
        if "publicEntry" not in new:
            report(f"{label} no longer requires imports through a public entry.")
        for entry in added(old["publicEntry"], new.get("publicEntry", [])):
            report(f"{label} accepts imports through {code(entry)}.")

    old_root, new_root = old.get("composition"), new.get("composition")
    if old_root is not None:
        if new_root is None:
            report(f"{label} no longer has rules for the composition root.")
        else:
            for key in ("allowedFiles", "controlFlowAllowedIn", "controlFlowAllowedPatterns"):
                for entry in added(old_root.get(key), new_root.get(key)):
                    report(f"{label} adds {code(entry)} to {code('composition.' + key)}.")
            old_max, new_max = old_root.get("maxLines", float("inf")), new_root.get("maxLines", float("inf"))
            if new_max > old_max:
                report(f"{label} raises {code('composition.maxLines')} from {old_max} to {new_max}.")
            for key in sorted((set(old_root) | set(new_root)) - {"allowedFiles", "controlFlowAllowedIn",
                                                                 "controlFlowAllowedPatterns", "maxLines"}):
                if old_root.get(key) != new_root.get(key):
                    report(f"{label} changed {code('composition.' + key)}.")

    known = {"mayImport", "external", "forbiddenCalls", "bannedTerms", "publicEntry", "composition"}
    for key in sorted((set(old) | set(new)) - known):
        if old.get(key) != new.get(key):
            report(f"{label} changed {code(key)}.")


def compare_external_sets(old, new, report):
    allowed, denied = set(), set()
    for kind in new.get("kinds", {}).values():
        external = kind.get("external", {})
        allowed.update(e[1:] for e in external.get("allow", []) if is_set_reference(e))
        denied.update(e[1:] for e in external.get("deny", []) if is_set_reference(e))
    old_sets, new_sets = old.get("externalSets", {}), new.get("externalSets", {})
    for name in sorted(set(old_sets) | set(new_sets)):
        if name in allowed:
            for entry in added(old_sets.get(name), new_sets.get(name)):
                report(f"The package set {code('@' + name)}, which a kind allows, adds {code(entry)}.")
        if name in denied:
            for entry in removed(old_sets.get(name), new_sets.get(name)):
                report(f"The package set {code('@' + name)}, which a kind denies, drops {code(entry)}.")


# ------------------------------------------------------ baseline, packages

def compare_baseline(old, new, report):
    for key, count in sorted(new.items()):
        before = old.get(key, 0)
        if count > before:
            report(f"It accepts {code(key)} {count} times, up from {before}.")


def compare_package(old, new, report):
    for key in sorted((set(old) | set(new)) - PACKAGE_INFO_KEYS - PACKAGE_DEPENDENCY_KEYS):
        if old.get(key) != new.get(key):
            report(f"{code(key)} changed. Scripts, subpath imports, and the other settings can change how ./check runs.")
    old_names = {name for key in PACKAGE_DEPENDENCY_KEYS for name in old.get(key, {})}
    new_names = {name for key in PACKAGE_DEPENDENCY_KEYS for name in new.get(key, {})}
    for name in sorted((old_names - new_names) & TOOLING_PACKAGES):
        report(f"It removes {code(name)}, which ./check runs.")


def changed_files(merge_base):
    return [line for line in git("diff", "--name-only", merge_base, "--").splitlines() if line]


def silencers(merge_base):
    found, path, number = [], None, 0
    for line in git("diff", "--unified=0", "--no-color", merge_base, "--").splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            number = int(match.group(1)) if match else 0
        elif line.startswith("+") and path and path.endswith(SOURCE_EXTENSIONS):
            for pattern, effect in SILENCERS:
                match = pattern.search(line)
                if match:
                    found.append((f"{path}:{number}", f"{code(match.group(0).strip())} {effect}."))
                    break
            number += 1
    return found


# --------------------------------------------------------------------- main

def main():
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1].startswith("-")):
        print(__doc__)
        return 2
    base = sys.argv[1] if len(sys.argv) == 2 else default_base()
    try:
        os.chdir(git("rev-parse", "--show-toplevel").strip())
        merge_base = git("merge-base", base, "HEAD").strip()
        findings = []

        def reporter(where):
            return lambda message: findings.append((where, message))

        old, new = base_json(merge_base, CONFIG), head_json(CONFIG)
        if old is not None and new is not None:
            compare_architecture(old, new, reporter(CONFIG))
        compare_baseline(base_json(merge_base, BASELINE) or {}, head_json(BASELINE) or {}, reporter(BASELINE))
        for path in changed_files(merge_base):
            if os.path.basename(path) == "package.json" and "node_modules/" not in path and os.path.exists(path):
                compare_package(base_json(merge_base, path) or {}, head_json(path), reporter(path))
        findings.extend(silencers(merge_base))
    except (GitError, ConfigError, OSError) as error:
        print(f"Gate check: {error}", file=sys.stderr)
        return 2

    if not findings:
        print(f"Gate check passed: no change loosens a rule (compared with {base} at {merge_base[:12]}).")
        return 0
    print(f"Gate check: {len(findings)} changes loosen a rule (compared with {base} at {merge_base[:12]}).\n")
    for where, message in findings:
        print(f"{where}\n  {message}\n")
    print("These changes need the owner's approval. If the change is meant, put it in a pull request of its own\n"
          "and give the reason in its description, so other work does not wait for the owner. If it only makes\n"
          "a check pass, undo it and apply the fix that the check names.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
