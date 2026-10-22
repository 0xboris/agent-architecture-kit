# Agent instructions

`README.md` describes what the project does. This codebase follows the architecture in `docs/ARCHITECTURE.md`. Read it before you add or move code. `docs/architecture/__LANGUAGE__.md` shows how each part looks in this language, `docs/architecture/stack.md` names the libraries this project uses, and `docs/architecture/modules.md` lists every module with its kind.

## Reference slice

The reference slice is **Notes**. Copy its structure when you add a slice, a use case, a port, an adapter, or their tests. The owner replaces Notes with the first real slice that follows the same patterns, and changes this line.

## Commands

- `./check` verifies everything: the architecture, the build, the types, and the tests. Run it after each step. A task is done only when it passes.
- The `new-slice` and `new-port` skills list the files that a new slice or port needs.

## How to work here

- Copy the structure of the reference slice, or of the closest existing code that follows it.
- When the check reports a violation, apply the fix it names. Never change a gate file to make a check pass. `.github/CODEOWNERS` lists the gate files: `architecture.json`, `check`, `tools/`, `.claude/`, `.github/`, the instruction files, the architecture docs, and the compiler, linter, and test runner settings. Changes to them need the owner.
- To tighten a rule, add an executable to `checks/`, or lower the baseline with `python3 tools/archcheck.py --write-baseline` after you fix a violation. Neither needs the owner.
- Use the names in `GLOSSARY.md` for business concepts, and add new concepts to it.
- A bug fix starts with a failing reproduction, committed before the fix: a test when a cheap one exists, otherwise a script or a recorded run against the running app.
- End with a short report: what changed, what you could not verify, and follow-ups you noticed but did not do.

## Skills and plugins

Workflow skills and plugins, such as pstack, run here under this file and `docs/ARCHITECTURE.md`. Where their advice differs, these files win.

- The module kinds and the slice layout are fixed. A design that needs a new kind or another change to `architecture.json` goes into its own pull request against main for the owner. Keep working on what doesn't depend on it.
- The gate files are gates the owner named. A failing `./check` is a finding in the code, never a broken tool or a flaky verifier. If you think a check is wrong, open a pull request against main that fixes it, link it in your report, and keep working. Never loosen a check inside a feature pull request.
- A rule table, a lint setting, or a skill that a workflow writes for this repository is a gate-file change, so it goes into its own pull request against main. A new check in `checks/` and a verification skill in `.claude/skills/verify-*/` are not gate files.
- Run the `architecture-reviewer` subagent before you open a pull request, in addition to the reviews the workflow runs.
