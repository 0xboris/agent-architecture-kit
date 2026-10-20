# Agent architecture kit

This kit sets up a codebase that coding agents can extend without eroding it. It has two halves:

- **A shared architecture.** Horizontal layers, vertical feature slices, ports, middleware, and a composition root, written down in `docs/ARCHITECTURE.md`.
- **Tooling that enforces it.** A check fails on wrong imports and misplaced code, a reference slice shows agents the shape of new code, and Claude Code integration runs the check before an agent finishes.

It works for Swift apps built from local packages, and for Go and TypeScript services. It does not depend on a framework: frameworks are allowed per module kind in `architecture.json`, and the reference slice shows how the project uses them.

## What is in the kit

```
docs/ARCHITECTURE.md              the architecture, for agents and people (copied into each project)
docs/architecture/<language>.md   the language rules for Swift, Go, and TypeScript
tools/archcheck.py                the architecture check
tools/new.py                      creates projects and adopts existing ones (runs from the kit only)
tools/agent-stop-check.sh         Claude Code Stop hook that runs ./check
templates/common/                 AGENTS.md, CLAUDE.md, GLOSSARY.md, .claude/, CODEOWNERS
templates/swift|go|typescript/    a working project with the Notes reference slice and its stack.md
```

Each project receives:

- **The docs.** `docs/ARCHITECTURE.md`, its language guide, `docs/architecture/stack.md` for the project's libraries, and the generated module map.
- **The tools.** `tools/archcheck.py`, the Stop hook script, and `./check`, the one command that verifies everything.
- **The configuration.** `architecture.json` maps directories to module kinds and sets the rules for each kind, and `architecture-baseline.json` holds the violations you have accepted.
- **Agent instructions.** `AGENTS.md`, which names the reference slice, a `CLAUDE.md` that imports it, and a `README.md` to fill in with what the project does.
- **Claude Code integration in `.claude/`.** The Stop hook, a path-scoped rule that points agents to the docs, the `new-slice` and `new-port` checklists, and the `architecture-reviewer` subagent.
- **Code owners.** `.github/CODEOWNERS` covers the gate files and the composition root.
- **CI.** `.github/workflows/check.yml` runs `./check`.
- **The Notes reference slice.** A small working feature with a domain rule, a port, middleware, a slice, an adapter, stubs, adapter tests against the real file system, and a composition test.

## Requirements

- Python 3.9 or later, for the check and `new.py`. Both use only the standard library.
- Git, for the Stop hook.
- Swift projects: a Swift 6 toolchain and Xcode.
- Go projects: Go 1.24 or later.
- TypeScript projects: Node 24 or later. The template uses TypeScript 7 for type checking, and Node runs the `.ts` files directly. It lints with oxlint, whose type-aware rules run on oxlint-tsgolint, which is built on TypeScript 7. typescript-eslint supports only TypeScript below 6.1 as of 2026-10-19, so it does not work with TypeScript 7.

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

The destination must be empty or hold only `.git`, so you can run `init` in a freshly cloned empty repository.

Then, in the new folder:

1. Run `./check`. It passes on a fresh project.
2. Swift only: create the Xcode app project.
   - In Xcode, create an iOS App project named like `--name` and save it in the project folder.
   - Delete the `ContentView.swift` and `<Name>App.swift` files that Xcode generated, and add `App/<Name>App.swift` to the app target.
   - Use File > Add Package Dependencies > Add Local to add `Packages/AppModules`, and link the `AppComposition` library to the app target.
   - Add an iOS build of the app to CI, as `docs/architecture/swift.md` describes.
3. Commit, push, and set up branch protection on `main`: require pull requests, require code-owner reviews, and require the `check` workflow.
4. To use other libraries than the template's, follow "Changing a library" in `docs/architecture/stack.md`. Rewrite the Notes slice with them first, so agents copy the right patterns.
5. Let agents use the Notes slice as their reference. Once your first real slice exists and follows the same patterns, delete the Notes slice, its tests, its wiring, and its glossary entries, and name the new slice as the reference in `AGENTS.md`. If the product itself has notes, its notes feature grows from the Notes slice, which stays the reference.

Agents should open pull requests under their own account or a GitHub App. GitHub does not let the author of a pull request approve it, so if agents push as you, the code-owner review cannot happen.

## Adopt the kit in an existing project

```bash
python3 path/to/kit/tools/new.py adopt go ~/Dev/legacy-service --owner @your-github-user
```

`adopt` adds the docs, tools, agent instructions, `.claude/`, and `CODEOWNERS` without overwriting files that exist. It adds `architecture.json` and `docs/architecture/stack.md` from the language template. It writes `check` if the project has none, or `check.kit` if it does. Then:

1. **Map every directory to a kind.** Edit `modules` in `architecture.json` until `python3 tools/archcheck.py` reports no unmapped file. A module path is a directory; `{"path": "."}` maps the repository root, for example a Go `main.go`. Pick the kind by what the code does today: handlers are `ui`, database code is `adapter`, and models and business logic are `domain`.
2. **Accept what exists.** Run `python3 tools/archcheck.py --write-baseline`. From now on the check fails only on new violations.
3. **Wire up `./check`.** Make it run your real build and tests. If you got `check.kit`, merge its architecture steps into your existing check.
4. **Turn on the gates.** Add `@AGENTS.md` as the first line of an existing `CLAUDE.md`, commit `.claude/`, set the owner in `CODEOWNERS`, and enable branch protection as for a new project.
5. **Describe the stack and pick a reference.** Rewrite `docs/architecture/stack.md` for the project's libraries, and allow them per kind in `architecture.json`. Name a reference slice in `AGENTS.md`: the existing slice that best follows the architecture, or one you rebuild in that shape, using the kit's Notes slice as the model.
6. **Write the glossary.** List the business concepts the code already uses, one heading each.
7. **Put new work in the new shape.** New capabilities become slices in the shape of the reference slice. New rules go into the domain. New I/O goes behind ports.
8. **Fix old code as you touch it.** When a change touches a module with violations, fix them in a separate commit and run `--write-baseline` to lower the counts. The baseline only ever goes down.

The language guides describe the template layout. In a project with a different layout, either move toward the template layout over time, or keep the existing layout mapped in `architecture.json` and name as the reference the slice that follows the architecture best.

## Day to day

The Stop hook runs `./check` with the PATH of the Claude Code session, so the session needs the project's toolchain, such as Node 24 and the package manager, on its PATH.

Agents read `AGENTS.md` at the start of each task and the architecture docs when they touch code. They copy the structure of the reference slice, using the `new-slice` and `new-port` checklists, run `./check` after each step, and cannot finish a task while the check fails. Before a pull request, they ask the `architecture-reviewer` subagent for the judgment calls the check cannot make.

Your review stays small:

- **Diffs to gate files.** `CODEOWNERS` sends you every change to `architecture.json`, the baseline, `check`, `tools/`, `.claude/`, `.github/`, and the instruction files. An agent that weakens a check shows up here.
- **Diffs to the composition root.** Legitimate changes are a few lines of wiring. Anything larger is feature code in the wrong place.
- **Ports and stored formats.** New ports, renamed stored or sent fields, and migrations deserve a careful look, because no test catches a format that only breaks old data.

When agents keep making the same mistake, improve the tooling instead of adding prose. Preferred fixes, in order:

1. A check, with the fix in its message.
2. A better reference slice.
3. A sentence in `docs/ARCHITECTURE.md`, only when nothing else can carry it.

Upgrade a project to a newer kit by copying `tools/archcheck.py`, `tools/agent-stop-check.sh`, `docs/ARCHITECTURE.md`, and the project's language guide from `docs/architecture/` out of the kit, then running `./check`. The kit owns these files, so the project does not edit them. Read the diff of the docs: a new rule may need a change in the project. Projects created before 2026-10-15 also have `tools/new.py`, which they can delete: new code now copies the reference slice.

TypeScript projects created before 2026-10-19 have no linter. To add it:

1. Copy `templates/typescript/.oxlintrc.json` to the project root, and change the paths in its `overrides` to the project's source and domain directories. In a repository with several apps, `docs/architecture/typescript.md` says which paths to use.
2. Add `oxlint` and `oxlint-tsgolint` to `devDependencies`, at the versions in `templates/typescript/package.json`. A project on TypeScript 6 or below can keep ESLint with typescript-eslint instead; the rules in the language guide hold either way.
3. Add `step lint npx oxlint` to `./check`, before the type check, and add `/.oxlintrc.json` to `.github/CODEOWNERS`.
4. Run `npx oxlint` and fix what it reports. Most findings in tests are stubs written as `async` functions without `await`, and JSON responses read as `any`.
5. Describe the linter in `docs/architecture/stack.md`, as the template's copy does.

## Frameworks

The architecture names no framework. The domain and use cases import none, so a framework can only sit in UI, adapters, the composition root, and tests. Each project allows its frameworks per kind in `architecture.json`, describes them in `docs/architecture/stack.md`, and shows how to use them in the reference slice. The templates use only each language's standard library. To switch to other libraries, follow "Changing a library" in `docs/architecture/stack.md`.

Frameworks that stay in one layer fit, such as HTTP routers, ORMs and query builders inside an adapter, job queues, HTTP clients, test runners, and UI libraries like React or SwiftUI. None of them has been tried with the kit yet.

Frameworks that want to own the structure fit badly:

- **File-based full-stack frameworks, such as Next.js.** The framework fixes the folder layout, and server actions put data access in UI files. The check fights the framework.
- **Frameworks with their own dependency injection container, such as NestJS.** The kit wires dependencies by hand in the composition root and allows no service locators. NestJS's decorators also do not work with Node's type stripping, which the TypeScript template uses.
- **Active-record ORMs, where database models are the business model.** They work only if the adapter maps its models to domain types, as the Swift template's `NoteRecord` does.

## Configuring `architecture.json`

Lines that start with `//` are comments.

- **`language`.** `swift`, `go`, or `typescript`.
- **`sourceRoots`.** Directories to scan. The templates scan the whole repository (`.`), so a source file outside every module fails as unmapped.
- **`testFiles` and `ignore`.** Glob patterns, matched against paths from the repository root. `*` stays within one directory and `**` crosses directories, so `*.config.ts` matches only files in the root. Test files are exempt from the import rules.
- **`glossary`.** The glossary file. Its level-2 headings are the terms banned from modules with `"bannedTerms": "glossary"`. The check splits identifiers into words, so the heading "API key" matches `apiKey`, `APIKey`, `api_key`, and `apiKeys`. A one-word heading that is also a common word, such as "Sync", matches identifiers like `readFileSync`, so prefer specific headings such as "Sync run".
- **`modules`.** Maps directories to kinds.
  - `path` may use `*` for one directory level, and `{1}` in `name` or `slice` inserts what the first `*` matched.
  - Swift module names must match the target names, because Swift imports name targets.
  - `app` names the app a module belongs to, in a repository with several apps. Modules of different apps may not import each other. A module without `app`, such as the shared domain, may be imported from every app.
- **`kinds`.** Sets the rules for each kind:
  - `mayImport`: kinds this kind may import. `*` means every kind except test support, and `usecases@same-slice` allows only the importing module's own slice.
  - `external`: `allow` and `deny` patterns for frameworks and packages. In Go, `std` means the standard library.
  - `forbiddenCalls`: regular expressions, or `@set` references, with the fix to show.
  - `bannedTerms`: `"glossary"` or a list of words.
  - `composition`: `allowedFiles`, `controlFlowAllowedIn`, `controlFlowAllowedPatterns`, and `maxLines`.
  - `publicEntry`: file names, such as `["index.ts"]`. Other modules may import a module of this kind only through one of these files. TypeScript only.
- **`typescript.aliases`.** Maps import names to directories, such as a workspace package `@acme/domain` to `packages/domain/src`, so that the check resolves those imports to modules.
- **`externalSets` and `forbiddenCallSets`.** Named lists that kinds refer to as `@name`. An entry with a slash, such as `@hono/node-server` or `@hono/*`, is a scoped npm package, not a set. A reference to a set that does not exist fails the check.

To allow a library in the domain, such as a decimal type, add it to the domain's `external.allow`. That is a deliberate change to a gate file, so it goes through your review.

## What was tested, and what was not

Tested on macOS on 2026-10-14 with Python 3.14, Swift 6.4 and Xcode 27, Go 1.27, Node 26, and TypeScript 7.0.2:

- **New projects.** For each language, `init` creates a project whose `./check` passes. That covers the architecture check, the build, the type check, and the tests.
- **Violations.** The check reports and explains these:
  - imports across slices
  - UI importing adapters
  - frameworks in the domain
  - I/O calls in the domain and UI
  - glossary terms in utilities
  - feature code and control flow in the composition root
  - unmapped files
  - cycles
  - imports of files that belong to no module, such as configuration files
  - production code that imports test files
- **Baseline.** Accepted violations pass, new ones fail, and fixed ones trigger a note to lower the baseline.
- **Stop hook.** It blocks the first stop while the check fails, allows the second stop, and does nothing when no files changed. I tested it by running the script directly.
- **Adoption.** `adopt` worked on a small legacy Go project: mapping, baseline, and a new violation failing.

Retested on Linux on 2026-10-15, after the generators were removed and the fakes and contracts were replaced by stubs and adapter tests, with Python 3.13, Go 1.24.7, Node 22.22, and TypeScript 7.0.2:

- **New projects.** `init go` and `init typescript` create projects whose `./check` passes.
- **Adoption.** `adopt go` on a small Go project adds `docs/architecture/stack.md` and keeps existing files.

Retested on Linux on 2026-10-15 with Node 24.22, after fixes from a test setup by a fresh agent:

- **`init` in an empty clone.** `init typescript` and `init go` work in a directory that holds only `.git`, and `./check` passes, including the install step from an empty `node_modules`.
- **Architecture check.** A `.js` file in the domain is checked like a `.ts` file. `@hono/*` in `external.allow` allows `@hono/node-server`. A reference to an unknown set fails with a configuration error.
- **Stop hook.** In a repository without commits, it runs `./check` when files exist.

Retested on Linux on 2026-10-15 with Node 24.22, after a second test setup by a fresh agent:

- **Architecture check.** Glossary terms match identifiers by words, including acronyms and plurals. An import of an unmapped file and an import of a test file from production code both fail. The check passes on all three templates.
- **New projects.** `init typescript` and `init go` pass `./check`.

On 2026-10-19, a test project was moved to the layout for several apps in one repository: an API, a React web app, and a shared domain package. Tested there:

- **The check.** It reports an import between apps, an import into a slice's UI that bypasses `ui/index.ts`, a screen that imports use cases, and a package import in the shared domain.
- **The contract.** `./check` fails when `openapi.json` no longer matches the API's routes.
- **The app.** The web app, in Chromium against the API on a Postgres-compatible server (PGlite), creates, lists, and opens notes. An empty title is rejected in the browser before any request.

Retested on Linux on 2026-10-19 with Node 24.22, TypeScript 7.0.2, oxlint 1.88.0, and oxlint-tsgolint 7.0.2004:

- **Lint.** `init typescript` creates a project whose `./check` passes, including the new lint step. Lint fails on `'x' as NoteTitle` in a slice's UI, passes it in the domain, fails on `JSON.parse` assigned to a typed value, and allows `as const`.
- **Adoption.** `adopt typescript` adds `.oxlintrc.json` and keeps an existing one.
- **Several apps.** The test project with an API, a React web app, and a shared domain moved from TypeScript 6 and ESLint to TypeScript 7 and oxlint, and `./check` passes: the contract, lint, type checks of every package, Vitest, and the Vite build. Lint fails on an assertion in a slice's `.tsx` file and on a list item without a key, and allows assertions in the shared domain and in tests. openapi-typescript, which needs TypeScript's JavaScript API, runs with TypeScript 5.9 from a package of its own and generates the same client. The hooks rule runs only on the React app, because the API's `useCases()` wiring helper is not a hook.
- **A fresh agent.** Given only the kit and the stack, a new agent built an API, a web app, and a shared domain with notes and users. It arrived at the same design, with an author slot that a screen fills and the edit rule in the shared domain, and `./check` passed. The gaps it reported are fixed: the steps from one app to several, an `architecture.json` for several apps, the React hooks rule, the shared domain's tests, `openapi.ts` in `allowedFiles`, and the fix message for an import between slices whose kinds have project names, such as `web-ui`.

Not tested:

- **A template for several apps.** `init` still creates one app. "From one app to several" in `docs/architecture/typescript.md` gives the steps and an `architecture.json` for an API, a web app, and a shared domain.

- **The Swift template after 2026-10-15.** Its new `StubNoteStore` and the rewritten tests have not been compiled. Run `./check` on macOS before relying on them.

- **Claude Code in a real session.** Nobody has watched it load the Stop hook, the skills, the subagent, or the path-scoped rule. The formats follow the Claude Code documentation as of 2026-10-14.
- **GitHub.** The GitHub Actions workflows were not run, and `CODEOWNERS` enforcement was not tried.
- **The Xcode app.** The project steps for Swift and an iOS build of the app.
- **Larger code.** Adoption in a real, larger codebase, and the check's speed on a large repository.
- **Other setups.** TypeScript path aliases, TypeScript frontends or frameworks such as Express or Fastify, Core Data or SwiftData adapters, and Windows.
