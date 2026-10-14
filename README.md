# Agent architecture kit

This kit sets up a codebase that coding agents can extend without eroding it. It has two halves:

- **A shared architecture.** Horizontal layers, vertical feature slices, ports, middleware, and a composition root, written down in `docs/ARCHITECTURE.md`.
- **Tooling that enforces it.** A check fails on wrong imports and misplaced code, generators create new code in the right shape, and Claude Code integration runs the check before an agent finishes.

It works for Swift apps built from local packages, and for Go and TypeScript services.

## What is in the kit

```
docs/ARCHITECTURE.md              the architecture, for agents and people (copied into each project)
docs/architecture/<language>.md   how the architecture looks in Swift, Go, and TypeScript
tools/archcheck.py                the architecture check
tools/new.py                      creates projects, adopts existing ones, adds slices, use cases, and ports
tools/agent-stop-check.sh         Claude Code Stop hook that runs ./check
templates/common/                 AGENTS.md, CLAUDE.md, GLOSSARY.md, .claude/, CODEOWNERS
templates/swift|go|typescript/    a working project with the Notes reference slice
```

Each project receives:

- **The docs.** `docs/ARCHITECTURE.md`, its language guide, and the generated module map.
- **The tools.** `tools/` and `./check`, the one command that verifies everything.
- **The configuration.** `architecture.json` maps directories to module kinds and sets the rules for each kind, and `architecture-baseline.json` holds the violations you have accepted.
- **Agent instructions.** `AGENTS.md`, plus a `CLAUDE.md` that imports it.
- **Claude Code integration in `.claude/`.** The Stop hook, a path-scoped rule that points agents to the docs, the `new-slice` and `new-port` skills, and the `architecture-reviewer` subagent.
- **Code owners.** `.github/CODEOWNERS` covers the gate files and the composition root.
- **CI.** `.github/workflows/check.yml` runs `./check`.
- **The Notes reference slice.** A small working feature with a domain rule, a port, middleware, a slice, an adapter, fakes, contract tests, and a composition test.

## Requirements

- Python 3.9 or later, for the check and the generator. Both use only the standard library.
- Git, for the Stop hook.
- Swift projects: a Swift 6 toolchain and Xcode.
- Go projects: Go 1.24 or later.
- TypeScript projects: Node 24 or later. The template uses TypeScript 7 for type checking, and Node runs the `.ts` files directly.

## Start a new project

```bash
python3 path/to/kit/tools/new.py init swift ~/Dev/expense-tracker --name ExpenseTracker --owner @your-github-user
```

```bash
python3 path/to/kit/tools/new.py init go ~/Dev/budget-service --name BudgetService --module github.com/you/budget-service --owner @your-github-user
```

```bash
python3 path/to/kit/tools/new.py init typescript ~/Dev/budget-api --name BudgetApi --owner @your-github-user
```

Then, in the new folder:

1. Run `./check`. It passes on a fresh project.
2. Swift only: create the Xcode app project.
   - In Xcode, create an iOS App project named like `--name` and save it in the project folder.
   - Delete the `ContentView.swift` and `<Name>App.swift` files that Xcode generated, and add `App/<Name>App.swift` to the app target.
   - Use File > Add Package Dependencies > Add Local to add `Packages/AppModules`, and link the `AppComposition` library to the app target.
   - Add an iOS build of the app to CI, as `docs/architecture/swift.md` describes.
3. Commit, push, and set up branch protection on `main`: require pull requests, require code-owner reviews, and require the `check` workflow.
4. Let agents use the Notes slice as their reference. Once your first real slice exists and follows the same patterns, delete the Notes slice, its tests, its wiring, and its glossary entries.

Agents should open pull requests under their own account or a GitHub App. GitHub does not let the author of a pull request approve it, so if agents push as you, the code-owner review cannot happen.

## Adopt the kit in an existing project

```bash
python3 path/to/kit/tools/new.py adopt go ~/Dev/legacy-service --owner @your-github-user
```

`adopt` adds the docs, tools, agent instructions, `.claude/`, and `CODEOWNERS` without overwriting files that exist. It adds `architecture.json` from the language template. It writes `check` if the project has none, or `check.kit` if it does. Then:

1. **Map every directory to a kind.** Edit `modules` in `architecture.json` until `python3 tools/archcheck.py` reports no unmapped file. A module path is a directory; `{"path": "."}` maps the repository root, for example a Go `main.go`. Pick the kind by what the code does today: handlers are `ui`, database code is `adapter`, and models and business logic are `domain`.
2. **Accept what exists.** Run `python3 tools/archcheck.py --write-baseline`. From now on the check fails only on new violations.
3. **Wire up `./check`.** Make it run your real build and tests. If you got `check.kit`, merge its architecture steps into your existing check.
4. **Turn on the gates.** Add `@AGENTS.md` as the first line of an existing `CLAUDE.md`, commit `.claude/`, set the owner in `CODEOWNERS`, and enable branch protection as for a new project.
5. **Write the glossary.** List the business concepts the code already uses, one heading each.
6. **Put new work in the new shape.** New capabilities become slices with `tools/new.py`. New rules go into the domain. New I/O goes behind ports.
7. **Fix old code as you touch it.** When a change touches a module with violations, fix them in a separate commit and run `--write-baseline` to lower the counts. The baseline only ever goes down.

The generators assume the template layout. In a project with a different layout, either move toward the template layout over time, or create slices by hand and copy the structure of the reference slice from the kit.

## Day to day

Agents read `AGENTS.md` at the start of each task and the architecture docs when they touch code. They create structure with the generators, run `./check` after each step, and cannot finish a task while the check fails. Before a pull request, they ask the `architecture-reviewer` subagent for the judgment calls the check cannot make.

Your review stays small:

- **Diffs to gate files.** `CODEOWNERS` sends you every change to `architecture.json`, the baseline, `check`, `tools/`, `.claude/`, `.github/`, and the instruction files. An agent that weakens a check shows up here.
- **Diffs to the composition root.** Legitimate changes are a few lines of wiring. Anything larger is feature code in the wrong place.
- **Ports and stored formats.** New ports, renamed stored or sent fields, and migrations deserve a careful look, because no test catches a format that only breaks old data.

When agents keep making the same mistake, improve the tooling instead of adding prose. Preferred fixes, in order:

1. A check, with the fix in its message.
2. A generator.
3. A better reference implementation.
4. A sentence in `docs/ARCHITECTURE.md`, only when nothing else can carry it.

Upgrade a project to a newer kit by copying `tools/archcheck.py`, `tools/new.py`, and `tools/agent-stop-check.sh` from the kit, then running `./check`.

## Configuring `architecture.json`

Lines that start with `//` are comments.

- **`language`.** `swift`, `go`, or `typescript`.
- **`sourceRoots`.** Directories to scan. The templates scan the whole repository (`.`), so a source file outside every module fails as unmapped.
- **`testFiles` and `ignore`.** Glob patterns. Test files are exempt from the import rules.
- **`glossary`.** The glossary file. Its level-2 headings are the terms banned from modules with `"bannedTerms": "glossary"`.
- **`modules`.** Maps directories to kinds.
  - `path` may use `*` for one directory level, and `{1}` in `name` or `slice` inserts what the first `*` matched.
  - Swift module names must match the target names, because Swift imports name targets.
- **`kinds`.** Sets the rules for each kind:
  - `mayImport`: kinds this kind may import. `*` means every kind except test support, and `usecases@same-slice` allows only the importing module's own slice.
  - `external`: `allow` and `deny` patterns for frameworks and packages. In Go, `std` means the standard library.
  - `forbiddenCalls`: regular expressions, or `@set` references, with the fix to show.
  - `bannedTerms`: `"glossary"` or a list of words.
  - `composition`: `allowedFiles`, `controlFlowAllowedIn`, `controlFlowAllowedPatterns`, and `maxLines`.
- **`externalSets` and `forbiddenCallSets`.** Named lists that kinds refer to as `@name`.

To allow a library in the domain, such as a decimal type, add it to the domain's `external.allow`. That is a deliberate change to a gate file, so it goes through your review.

## What was tested, and what was not

Tested on macOS on 2026-10-14 with Python 3.14, Swift 6.4 and Xcode 27, Go 1.27, Node 26, and TypeScript 7.0.2:

- **New projects.** For each language, `init` creates a project whose `./check` passes. That covers the architecture check, the build, the type check, and the tests.
- **Scaffolding.** In each language, `slice`, `usecase`, and `port`, including multi-word names, produce code that passes `./check`.
- **Violations.** The check reports and explains these:
  - imports across slices
  - UI importing adapters
  - frameworks in the domain
  - I/O calls in the domain and UI
  - glossary terms in utilities
  - feature code and control flow in the composition root
  - unmapped files
  - cycles
- **Baseline.** Accepted violations pass, new ones fail, and fixed ones trigger a note to lower the baseline.
- **Stop hook.** It blocks the first stop while the check fails, allows the second stop, and does nothing when no files changed. I tested it by running the script directly.
- **Adoption.** `adopt` worked on a small legacy Go project: mapping, baseline, and a new violation failing.

Not tested:

- **Claude Code in a real session.** Nobody has watched it load the Stop hook, the skills, the subagent, or the path-scoped rule. The formats follow the Claude Code documentation as of 2026-10-14.
- **GitHub.** The GitHub Actions workflows were not run, and `CODEOWNERS` enforcement was not tried.
- **The Xcode app.** The project steps for Swift and an iOS build of the app.
- **Larger code.** Adoption in a real, larger codebase, and the check's speed on a large repository.
- **Other setups.** TypeScript path aliases, TypeScript frontends or frameworks such as Express or Fastify, Core Data or SwiftData adapters, and Windows.
