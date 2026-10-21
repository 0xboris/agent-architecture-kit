# Agent instructions

`README.md` describes what the project does. This codebase follows the architecture in `docs/ARCHITECTURE.md`. Read it before you add or move code. `docs/architecture/__LANGUAGE__.md` shows how each part looks in this language, `docs/architecture/stack.md` names the libraries this project uses, and `docs/architecture/modules.md` lists every module with its kind.

## Reference slice

The reference slice is **Notes**. Copy its structure when you add a slice, a use case, a port, an adapter, or their tests. The owner replaces Notes with the first real slice that follows the same patterns, and changes this line.

## Commands

- `./check` verifies everything: the architecture, the build, the types, and the tests. Run it after each step. A task is done only when it passes.
- The `new-slice` and `new-port` skills list the files that a new slice or port needs.

## How to work here

- Copy the structure of the reference slice, or of the closest existing code that follows it.
- When the check reports a violation, apply the fix it names. Never change a gate file to make a check pass. `.github/CODEOWNERS` lists the gate files: `architecture.json`, the baseline, `check`, `tools/`, `.claude/`, `.github/`, the instruction files, the architecture docs, and the compiler, linter, and test runner settings. Changes to them need the owner.
- Use the names in `GLOSSARY.md` for business concepts, and add new concepts to it.
- Every behavior change gets a test that fails without the change. A bug fix starts with a test that reproduces the bug.
- End with a short report: what changed, what you could not verify, and follow-ups you noticed but did not do.

## Skills and plugins

Workflow skills and plugins, such as pstack, run here under this file and `docs/ARCHITECTURE.md`. Where their advice differs, these files win.

- The module kinds and the slice layout are fixed. A design that needs a new kind or another change to `architecture.json` is the owner's decision, so propose it and wait.
- The gate files are gates the owner named. A failing `./check` is a finding in the code, never a broken tool or a flaky verifier. If you think a check is wrong, say so in your report and leave the check as it is.
- Rules, checks, and skills that a workflow writes for this repository, such as a rule table, a lint, or a verification skill, are gate-file changes. Put them in their own pull request against main for the owner. On any other branch, CI rejects gate-file changes.
- Run the `architecture-reviewer` subagent before you open a pull request, in addition to the reviews the workflow runs.
