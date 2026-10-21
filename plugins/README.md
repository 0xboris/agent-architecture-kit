# Plugins

The kit is also a Claude Code plugin marketplace, named `agent-architecture-kit` in `.claude-plugin/marketplace.json`. It serves one plugin.

## pstack

`plugins/pstack/` is [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, MIT licensed, with ten edits. Read literally, some pstack rules remove layers that a project's architecture requires, replace the test doubles that its testing rules prescribe, or tell the agent to fix a failing check itself. The edits scope those rules to what the repository's architecture docs allow:

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

The edits name no part of the kit, so the same edits can go upstream. Once upstream has them, a project can enable `pstack@cursor-plugins` instead, and this copy can go.

Do not edit `plugins/pstack/` by hand. `tools/vendor_pstack.py` builds it:

```bash
python3 tools/vendor_pstack.py              # vendor upstream main
python3 tools/vendor_pstack.py --ref SHA    # vendor one upstream commit
```

The script clones `cursor/plugins`, applies the edits in its `EDITS` list to `pstack/`, runs upstream's generator for the Claude Code tree, and copies that tree here. It sets the plugin's version to the upstream version plus `+kit.` and the upstream commit, so Claude Code sees each update. When upstream rewords a line that an edit changes, the script stops and names the line. Update the edit to match, and run the script again. An edit that upstream already has is skipped.

## Proposing the edits upstream

```bash
python3 tools/vendor_pstack.py --diff pstack.diff
```

This writes the edits, with upstream's regenerated `harness/pstack/claude-code/` tree, as a patch against `cursor/plugins` main. Apply it in a fork with `git apply pstack.diff`, then open a pull request with this title and body.

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
