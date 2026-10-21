#!/usr/bin/env python3
"""Builds the kit's copy of pstack: upstream pstack with the edits below applied.

pstack (https://github.com/cursor/plugins/tree/main/pstack) has a few rules
that, read literally, remove layers a project's architecture requires, or
tell the agent to fix a failing check itself. The edits below scope those
rules to what the repository's architecture allows. They name no part of
the kit, so they can go upstream unchanged; an edit that upstream already
has is skipped.

The script clones cursor/plugins, applies the edits to pstack/, runs
upstream's generator for the Claude Code tree, checks the result with
upstream's own validator when Node can run it, and replaces plugins/pstack/
in the kit with the generated tree. The kit's marketplace,
.claude-plugin/marketplace.json, serves that copy as pstack@agent-architecture-kit.

Usage:
  python3 tools/vendor_pstack.py                  vendor upstream main
  python3 tools/vendor_pstack.py --ref SHA        vendor one upstream commit
  python3 tools/vendor_pstack.py --diff FILE      also write the edits as a patch for upstream

Runs from the kit only. Needs Python 3.9 or later, Git, and Node 20 or later.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

UPSTREAM = "https://github.com/cursor/plugins.git"
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(KIT, "plugins", "pstack")
ARCHITECTURE = "the repository's architecture docs"

# (file under pstack/, text upstream has, text the kit's copy has)
EDITS = [
    ("skills/principle-minimize-reader-load/SKILL.md",
     "speculative indirection that was never needed. Inline them.",
     f"speculative indirection that was never needed. Inline them. A layer that {ARCHITECTURE} require stays, "
     "even when it is thin."),
    ("skills/principle-minimize-reader-load/SKILL.md",
     "adds reader load without compression. Collapse pass-through layers.",
     f"adds reader load without compression. Collapse pass-through layers, except the layers that {ARCHITECTURE} "
     "require."),
    ("skills/poteto-mode/SKILL.md",
     "Count layers and hidden state, collapse one-caller wrappers, shrink mutable scope.",
     "Count layers and hidden state, collapse one-caller wrappers that the architecture does not require, "
     "shrink mutable scope."),
    ("skills/architect/references/design-red-flags.md",
     "Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction.",
     "Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction, or when "
     f"{ARCHITECTURE} require the layer it belongs to."),
    ("skills/architect/SKILL.md",
     "Whole-shape alternatives, not point fixes inside one shape.",
     f"Whole-shape alternatives, not point fixes inside one shape. When {ARCHITECTURE} fix the module layout, "
     "the candidates differ inside that layout, in types, data structures, and interfaces, and a change to the "
     "layout is the operator's call."),
    ("skills/poteto-mode/playbooks/refactoring.md",
     "Delete dead code, collapse one-caller wrappers, drop redundant validators,",
     "Delete dead code, collapse one-caller wrappers that the architecture does not require, drop redundant "
     "validators,"),
    ("skills/interrogate/references/code-quality-review.md",
     "Flag thin abstractions, identity wrappers, or pass-through helpers that add indirection without buying clarity.",
     "Flag thin abstractions, identity wrappers, or pass-through helpers that add indirection without buying "
     f"clarity. A layer that {ARCHITECTURE} require is not one of them."),
    ("skills/typescript-best-practices/SKILL.md",
     "A brand comes from a verifying type guard (`input is AgentId`), never from `as`.",
     "A brand comes from a verifying type guard (`input is AgentId`) or a parse function that validates first, "
     "never from an unchecked `as`."),
    ("skills/typescript-best-practices/SKILL.md",
     "Mock only what you can't run locally. |",
     "Mock only what you can't run locally. Where the repository's testing rules prescribe test doubles at a "
     "boundary, such as stubs typed against a port, follow them. |"),
    ("skills/poteto-mode/playbooks/autonomous-run.md",
     "orphaned follow-ups, and fixable drift yourself via poteto-mode.",
     "orphaned follow-ups, and fixable drift yourself via poteto-mode. A gate that the repository's owner "
     "controls, such as an architecture check or a file that needs code-owner review, is not a tooling failure. "
     "Fix the code it reports, or report the gate, and never loosen it to get green."),
]


def run(args, cwd, **kwargs):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, **kwargs)
    if result.returncode != 0:
        sys.exit(f"vendor_pstack: `{' '.join(args)}` failed:\n{result.stdout}{result.stderr}")
    return result.stdout


def apply_edits(pstack):
    applied, upstream = [], []
    for rel, old, new in EDITS:
        path = os.path.join(pstack, rel)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if new in text:
            upstream.append(rel)
            continue
        if text.count(old) != 1:
            sys.exit(f"vendor_pstack: {rel} no longer contains this text exactly once:\n  {old}\n"
                     "Upstream changed it. Update EDITS in tools/vendor_pstack.py to match, then run this again.")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new))
        applied.append(rel)
    return applied, upstream


def stamp_version(tree, sha):
    for rel in ("plugin.json", ".claude-plugin/plugin.json"):
        path = os.path.join(tree, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["version"] = f"{manifest['version'].split('+')[0]}+kit.{sha[:7]}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Vendor pstack with the kit's edits.")
    parser.add_argument("--ref", default="main", help="upstream branch, tag, or commit (default: main)")
    parser.add_argument("--diff", metavar="FILE", help="write the edits, with the regenerated tree, as a patch")
    args = parser.parse_args()
    if shutil.which("node") is None:
        sys.exit("vendor_pstack: Node is required to run upstream's generator.")

    with tempfile.TemporaryDirectory() as tmp:
        clone = os.path.join(tmp, "plugins")
        os.makedirs(clone)
        run(["git", "init", "-q"], clone)
        run(["git", "fetch", "-q", "--depth", "1", UPSTREAM, args.ref], clone)
        run(["git", "checkout", "-q", "FETCH_HEAD"], clone)
        sha = run(["git", "rev-parse", "HEAD"], clone).strip()

        applied, upstream = apply_edits(os.path.join(clone, "pstack"))
        run(["node", "scripts/generate-pstack-harness-trees.mjs"], clone)
        run(["node", "scripts/generate-pstack-harness-trees.mjs", "--check"], clone)

        if args.diff:
            with open(args.diff, "w", encoding="utf-8") as f:
                f.write(run(["git", "diff", "--", "pstack", "harness"], clone))

        tree = os.path.join(clone, "harness", "pstack", "claude-code")
        if os.path.exists(DEST):
            shutil.rmtree(DEST)
        shutil.copytree(tree, DEST)
        stamp_version(DEST, sha)

    print(f"Vendored pstack from cursor/plugins {sha[:12]} into plugins/pstack/.")
    print(f"Applied {len(applied)} edits" + (f"; {len(upstream)} are upstream already." if upstream else "."))
    if args.diff:
        print(f"Wrote the patch for upstream to {args.diff}.")
    print("Run `claude plugin validate .` from the kit root if Claude Code is installed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
