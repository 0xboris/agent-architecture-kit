# Agent instructions

`README.md` describes what the project does. This codebase follows the architecture in `docs/ARCHITECTURE.md`. Read it before you add or move code. `docs/architecture/__LANGUAGE__.md` shows how each part looks in this language, `docs/architecture/stack.md` names the libraries this project uses, and `docs/architecture/modules.md` lists every module with its kind.

## Reference slice

The reference slice is **Notes**. Copy its structure when you add a slice, a use case, a port, an adapter, or their tests. The owner replaces Notes with the first real slice that follows the same patterns, and changes this line.

## Commands

- `./check` verifies everything: the architecture, the build, the types, and the tests. Run it after each step. A task is done only when it passes.
- The `new-slice` and `new-port` skills list the files that a new slice or port needs.

## How to work here

- Copy the structure of the reference slice, or of the closest existing code that follows it.
- When the check reports a violation, apply the fix it names. Never loosen a rule, silence the linter, or skip a test to make a check pass.
- Use the names in `GLOSSARY.md` for business concepts, and add new concepts to it.
- Every behavior change gets a test that fails without the change. A bug fix starts with a test that reproduces the bug.
- End with a short report: what changed, what you could not verify, and follow-ups you noticed but did not do.

## Gate files and merging

- Change any file the task needs in your pull request, including docs, `README.md`, and gate files. Never hand the owner a patch to apply instead.
- Gate files define the checks. Two kinds of change to them wait for the owner's approval:
  - Any change to a file that `.github/CODEOWNERS` lists: `check`, `tools/`, `.claude/`, `.github/`, the instruction files, `docs/ARCHITECTURE.md` and the language guide, and the compiler, linter, and test runner settings.
  - A change that loosens a rule in `architecture.json`, the baseline, or a `package.json`, or a new comment that silences the linter or skips a test. `python3 tools/gatecheck.py` lists them.
- A stricter rule or a lower baseline needs no approval.
- Put a change that waits for the owner in a pull request of its own, with the reason in its description, so other work does not wait on it.
- A pull request may merge once `check` and `gates` pass on its current head, and an agent that did not write it has run the architecture-reviewer subagent on it and found no problems. Merge with a squash merge, and never bypass a required check or review.
