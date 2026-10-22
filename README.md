# Agent architecture kit

This kit sets up a codebase that coding agents can extend without eroding it. It has two halves:

- **A shared architecture.** Horizontal layers, vertical feature slices, ports, middleware, and a composition root, written down in `docs/ARCHITECTURE.md`.
- **Tooling that enforces it.** A check fails on wrong imports and misplaced code, a reference slice shows agents the shape of new code, and Claude Code integration runs the check before an agent finishes.

It works for Swift apps built from local packages, and for Go and TypeScript services. It does not depend on a framework. Frameworks are allowed per module kind in `architecture.json`, and the reference slice shows how the project uses them.

## What is in the kit

```
docs/ARCHITECTURE.md              the architecture, for agents and people (copied into each project)
docs/architecture/<language>.md   the language rules for Swift, Go, and TypeScript
docs/architecture/where-code-goes.md   which module new code belongs in
docs/architecture/review.md       the questions every review answers
tools/archcheck.py                the architecture check
tools/new.py                      creates projects and adopts existing ones (runs from the kit only)
tools/agent-stop-check.sh         Claude Code Stop hook that runs ./check
tools/gateguard.py                CI check that keeps the baseline and the project checks from loosening
templates/common/                 AGENTS.md, CLAUDE.md, GLOSSARY.md, .claude/, CODEOWNERS
templates/swift|go|typescript/    a working project with the Notes reference slice and its stack.md
examples/                         pages that show the architecture in example projects (not copied into projects)
```

Each project receives:

- **The docs.** `docs/ARCHITECTURE.md`, its language guide, `where-code-goes.md`, the review questions in `review.md`, `docs/architecture/stack.md` for the project's libraries, and the generated module map.
- **The tools.** `tools/archcheck.py`, the Stop hook script, the gate guard, and `./check`, the one command that verifies everything. It also runs every executable in `checks/`, where agents add project checks.
- **The configuration.** `architecture.json` maps directories to module kinds and sets the rules for each kind, and `architecture-baseline.json` holds the violations you have accepted.
- **Agent instructions.** `AGENTS.md`, which names the reference slice, sends every review to the review questions, and pairs each rule with what enforces it. A `CLAUDE.md` that imports it, and a `README.md` to fill in with what the project does.
- **Claude Code integration in `.claude/`.** The Stop hook, a path-scoped rule that points agents to the docs, the `new-slice` and `new-port` checklists, the `deslop` skill, and pstack, enabled from its upstream marketplace.
- **Code owners.** `.github/CODEOWNERS` covers the gate files, which define the checks.
- **CI.** `.github/workflows/check.yml` runs `./check` and, on every pull request, the gate guard. The guard fails when the baseline rises or an existing project check changes or goes away.
- **A verification skill, for Go and TypeScript.** `.claude/skills/verify-<name>/` starts the service on a temporary data directory, sends requests to it, and keeps each request and response as evidence. Its feature map covers the Notes slice and grows with the project. For Swift, generate one with `/pstack:create-verification-skill` once the Xcode project exists.
- **The Notes reference slice.** A small working feature with a domain rule, a port, middleware, a slice, an adapter, tests that run against the real file store in a temporary directory, a committed sample of the stored format with a test that loads it, and a composition test.

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
   - Run `/pstack:create-verification-skill` to get a skill that drives the app in the simulator and keeps the evidence.
3. Commit, push, and set up branch protection on `main`: require pull requests, require code-owner reviews, and require the `check` workflow.
4. To use other libraries than the template's, follow "Changing a library" in `docs/architecture/stack.md`. Rewrite the Notes slice with them first, so agents copy the right patterns.
5. Let agents use the Notes slice as their reference. Once your first real slice exists and follows the same patterns, delete the Notes slice, its tests, its wiring, and its glossary entries, and name the new slice as the reference in `AGENTS.md`. If the product itself has notes, its notes feature grows from the Notes slice, which stays the reference.

Agents should open pull requests under their own account or a GitHub App. GitHub does not let the author of a pull request approve it, so if agents push as you, the code-owner review cannot happen.

## Adopt the kit in an existing project

```bash
python3 path/to/kit/tools/new.py adopt go ~/Dev/legacy-service --owner @your-github-user
```

`adopt` adds the docs, tools, agent instructions, `.claude/`, and `CODEOWNERS` without overwriting files that exist. It adds `architecture.json` and `docs/architecture/stack.md` from the language template. It writes `check` if the project has none, or `check.kit` if it does. Then:

1. **Map every directory to a kind.** Edit `modules` in `architecture.json` until `python3 tools/archcheck.py` reports no unmapped file. A module path is a directory, and `{"path": "."}` maps the repository root, for example a Go `main.go`. Pick the kind by what the code does today: handlers are `ui`, database code is `adapter`, and models and business logic are `domain`.
2. **Accept what exists.** Run `python3 tools/archcheck.py --write-baseline`. From now on the check fails only on new violations.
3. **Wire up `./check`.** Make it run your real build and tests. If you got `check.kit`, merge its architecture steps into your existing check.
4. **Turn on the gates.** Add `@AGENTS.md` as the first line of an existing `CLAUDE.md`, commit `.claude/`, set the owner in `CODEOWNERS`, and enable branch protection as for a new project.
5. **Describe the stack and pick a reference.** Rewrite `docs/architecture/stack.md` for the project's libraries, and allow them per kind in `architecture.json`. Name a reference slice in `AGENTS.md`: the existing slice that best follows the architecture, or one you rebuild in that shape, using the kit's Notes slice as the model.
6. **Write the glossary.** List the business concepts the code already uses, one heading each.
7. **Get a verification skill.** Run `/pstack:create-verification-skill`. It writes `.claude/skills/verify-<name>/`, which drives the app the way a user does and keeps the evidence, and proves it once before it hands it over.
8. **Put new work in the new shape.** New capabilities become slices in the shape of the reference slice. New rules go into the domain. New I/O goes behind ports.
9. **Fix old code as you touch it.** When a change touches a module with violations, fix them in a separate commit and run `--write-baseline` to lower the counts. The baseline only ever goes down. The gate guard fails a pull request that raises it, and lowering it needs no owner.

The language guides describe the template layout. In a project with a different layout, either move toward the template layout over time, or keep the existing layout mapped in `architecture.json` and name as the reference the slice that follows the architecture best.

## Day to day

The Stop hook runs `./check` with the PATH of the Claude Code session, so the session needs the project's toolchain, such as Node 24 and the package manager, on its PATH.

Agents read `AGENTS.md` at the start of each task and the architecture docs when they touch code. They copy the structure of the reference slice, using the `new-slice` and `new-port` checklists, run `./check` after each step, and cannot finish a task while the check fails. Every review answers the questions in `docs/architecture/review.md` for the judgment calls the check cannot make. When an agent runs `/pstack:interrogate`, it adds that file to the rubric the reviewers get.

Your review stays small:

- **Diffs to gate files.** `CODEOWNERS` sends you every change to `architecture.json`, `check`, `tools/`, `.claude/`, `.github/`, the instruction files, and the compiler, linter, and test runner settings. An agent that weakens a check shows up here. Changes that only tighten a check need no review: a lower baseline, a new project check in `checks/`, and a verification skill.
- **New ports, stored formats, and wire contracts.** The first version of a format is the one old data will be in. A test that loads a committed sample of each stored format catches a renamed field, but not a format that was wrong from the start.

The composition root needs no owner. The architecture check limits it to its files, to wiring without control flow, and to a line limit.

When agents keep making the same mistake, fix the repository instead of the next prompt. `/pstack:correct` finds the mistake classes in the history and fixes each at the highest level that works:

1. Make the mistake impossible, with the architecture or a better reference slice.
2. Block it with a type, a rule in `architecture.json`, a lint rule, or a project check in `checks/`, with the fix in its message.
3. Catch it with a test.
4. Add a row to the rule table in `AGENTS.md`, or a sentence to the docs, only when nothing else can carry it.

Upgrade a project to a newer kit by copying `tools/archcheck.py`, `tools/gateguard.py`, `tools/agent-stop-check.sh`, `docs/ARCHITECTURE.md`, from `docs/architecture/` the project's language guide, `where-code-goes.md`, and `review.md`, and `.claude/skills/deslop/` out of the kit, then running `./check`. The kit owns these files, so the project does not edit them. Read the diff of the docs, because a new rule may need a change in the project. Projects created before 2026-10-15 also have `tools/new.py`, which they can delete, because new code copies the reference slice.

TypeScript projects created before 2026-10-19 have no linter. To add it:

1. Copy `templates/typescript/.oxlintrc.json` to the project root, and change the paths in its `overrides` to the project's source and domain directories. In a repository with several apps, `docs/architecture/typescript.md` says which paths to use.
2. Add `oxlint` and `oxlint-tsgolint` to `devDependencies`, at the versions in `templates/typescript/package.json`. A project on TypeScript 6 or below can keep ESLint with typescript-eslint instead. The rules in the language guide hold either way.
3. Add `step lint npx oxlint` to `./check`, before the type check, and add `/.oxlintrc.json` to `.github/CODEOWNERS`.
4. Run `npx oxlint` and fix what it reports. Most findings in tests are stubs written as `async` functions without `await`, and JSON responses read as `any`.
5. Describe the linter in `docs/architecture/stack.md`, as the template's copy does.

## pstack

[pstack](https://github.com/cursor/plugins/tree/main/pstack) decides how an agent works: which playbook it follows, which subagents it spawns, how it proves its work, and how it reviews and lands pull requests. The kit decides where code goes, and fails the check when code goes elsewhere. The kit follows pstack's principles, so an agent reads one set of rules:

- **Layers.** Each layer of the architecture states its reason, and the docs say to leave out a wrapper that has none. Here the kit departs from pstack on purpose. Minimize Reader Load would inline a port with one adapter and a use case with one caller. The kit keeps both, because the port keeps outside types and I/O out of the domain and the use case is the one way from UI to the ports, and the architecture check enforces both. `docs/architecture/review.md` gives reviewers that reason.
- **Tests.** Tests run against real adapters wherever those run locally, and test doubles only make a port fail or stand in for time, ids, and remote services. pstack's TypeScript rules and Test Behavior, Not Implementation ask for this.
- **Proof.** A change is done when the verification skill shows it working in the running app, not when it compiles.
- **Gates.** A new check in `checks/`, a lower baseline, a committed script, and a verification skill need no owner, so most of what `/pstack:correct` and Build the Lever produce doesn't wait for you. A new lint rule and a new row in the rule table still do, because the same files can also loosen a check.
- **Review.** Every review answers `docs/architecture/review.md`. `AGENTS.md` tells agents to add it to the rubric of `/pstack:interrogate`, and keeps the rule table that `/pstack:correct` maintains.

Projects use upstream pstack, unchanged. The template's `.claude/settings.json` enables it for everyone who works on the project:

```json
"extraKnownMarketplaces": {
  "cursor-plugins": {"source": {"source": "github", "repo": "cursor/plugins"}}
},
"enabledPlugins": {"pstack@cursor-plugins": true}
```

Claude Code registers the marketplace after a contributor accepts the workspace trust dialog. Cloud sessions show no such dialog, so install the plugin there with `/plugin marketplace add cursor/plugins` and `/plugin install pstack@cursor-plugins`. Run `/pstack:setup-pstack` once to pick the models, then type `/pstack:poteto-mode` before a task that needs rigor. pstack's own adapter maps its Cursor names to Claude Code, and skips steps that need a Cursor-only feature, such as Bugbot. pstack also runs `/deslop` before each commit, and the `control-ui` and `control-cli` skills to drive an app. All three come from Cursor's cursor-team-kit plugin, which the marketplace does not offer to Claude Code. The kit ships cursor-team-kit's `deslop` skill unchanged in `.claude/skills/deslop/`, with its MIT license, as of cursor/plugins commit eb4db2b. To update it, copy `cursor-team-kit/skills/deslop/SKILL.md` from a newer commit. The verification skill drives the app in place of the control skills.

The architecture holds in a pstack session for these reasons:

- **The check.** The Stop hook runs `./check` in the checkout or git worktree the session works in. UI that uses a port fails the check, so an agent cannot replace a use case by calling its port from the UI.
- **The gates.** Branch protection and `CODEOWNERS` hold every change to a gate file on main for your review. pstack's autopilot playbooks merge pull requests on their own, but never give or bypass an approval that GitHub enforces. This works only when agents open pull requests under their own account, as described under "Start a new project".
- **The verification skill.** pstack's playbooks prove each change in the running app, and the verification skill is how they drive it in a kit project.

The Stop hook runs only when the main session finishes. pstack's subagents inherit the worktree of the session that spawns them, so the hook checks their combined work, and they run `./check` themselves because `AGENTS.md` tells them to. If the main session ends a turn while subagents still edit files, the hook can report failures in their unfinished work.

### Upgrade a project created before 2026-10-22

1. Copy `tools/archcheck.py`, `tools/gateguard.py`, `tools/agent-stop-check.sh`, `docs/ARCHITECTURE.md`, and from `docs/architecture/` the language guide, `where-code-goes.md`, and `review.md` out of the kit.
2. In `architecture.json`, add `"scriptFiles": ["scripts/**", "checks/**"]`. Add `portFiles`, and `"forbidPorts": true` on each UI kind, if the project has neither yet. Add `.scratch/` and `.verify/` to `.gitignore`.
3. In TypeScript, add `scripts` and `checks` to the `include` of `tsconfig.json` and to the files of the type-assertion rule in the linter settings. Remove the domain from that rule's excluded files, and replace each type assertion in the domain with a type guard, like `isNoteTitle`.
4. Copy the language template's `check` over the project's, and merge back the project's own steps. It runs each executable in `checks/`, and keeps its work in one function, so that no step can rewrite the rest of the script. In `.github/workflows/check.yml`, make the gate guard step run on every pull request, and replace the step that diffs the module map with `git diff --exit-code`, as in the language template.
5. Copy `templates/common/.claude/skills/deslop/` into `.claude/skills/`.
6. Replace `.github/CODEOWNERS` with the template's, so that the composition root, the baseline, and the verification skills need no owner.
7. Replace `AGENTS.md` and `CLAUDE.md` with the template's. Keep the project's reference slice and its own rows in the rule table. Delete `.claude/agents/architecture-reviewer.md`.
8. In `.claude/settings.json`, replace the lines for `pstack@agent-architecture-kit` with the template's lines for `pstack@cursor-plugins`.
9. Run `/pstack:create-verification-skill`, or copy the template's verification skill and change its launch line.
10. Rewrite the reference slice's tests to run against the real adapter, as the template's do. Commit a sample of each stored format, with a test that loads it.

Run `./check` after each step.

## Autopilot with pstack

pstack runs large work on its own with two playbooks. Both keep the kit's gates, because every pull request ends up merging into main, where branch protection and `CODEOWNERS` apply.

- **Autopilot-stack** builds a queue of changes as one linear stack of pull requests, each with a verdict from an agent that did not write it, and stops. You review the stack and land it. Use it when you want to see the work before it lands, or when the changes depend on each other: `/pstack:poteto-mode autopilot these changes but stack them, don't ship.`
- **Autopilot-full** runs independent pull requests to merged, with one owner agent per pull request. An owner merges only after a swarm of verifiers has proven its code. A pull request that changes a gate file still waits for your approval, which no agent gives or bypasses.

Before a run on a large feature:

1. **Review the foundation first.** Make the first pull request hold the shared shape: glossary entries, domain types and rule signatures, new ports and their result types, changes to stored formats and wire contracts, and an empty slice with its wiring for each track. Every later pull request builds on it, so a mistake here costs the most when it is found late.
2. **Keep gate changes out of the feature work.** A new kind in `architecture.json` or a changed lint setting goes into its own pull request against main, which waits for you. Plan the run so that nothing else waits on it.
3. **Let agent identities open the pull requests.** GitHub does not let you approve your own pull request.

Try it first on a medium feature with two or three tracks before you trust it overnight. It has not been tried with the kit yet.

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
- **`sourceRoots`.** Directories to scan. The templates scan the whole repository (`.`), so a source file outside every module fails as unmapped. Directories whose names start with a dot are skipped, so prototypes go into `.scratch/`, which `.gitignore` lists.
- **`testFiles`, `scriptFiles`, and `ignore`.** Glob patterns, matched against paths from the repository root. `*` stays within one directory and `**` crosses directories, so `*.config.ts` matches only files in the root. Test files and script files, such as a codemod in `scripts/` or a project check in `checks/`, are exempt from the import rules, and production code may not import them.
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
  - `forbidPorts`: `true` makes the check fail when a module of this kind uses a port by name. The templates set it for UI, which reaches ports only through use cases.
- **`portFiles`.** Glob patterns for the files that declare the ports. The check reads the port names from them: interfaces in TypeScript, interface types in Go, and protocols in Swift. A kind with `forbidPorts` needs this setting.
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

Retested on Linux on 2026-10-20, after the Stop hook learned to check git worktrees:

- **Stop hook.** I ran the script directly with hook input. With `cwd` in a git worktree of the project, it runs `./check` there and blocks on a failing change that the main checkout does not have. Before this change, it passed. With `cwd` in another repository, outside any repository, or missing, it checks the main checkout as before.

Retested on Linux on 2026-10-21, after the port check, the gate guard, and the kit's copy of pstack were added:

- **Port check.** `init` creates TypeScript, Go, and Swift projects whose architecture check passes. A port used in a slice's UI fails in all three, also as a qualified name such as `domain.NoteStore` in Go. A port named in a comment or a string passes. The baseline accepts the violation. A UI kind with `forbidPorts` and no `portFiles` is a configuration error. Swift was checked with the architecture check only, without a Swift build.
- **Gate guard.** I ran the script directly in a TypeScript and a Go project. It passes wiring changes in the composition root, a new slice, a glossary entry, and the generated module map. It fails on `architecture.json`, `package.json`, `go.mod`, and a deleted `.claude/settings.json`. The workflow step itself has not run on GitHub yet.
- **The kit's copy of pstack.** `tools/vendor_pstack.py` applied all ten edits to cursor/plugins at commit 190d287, and upstream's generator check and plugin validator pass on the result. `claude plugin validate` passes on the marketplace and the plugin, and Claude Code installs `pstack@agent-architecture-kit` from a local clone of the kit. The kit removed its copy on 2026-10-22.

Retested on Linux on 2026-10-22 with Python 3.13, Node 22.22, TypeScript 7.0.2, oxlint 1.88.0, and Go 1.24.7, after the kit was aligned with upstream pstack and its copy of pstack was removed. The kit requires Node 24, so the TypeScript template still needs a run on Node 24.

- **New projects.** `init typescript` and `init go` create projects whose `./check` passes, with the reference slice's tests running against the real file store. In both languages, a renamed stored field fails the test that loads the committed file in that format, and only that test. In TypeScript, `as NoteTitle` in the domain fails lint.
- **Gate guard.** I ran it in a git repository of a TypeScript project. It passes a new check in `checks/` and a lower baseline. It fails when an existing check changes or is deleted, and when the baseline gains a violation.
- **Project checks and scripts.** `./check` runs an executable in `checks/` as its own step, and the step fails on the mistake it checks for. A TypeScript file in `scripts/` passes the architecture check, and production code that imports it fails.
- **Verification skills.** On a fresh Go project and a fresh TypeScript project, I followed each skill's own steps: start, doctor, both feature recipes, and stop. Every step gave the result its feature file names, the evidence survived cleanup, and no server process was left running. The doctor reports a stopped instance as a failure.
- **Swift.** Only the architecture check ran, which passes.

Retested the same day, after an independent review found holes in the gate guard and the scripts:

- **Gate guard.** It fails on a changed check with a non-ASCII name, on a check that lost its executable bit, and on a baseline that comes back with a violation after a pull request deleted it. It reads a baseline with comments. A pull request that loosens a check and also changes `AGENTS.md` passes, because that file sends it to the owner.
- **Project checks.** A non-executable helper file and a folder in `checks/` are skipped, and `./check` passes.
- **Verification skill.** In a project inside a larger git repository, the run directory lands in the project. A second `stop` does nothing.
- **Code owners.** A new TypeScript project's `CODEOWNERS` owns `package.json` and `package-lock.json` again, so an install script can't switch off `./check` without your review.

Retested later that day, after `deslop` was added and `./check` moved its work into one function:

- **A step that rewrites `./check`.** A test that overwrote `check` while it ran, together with a real architecture violation, made the old script print `FAIL architecture` and still exit 0. The new script exits 1, and the CI step `git diff --exit-code` fails on the rewritten file.
- **`deslop`.** `init` copies the skill and its license into `.claude/skills/deslop/`, unchanged from cursor/plugins at commit eb4db2b.

Not tested:

- **A template for several apps.** `init` still creates one app. "From one app to several" in `docs/architecture/typescript.md` gives the steps and an `architecture.json` for an API, a web app, and a shared domain.

- **The Swift template after 2026-10-15.** Its tests, rewritten again on 2026-10-22 to run against the real file store, and `FailingNoteStore` have not been compiled. Run `./check` on macOS before relying on them.

- **Claude Code in a real session.** Nobody has watched it load the Stop hook, the skills, the path-scoped rule, or `pstack@cursor-plugins` from the template's settings. The formats follow the Claude Code documentation as of 2026-10-14.
- **GitHub.** The GitHub Actions workflows were not run, and `CODEOWNERS` enforcement was not tried, including the lines without an owner that free the verification skills.
- **The Xcode app.** The project steps for Swift and an iOS build of the app.
- **Larger code.** Adoption in a real, larger codebase, and the check's speed on a large repository.
- **pstack in a kit project.** Nobody has run pstack's playbooks in a kit project, and its autopilot playbooks have not been tried here.
- **Other setups.** TypeScript path aliases, TypeScript frontends or frameworks such as Express or Fastify, Core Data or SwiftData adapters, and Windows.
