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
tools/gateguard.py                CI check that keeps gate-file changes out of branches other than main
tools/vendor_pstack.py            builds the kit's copy of pstack (runs from the kit only)
.claude-plugin/marketplace.json   the kit as a Claude Code plugin marketplace
plugins/                          the kit's copy of pstack, and how it differs from upstream
templates/common/                 AGENTS.md, CLAUDE.md, GLOSSARY.md, .claude/, CODEOWNERS
templates/swift|go|typescript/    a working project with the Notes reference slice and its stack.md
examples/                         pages that show the architecture in example projects (not copied into projects)
```

Each project receives:

- **The docs.** `docs/ARCHITECTURE.md`, its language guide, `docs/architecture/stack.md` for the project's libraries, and the generated module map.
- **The tools.** `tools/archcheck.py`, the Stop hook script, the gate guard, and `./check`, the one command that verifies everything.
- **The configuration.** `architecture.json` maps directories to module kinds and sets the rules for each kind, and `architecture-baseline.json` holds the violations you have accepted.
- **Agent instructions.** `AGENTS.md`, which names the reference slice, a `CLAUDE.md` that imports it, and a `README.md` to fill in with what the project does.
- **Claude Code integration in `.claude/`.** The Stop hook, a path-scoped rule that points agents to the docs, the `new-slice` and `new-port` checklists, and the `architecture-reviewer` subagent.
- **Code owners.** `.github/CODEOWNERS` covers the gate files and the composition root.
- **CI.** `.github/workflows/check.yml` runs `./check`, and the gate guard on pull requests into branches other than main.
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

## Workflow plugins such as pstack

A workflow plugin decides how an agent works: which steps it takes, which subagents it spawns, and how it reviews and lands its pull requests. [pstack](https://github.com/cursor/plugins/tree/main/pstack) is one. The kit decides where code goes and fails the check when code goes elsewhere. The two work together, with the kit's rules on top.

The kit serves its own copy of pstack with twelve edits, which `plugins/README.md` lists. Read literally, a few pstack rules remove layers that the architecture requires, replace the stubs that its testing rules prescribe, or tell the agent to fix a failing check itself. Ten edits scope each such rule to what the repository's architecture docs allow, so the agent reads one set of rules instead of two that disagree. The other two let pstack work with GitHub in Claude Code cloud sessions, as described below. The edits name no part of the kit, and `plugins/README.md` describes how to propose them upstream. Once upstream has them, enable `pstack@cursor-plugins` instead.

To enable the kit's copy for everyone who works on a project, add this to `.claude/settings.json`. It is a gate file, so commit the change yourself.

```json
"extraKnownMarketplaces": {
  "agent-architecture-kit": {"source": {"source": "github", "repo": "0xboris/agent-architecture-kit"}}
},
"enabledPlugins": {"pstack@agent-architecture-kit": true}
```

Claude Code registers the marketplace after a contributor accepts the workspace trust dialog, and only for contributors who can read the kit's repository. Cloud sessions show no such dialog, so install the plugin there with `/plugin install pstack@agent-architecture-kit`. Then type `/pstack:poteto-mode` before a task.

The architecture holds in a pstack session for these reasons:

- **The check.** The Stop hook runs `./check` in the checkout or git worktree the session works in. UI that uses a port fails the check, so an agent cannot replace a use case by calling its port from the UI.
- **The gates.** Branch protection and `CODEOWNERS` hold every change to a gate file on main for your review, and the gate guard keeps gate changes out of feature branches. pstack's autonomous playbooks merge pull requests on their own but never bypass an approval that GitHub enforces. This works only when agents open pull requests under their own account, as described under "Start a new project".
- **The kit's copy of pstack.** Its rules keep the layers that `docs/ARCHITECTURE.md` requires, and it treats an owner's gate as a gate, not as a tooling failure.
- **The precedence section.** The "Skills and plugins" section in `AGENTS.md` covers what no edit does: a failing check is a finding in the code, and rules and checks that a workflow writes are gate changes. Claude Code loads it in every session and in pstack's subagents.
- **The reviewer.** The `architecture-reviewer` subagent runs before each pull request, next to pstack's own reviews.

A Claude Code cloud session blocks GitHub's GraphQL API, so every `gh pr` command fails there, and so does pstack's PR watcher. In the kit's copy, pstack detects a cloud session and uses the GitHub MCP tools instead. In place of the watcher, it subscribes the session to each PR, so CI results, reviews, and the merge wake the session. The Orchestrate playbook still needs a session outside the cloud.

The Stop hook runs only when the main session finishes. pstack's subagents run `./check` because `AGENTS.md` tells them to, and the main session's Stop hook checks their combined work. If the main session ends a turn while subagents still edit files, the hook can report failures in their unfinished work.

Projects created before 2026-10-21 get all of this, the port check and the gate guard included, with these steps:

1. Copy `tools/archcheck.py`, `tools/gateguard.py`, and `tools/agent-stop-check.sh` from the kit.
2. In `architecture.json`, add `portFiles` with the files that declare the ports, and `"forbidPorts": true` to each UI kind, as the language template does. Run `./check` and fix or baseline what it reports.
3. Add the gate guard step and `fetch-depth: 2` to `.github/workflows/check.yml`, as in the language template.
4. Copy the "Skills and plugins" section of `templates/common/AGENTS.md` into the project's `AGENTS.md`, and question 13 of `templates/common/.claude/agents/architecture-reviewer.md` into the project's reviewer.

## Autopilot on a feature branch

Agents can build a large feature on their own: several tracks in parallel, each delivered as pull requests into one feature branch, and one pull request from the feature branch into main at the end, which you review and approve. pstack's Autopilot-full playbook comes closest, with the feature branch in place of main. These steps keep the architecture intact during the run, and keep the final review small enough to be a real review.

1. **Review the foundation before the tracks start.** The first pull request into the feature branch holds the shared shape: glossary entries, domain types and rule signatures, new ports and their result types, changes to stored formats and wire contracts, and an empty slice with its wiring for each track. Every track builds on it, so a mistake here costs the most when it is found late.
2. **Let the tracks run.** Slices never import each other, so tracks mostly touch different files, apart from the domain and the composition root. A track's pull request merges into the feature branch once CI passes, the architecture reviewer has run, and the workflow's own verification is done.
3. **Keep the gates.** Branch protection usually covers only main, so the feature branch has no owner review. The gate guard fails a pull request into any branch other than main that changes a gate file, so agents put gate changes into their own pull request against main and wait for you on that track. GitHub runs the workflow from the pull request itself, so a pull request that deletes the guard step also passes. That deletion is a change to `.github/`, so it appears among the gate files of the final review.
4. **Merge, never rebase, the shared branch.** Merge track pull requests with merge commits, so that each track stays visible, and merge main into the feature branch regularly. Several agents work from the branch, so its history must not change under them.
5. **Ask for a review guide in the final pull request.** Its description lists the gate-file changes, which should be none; the composition-root diff; the ports, stored formats, and wire contracts that changed after the foundation review; and each track, with links to its pull requests and their verification. Review those closely and skim the rest, which the check, the tests, and the verifiers have covered.
6. **Let an agent identity open the final pull request.** GitHub does not let you approve your own pull request.

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
- **The kit's copy of pstack.** `tools/vendor_pstack.py` applied all ten edits to cursor/plugins at commit 190d287, and upstream's generator check and plugin validator pass on the result. `claude plugin validate` passes on the marketplace and the plugin, and Claude Code installs `pstack@agent-architecture-kit` from a local clone of the kit.

Retested on Linux on 2026-10-21, in a Claude Code cloud session, after pstack's adapter learned to reach GitHub there:

- **GitHub in a cloud session.** `gh pr view`, `gh pr list`, and `gh api graphql` fail with HTTP 403, and `gh api` REST paths work. The MCP tools in the adapter's table return the fields it names: `get` gives `merged`, `merged_at`, `base.ref`, `head.sha`, and `mergeable_state`, and `get_check_runs` and `get_review_comments` answer. `list_pull_requests` reports `merged: false` for a merged PR, which the table notes.
- **The edits.** `tools/vendor_pstack.py` applied all twelve edits to cursor/plugins at commit 190d287. Upstream's generator check, plugin validator, and docs check pass on the whole patch and on each of its two halves. `claude plugin validate` passes on the plugin.
- **Not run.** No pstack playbook has run in a cloud session, so the PR subscription in place of the watcher has not been tried in a real babysit.

Not tested:

- **A template for several apps.** `init` still creates one app. "From one app to several" in `docs/architecture/typescript.md` gives the steps and an `architecture.json` for an API, a web app, and a shared domain.

- **The Swift template after 2026-10-15.** Its new `StubNoteStore` and the rewritten tests have not been compiled. Run `./check` on macOS before relying on them.

- **Claude Code in a real session.** Nobody has watched it load the Stop hook, the skills, the subagent, or the path-scoped rule. The formats follow the Claude Code documentation as of 2026-10-14.
- **GitHub.** The GitHub Actions workflows were not run, and `CODEOWNERS` enforcement was not tried.
- **The Xcode app.** The project steps for Swift and an iOS build of the app.
- **Larger code.** Adoption in a real, larger codebase, and the check's speed on a large repository.
- **pstack in a kit project.** Nobody has run pstack's playbooks in a kit project, and the autopilot workflow on a feature branch has not been tried.
- **Other setups.** TypeScript path aliases, TypeScript frontends or frameworks such as Express or Fastify, Core Data or SwiftData adapters, and Windows.
