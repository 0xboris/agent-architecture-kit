# Agent instructions

`README.md` describes what the project does. This codebase follows the architecture in `docs/ARCHITECTURE.md`. Read it before you add or move code. `docs/architecture/__LANGUAGE__.md` shows how each part looks in this language, `docs/architecture/stack.md` names the libraries this project uses, `docs/architecture/modules.md` lists every module with its kind, and `docs/architecture/where-code-goes.md` says which module new code belongs in.

## Reference slice

The reference slice is **Notes**. Copy its structure when you add a slice, a use case, a port, an adapter, or their tests. The owner replaces Notes with the first real slice that follows the same patterns, and changes this line.

## Commands

- `./check` runs the architecture check, the build, the types, the tests, and the project checks in `checks/`. Run it after each step. A change is done when the check passes and you have shown the change working in the running app.
- The `new-slice` and `new-port` skills list the files that a new slice or port needs.

## How to work here

- Copy the structure of the reference slice, or of the closest existing code that follows it.
- When the check reports a violation, apply the fix it names. A failing `./check` is a finding in the code, never a flaky tool.
- Use the names in `GLOSSARY.md` for business concepts, and add new concepts to it.
- A bug fix starts with a failing reproduction, committed before the fix: a test when a cheap one exists, otherwise a script or a recorded run against the running app.
- Change an API inside the repository in one step. Move every caller and delete the old form in the same change. Stored formats and wire contracts change by expanding first, as `docs/ARCHITECTURE.md` describes.
- Every review of a change here, by a person or by an agent such as the reviewers of `/pstack:interrogate`, also answers the questions in `docs/architecture/review.md`.

## Gates

`.github/CODEOWNERS` lists the gate files: `architecture.json`, `check`, `tools/`, `.claude/`, `.github/`, the instruction files, the architecture docs, and the compiler, linter, and test runner settings. A change to them can loosen a check, so the owner reviews it.

- Never change a gate file to make a check pass, and never loosen a check inside a feature pull request.
- A gate change, such as a new module kind, a fix to a check you think is wrong, a lint setting, a row in the table below, or a skill, goes into its own pull request against main. Link it in your report and keep working on what doesn't depend on it.
- To tighten a rule, add an executable to `checks/` whose message names the fix, or lower the baseline with `python3 tools/archcheck.py --write-baseline` after you fix a violation. Neither needs the owner. Neither does a verification skill in `.claude/skills/verify-*/`.

## Rules and what enforces them

When agents keep making the same mistake, fix it at the highest level that works: the architecture, then a type, then a check whose message names the fix, then a test, and a row here last. A rule whose only enforcement is review is a candidate for a check.

| Rule | Enforced by |
| --- | --- |
| Modules import only the kinds that `architecture.json` allows, and slices never import each other. | `tools/archcheck.py` |
| Every source file belongs to a module, a test, or a script. | `tools/archcheck.py` |
| The domain, use cases, and UI perform no I/O, and take the time and ids from ports. | `tools/archcheck.py`, `forbiddenCalls` |
| UI reaches ports only through its slice's use cases. | `tools/archcheck.py`, `forbidPorts` |
| Utilities and shared UI use no business terms. | `tools/archcheck.py`, `bannedTerms` from `GLOSSARY.md` |
| The composition root holds only wiring. | `tools/archcheck.py`, `composition` |
| Violations that existed at adoption only go down. | `architecture-baseline.json`, `tools/gateguard.py` |
| A stored format still loads data that an earlier version wrote. | The adapter's test on its committed file in that format |
| A use case makes no business decision, and each rule exists once. | Review, `docs/architecture/review.md` |
