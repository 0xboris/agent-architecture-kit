# Plugins

The kit is also a Claude Code plugin marketplace, named `agent-architecture-kit` in `.claude-plugin/marketplace.json`. It serves one plugin.

## pstack

`plugins/pstack/` is [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, MIT licensed, with twelve edits in two groups.

### Rules that defer to the architecture

Read literally, some pstack rules remove layers that a project's architecture requires, replace the test doubles that its testing rules prescribe, or tell the agent to fix a failing check itself. Ten edits scope those rules to what the repository's architecture docs allow:

| Upstream file | Upstream rule | The edit adds |
| --- | --- | --- |
| `principle-minimize-reader-load` | Collapse one-caller wrappers, adapters with one implementation, and pass-through layers. | Except the layers that the repository's architecture docs require. |
| `poteto-mode` (principles index) | Collapse one-caller wrappers. | The same exception. |
| `architect/references/design-red-flags.md` | Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction. | Or when the architecture docs require its layer. |
| `architect` | Compare whole-shape alternatives. | When the architecture docs fix the module layout, compare inside it. A layout change is the operator's call. |
| `poteto-mode/playbooks/refactoring.md` | Collapse one-caller wrappers before reshaping. | Only those the architecture does not require. |
| `interrogate/references/code-quality-review.md` | Flag thin abstractions and pass-through helpers. | A required layer is not one of them. |
| `typescript-best-practices` | A brand comes from a type guard, never from `as`. | Or from a parse function that validates first. |
| `typescript-best-practices` | Mock only what you can't run locally. | Follow the repository's rules for test doubles at a boundary. |
| `poteto-mode/playbooks/autonomous-run.md` | Fix flaky verifiers and tooling failures yourself. | An owner-controlled gate is not a tooling failure. Never loosen it to get green. |

### GitHub in Claude Code cloud sessions

A Claude Code cloud session blocks GitHub's GraphQL API. Every `gh pr` command fails there, and so does pstack's PR watcher, `scripts/watch-pr/watch-pr`, which the babysit and shipping playbooks use. `gh api` with REST paths still works, and so do the GitHub MCP tools, which run outside the session.

Two edits to pstack's Claude Code adapter, `docs/harness/claude-code.md`, cover this. One changes its "built-in PR tool" row, and the other adds the section "GitHub in cloud sessions":

- The agent detects a cloud session by running `gh api graphql` once, before its first GitHub step.
- In a cloud session, the GitHub MCP tools are pstack's built-in PR tool, which its playbooks already prefer over a forge command. A table maps each `gh pr` command that pstack uses to an MCP tool. `gh api` REST paths cover the rest.
- In place of `watch-pr`, the session subscribes to each PR with `subscribe_pr_activity`, so CI results, reviews, comments, and the merge wake it. At each wake it reads the PR's state with the MCP tools and applies the playbook's rules. A check-in with `send_later` covers changes that wake no session, such as a conflict from a push to the base.
- `orch frontier set` reads PRs with `gh pr list`, so the Orchestrate playbook runs from a session outside the cloud.

None of the edits names the kit, so the same edits can go upstream. Once upstream has them, a project can enable `pstack@cursor-plugins` instead, and this copy can go.

Do not edit `plugins/pstack/` by hand. `tools/vendor_pstack.py` builds it:

```bash
python3 tools/vendor_pstack.py              # vendor upstream main
python3 tools/vendor_pstack.py --ref SHA    # vendor one upstream commit
```

The script clones `cursor/plugins`, applies the edits in its `EDITS` list to `pstack/`, runs upstream's generator for the Claude Code tree, and copies that tree here. It sets the plugin's version to the upstream version plus `+kit.`, the upstream commit, and a hash of the edits, so Claude Code sees a change to either. When upstream rewords a line that an edit changes, the script stops and names the line. Update the edit to match, and run the script again. An edit that upstream already has is skipped.

## Proposing the edits upstream

```bash
python3 tools/vendor_pstack.py --diff pstack.diff
```

This writes all twelve edits, with upstream's regenerated `harness/pstack/claude-code/` tree, as one patch against `cursor/plugins` main. The two groups are separate topics, so propose them as two pull requests. Each half passes upstream's checks on its own.

### Pull request 1: rules that defer to the architecture

In a branch of your fork, run `git apply --exclude='*/docs/harness/claude-code.md' pstack.diff`, then open a pull request with this title and body.

Title:

```
fix(pstack): keep the layers a repository's architecture requires
```

Body:

```markdown
## Why

Several pstack rules, read literally, remove layers that a repository's own architecture requires. Minimize Reader Load inlines "adapters with no second implementation", and the refactoring playbook collapses one-caller wrappers. In a ports-and-adapters codebase that deletes ports and use cases that the project keeps on purpose, so the agent gets two instructions that disagree. The autonomous-run playbook also lists tooling failures as the agent's to fix, which an agent can read as permission to loosen an architecture check.

## What changed

- The layer rules in Minimize Reader Load, the design red flags, the refactoring playbook, the code-quality review lens, and the poteto-mode index keep a layer that the repository's architecture docs require. `architect` compares candidates inside a module layout that those docs fix.
- `typescript-best-practices` accepts a validating parse function as a source of brands, and follows a repository's rules for test doubles at a boundary.
- The autonomous-run playbook says that an owner-controlled gate is not a tooling failure.

## Scope

- Only repositories whose docs define an architecture see a change. Elsewhere every rule reads as before.
- No rule changes what pstack prefers. Each edit adds one exception.

## Verification

- `node scripts/generate-pstack-harness-trees.mjs --check` passes on the regenerated tree.
- `node scripts/validate-plugins.mjs` passes.
- In projects built with the agent architecture kit: <what you saw pstack do with and without the edits>.
```

Before you open it, run both commands in the fork, as upstream's CI does, and replace the last line with what you have seen in your own projects.

### Pull request 2: GitHub in Claude Code cloud sessions

In a second branch, run `git apply --include='*/docs/harness/claude-code.md' pstack.diff`, then open a pull request with this title and body.

Title:

```
fix(pstack): reach GitHub without GraphQL in Claude Code cloud sessions
```

Body:

```markdown
## Why

A Claude Code cloud session blocks GitHub's GraphQL API, with the message "GitHub GraphQL is not available from Claude Code sessions". Every `gh pr` command fails there, and so does `scripts/watch-pr/watch-pr`, so the babysit, shipping, and autopilot playbooks stop at their first GitHub step. REST through `gh api` and the GitHub MCP tools still work.

## What changed

- The Claude Code adapter gets a section, GitHub in cloud sessions. The agent detects a cloud session with one `gh api graphql` call, then uses the GitHub MCP tools as the built-in PR tool. A table maps each `gh pr` command that pstack uses to an MCP tool.
- In a cloud session, PR activity subscriptions replace `watch-pr`: GitHub events wake the session, which rereads the PR and applies the playbook's rules.
- The "built-in PR tool" row points cloud sessions to the new section.

## Scope

- Only Claude Code cloud sessions see a change. Local Claude Code sessions and Cursor read the adapter as before.
- `watch-pr` and `orch` keep their GraphQL code. The Orchestrate playbook still needs a session outside the cloud.

## Verification

- `node scripts/generate-pstack-harness-trees.mjs --check` passes on the regenerated tree.
- `node scripts/validate-plugins.mjs` passes.
- In a cloud session, `gh pr view` and `gh api graphql` fail with HTTP 403, while `gh api` REST paths and the MCP tools in the table return the fields it names.
```
