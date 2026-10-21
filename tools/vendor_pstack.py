#!/usr/bin/env python3
"""Builds the kit's copy of pstack: upstream pstack with the edits below applied.

pstack (https://github.com/cursor/plugins/tree/main/pstack) has a few rules
that, read literally, remove layers a project's architecture requires, or
tell the agent to fix a failing check itself. The edits below scope those
rules to what the repository's architecture allows. Two more edits tell
pstack's Claude Code adapter how to reach GitHub in a cloud session, which
blocks GitHub's GraphQL API and so every `gh pr` command. The edits name no
part of the kit, so they can go upstream unchanged; an edit that upstream
already has is skipped.

The script clones cursor/plugins, applies the edits to pstack/, runs
upstream's generator for the Claude Code tree and its --check, and replaces plugins/pstack/
in the kit with the generated tree. The kit's marketplace,
.claude-plugin/marketplace.json, serves that copy as pstack@agent-architecture-kit.

Usage:
  python3 tools/vendor_pstack.py                  vendor upstream main
  python3 tools/vendor_pstack.py --ref SHA        vendor one upstream commit
  python3 tools/vendor_pstack.py --diff FILE      also write the edits as a patch for upstream

Runs from the kit only. Needs Python 3.9 or later, Git, and Node 20 or later.
"""

import argparse
import hashlib
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

CLOUD_GITHUB = """
## GitHub in cloud sessions

A Claude Code cloud session blocks GitHub's GraphQL API. Every `gh pr` command fails there, and so does `scripts/watch-pr/watch-pr`, which reads GitHub through `gh pr` and GraphQL. Before the first GitHub step of a session, run `gh api graphql -f query='{viewer{login}}'`. When it fails with "not available from Claude Code sessions", the session is a cloud session, and every GitHub step follows this section. These are substitutes, not skips, so write no skip line.

The GitHub MCP tools (`mcp__github__*`) are the cloud session's built-in PR tool. For anything they do not cover, use `gh api` with a REST path, such as `repos/<owner>/<repo>/pulls/<pr>`. REST works in a cloud session.

| Forge command | In a cloud session |
| --- | --- |
| `gh pr create` | `mcp__github__create_pull_request` with `draft: false`. |
| `gh pr edit <pr> --base <branch>`, and title or body edits | `mcp__github__update_pull_request` with `base`, `title`, or `body`. |
| `gh pr ready <pr>` | `mcp__github__update_pull_request` with `draft: false`. |
| `gh pr view <pr> --json ...` | `mcp__github__pull_request_read` with method `get`. `merged` and `merged_at` say whether it merged, `base.ref` names its base, `head.sha` its head, and `mergeable_state` its merge state. |
| `gh pr list` | `mcp__github__list_pull_requests`, filtered by `head` as `<owner>:<branch>`, `base`, or `state`. Its `merged` field reads `false` even for a merged PR, so read a PR's merge state with method `get`. |
| `gh pr checks <pr>` | `mcp__github__pull_request_read` with method `get_check_runs`, and with method `get_status` for commit statuses. |
| Review threads | `mcp__github__pull_request_read` with method `get_review_comments`. Reply with `mcp__github__add_reply_to_pull_request_comment`, and resolve with `mcp__github__resolve_review_thread` and the thread's id. |
| `gh pr merge <pr> --squash` | `mcp__github__merge_pull_request` with `merge_method: "squash"` and `expectedHeadSha` set to the head that the verdict covers. Read the PR back afterward, as the step says. |
| `gh pr merge <pr> --auto` | `mcp__github__enable_pr_auto_merge`. |
| Re-running a failed CI job | `mcp__github__actions_run_trigger` with method `rerun_failed_jobs`. |
| `orch frontier set` | It reads PRs with `gh pr list`, so it fails. Run the Orchestrate playbook from a session outside the cloud. |

Without the MCP tools, use `gh api` REST paths, and these routes for what REST lacks: `GET repos/<owner>/<repo>/pulls/<pr>/ccr/review_threads`, `POST repos/<owner>/<repo>/pulls/<pr>/ccr/comments/<comment_id>/resolve`, `PUT` or `DELETE repos/<owner>/<repo>/pulls/<pr>/ccr/auto_merge`, and `POST repos/<owner>/<repo>/pulls/<pr>/ccr/ready_for_review`.

### Watching a PR in a cloud session

Where a playbook runs `scripts/watch-pr/watch-pr`, do this instead:

1. Subscribe the session to each PR with `subscribe_pr_activity` from the `claude-code-remote` MCP server. CI results, reviews, comments, and the merge then wake the session as new turns, so the playbook needs no `/loop` and no poll loop. Only the session receives these events, not its subagents. The session that runs the playbook subscribes, and hands each event to the PR's owner.
2. At each wake, and before each decision the playbook makes, read the PR's current state with the table above: the PR, its checks and statuses, and its review threads. Apply the playbook's rules to that state as you would to the watcher's verdict. Ready means `mergeable_state` reads `clean`. `unknown` means GitHub is still computing it, so read it again. A green check list alone is not ready.
3. Some changes wake no session, such as a conflict from a push to the base, another person's push, CI that reports only a commit status, or a lost event. While a PR waits, schedule a check-in about an hour out with `send_later` from the same server, and reread the PR when it fires.
4. For Shipping's queued stack, subscribe to every PR in the stack, and at each wake reread them from the bottom up. The run is complete when the top PR reads merged with trunk as its base.
5. Unsubscribe with `unsubscribe_pr_activity` once the PR merges or closes, or when the operator says to stop."""

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
    ("docs/harness/claude-code.md",
     "Claude Code has no Cursor Automations, Bugbot, Cursor cloud agents, or built-in PR tool.",
     "Claude Code has no Cursor Automations, Bugbot, or Cursor cloud agents, and only a cloud session has a "
     "built-in PR tool."),
    ("docs/harness/claude-code.md",
     "| A built-in PR tool | Use the forge command that the step gives, such as `gh pr create`. That is not a skip, "
     "so write no line. |",
     "| A built-in PR tool | In a cloud session, the GitHub MCP tools, as in GitHub in cloud sessions. Elsewhere, use "
     "the forge command that the step gives, such as `gh pr create`. Neither is a skip, so write no line. |\n"
     + CLOUD_GITHUB),
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
    """The upstream version, plus the upstream commit and a hash of EDITS, so Claude Code sees either change."""
    edits = hashlib.sha256(repr(EDITS).encode("utf-8")).hexdigest()[:7]
    for rel in ("plugin.json", ".claude-plugin/plugin.json"):
        path = os.path.join(tree, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["version"] = f"{manifest['version'].split('+')[0]}+kit.{sha[:7]}.{edits}"
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
