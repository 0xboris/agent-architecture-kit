# Architecture

This document describes how the code is organized and why. It gives every agent and every person who works here the same picture: which kinds of modules exist, what each holds, which may depend on which, and how a change is verified.

The language guide in `docs/architecture/` shows how each part looks in this project's language, and `docs/architecture/stack.md` names the libraries this project uses and how the reference slice uses them. `docs/architecture/modules.md` lists every module with its kind; the check generates it. `AGENTS.md` names the reference slice. When you write a kind of code for the first time, copy its structure.

`./check` enforces most of this document. A forbidden import, a file outside every module, or feature code in the composition root fails the check with a message that names the fix. The rest of this document covers the judgment calls that no tool can make.

## The shape

The code is layered horizontally and sliced vertically. The layers say which code may depend on which. The slices keep the code of one capability together.

```
                composition root
                 │            │
                 ▼            ▼
         feature slices     adapters
        (UI → use cases)       │
           │       │           │
           ▼       ▼           ▼
       shared UI   domain ◄────┘
           │       │
           ▼       ▼
           utilities
```

An arrow points from a module to what it may depend on. Dependencies point inward, from details toward policy: the domain is policy, while UI, storage, and frameworks are details. Policy never depends on details.

## Module kinds

- **Domain.** The business model, the rules, the ports, and the middleware. It performs no I/O and uses no UI framework, database, or SDK. It depends only on utilities.
- **Use cases.** One module per slice. A use case carries out one operation for its slice: it loads what it needs through ports, lets domain rules decide, and saves or sends the result through ports. It depends on the domain and utilities.
- **UI.** One module per slice: screens and view models in an app, request handlers in a service, commands in a tool. It turns input into use case calls and results into output. It depends on its own slice's use cases, the domain, shared UI, and utilities.
- **Shared UI.** Presentation pieces that several slices use, such as components, styles, or HTTP response helpers. It holds no business types and depends only on utilities.
- **Adapters.** Implementations of the ports: databases, files, the network, platform services, third-party SDKs, the clock, and random sources. Each adapter maps outside formats to domain types. It depends on the domain and utilities.
- **Composition root.** The entry point. It creates the adapters, applies middleware, wires every slice, reads configuration, and starts the process. It is the only code that knows which implementation stands behind each port. Nothing depends on it.
- **Utilities.** Helpers with no business meaning, such as the logging interface or a result type. They depend on nothing in the project.
- **Test support.** Sample data, stubs, and small fakes for tests. Only test code depends on it.
- **Screens.** In an app with pages, a screen arranges the public UI of one or more slices on one page, such as a home page made of a list from one slice and a status box from another. It depends on the UI of slices, through each slice's public entry, and on shared UI. It calls no use cases and makes no decisions. The composition root maps routes to screens.
  - A screen connects slices. It passes a value from one slice's UI to another's, such as the current user's id, and fills a slot in one slice's UI with another slice's UI, such as how an author's name is shown. A slice's UI takes what it needs from another slice as such a parameter, never as an import.
  - A slice's UI links only to its own slice's pages. A link to another slice's page is a parameter that the screen fills.
- **Shared domain.** In a repository with several apps, the model types, parse functions, and pure rules that more than one app uses. It holds no ports and no use cases, performs no I/O, and depends on nothing, so it runs unchanged in every app, a browser included.

## Feature slices

A slice is one capability of the product, such as transactions, budgets, or recurring transactions. It has a UI module and a use case module. A slice can have several entry points: screens, endpoints, and background work that the composition root triggers, such as a scheduled job.

- Slices never depend on each other. When two slices need the same type or rule, it moves into the domain.
- Ports belong to the domain, not to a slice. Any slice's use case may use any port, such as a use case that creates a note and checks its author through the user store.
- Use cases are never shared. Each slice writes its own use cases, even when two of them look alike. The rules they use are shared, through the domain.
- A new capability gets a new slice. Do not grow an existing slice into something it was not made for.
- Create a slice by copying the structure of the reference slice: its modules, its tests, and its wiring file.

## The domain

The domain holds four things.

- **The model.** Business types and values. A value that must follow rules is created only through a function that checks them, so the rest of the code can trust it. States that exclude each other form one closed set of cases, not flags that can contradict each other.
- **The rules.** Every business decision, as pure functions of values: same input, same output, no I/O, no clock, no randomness. This includes rules that only one path uses today, such as "a manual entry needs a category", so that all rules live in one place.
- **The ports.** Interfaces for everything the use cases need from outside the process.
- **The middleware.** Decorators that wrap a port and add a step to every call through it. They depend only on ports and rules, so they perform no I/O themselves.

Each rule exists once, under the name that `GLOSSARY.md` gives the concept. A copy of a rule drifts, and an agent that fixes one copy does not know about the other.

## Use cases orchestrate

A use case makes no business decision. If you write an `if` about business meaning in a use case, it belongs in a domain rule that the use case calls.

Orchestration may repeat across slices. A manual entry, an import, and a scheduled job may each load, validate, and save a transaction in their own use case. That is acceptable, because the knowledge sits in the rules and the rules are shared.

Watch for steps that must happen on every path. If changing a step would force every path to change the same way, it is not orchestration. It belongs in a domain rule, a port method, or middleware, where the next path cannot forget it.

## Ports and dependency inversion

When code needs something from outside the process, the domain declares a port and an adapter implements it. The composition root passes the adapter in. The call goes outward at run time, while the source dependency points inward.

- Name a port for what the use case needs, such as `TransactionStore` or `PaymentGateway`, not for the technology behind it.
- A port uses domain types. Storage records, wire payloads, and SDK types stay inside the adapter.
- Every dependency arrives through a constructor or a parameter. There are no singletons, global registries, or service locators, so an agent can see what a piece of code depends on by reading it.
- Each third-party library that performs I/O sits behind one adapter.
- Add an interface only at a module boundary or to isolate something slow or nondeterministic. Inside a module, use concrete types.
- A port's results form a closed set of cases, such as a union of outcomes or a result with a closed set of errors. Callers and their tests can then handle every case, and the compiler shows every caller that misses a new one.

## Middleware

Middleware wraps a port, and the composition root decides which slices receive it. There are two kinds.

- **Mandatory middleware** keeps data consistent or performs a technical step that every write needs, such as refreshing a widget or a search index. The composition root applies it once, when it creates the adapter, so no slice can receive the bare adapter.
- **Optional middleware** depends on intent, such as a budget alert that manual entries trigger and imports do not. The composition root adds it per slice, on top of the mandatory middleware.

Four conditions keep middleware safe.

1. The decision stays in a domain rule. The middleware calls the rule and acts on the result.
2. Writes that must succeed together happen in one port call or one transaction.
3. Middleware sees writes, not intent. When intent matters, the composition root applies the middleware only to the slices with that intent. When the decision depends on the data, such as an alert only for today's transactions, a domain rule decides.
4. The composition test covers each choice that matters. Unit tests of a slice build its use cases directly and never see the wiring.

Before adding middleware, ask whether the data needs updating at all. A total that can be computed from stored data when it is read needs no middleware to keep it in sync.

## The composition root

The composition root holds wiring and nothing else.

- It has no control flow, apart from one configuration file and the error handling that the language requires. Decisions belong in the domain or in a use case.
- It consists of a fixed set of files: the entry point, the container, the live dependencies, the configuration, and one wiring file per slice.
- It has a size limit. Feature code that lands here fails the check.
- Configuration and the environment are read here and passed in as values.

## Boundaries

- **Parse at the edge.** Data from outside the process becomes domain types where it enters. This includes requests, responses, database rows, files, stored settings, and deep links. Inside, code trusts its types.
- **One model per boundary.** Wire types, storage types, and domain types stay separate even when they look alike. Adapters and UI map between them.
- **Data outlives code.** Data that older versions stored, and clients that are still installed, will meet the new code. That includes what a client keeps on the device, such as a key in the browser's storage. Change stored formats and wire contracts by adding: add optional fields, keep old fields until nothing uses them, and map unknown enumeration values to an unknown case. Renaming or removing a stored or sent field is a deliberate decision with a migration path.
- **Errors are explicit.** No error is swallowed. An error that leaves a module tells the caller what it can do and carries its cause. Log each error once, where it is handled, with internal ids and no personal data.
- **Authorization is checked where requests enter.** Every entry point that acts for a caller checks that the caller may act on each record that the request touches.

## Several apps in one repository

A repository can hold several apps, such as an API and the web app that calls it. Each app has the layers above, with its own composition root, slices, domain, and adapters. Between the apps, two rules hold.

- **Rules are shared as code.** A rule that several apps need, such as the rules for a valid title, lives once in the shared domain, and each app's domain and slices import it. A web form then gives the same answer as the API, from the same code.
- **Data goes only through the API.** A client app reads and writes through the API over HTTP, with a client generated from the API's contract, its OpenAPI document. No app imports another app's code. The architecture check fails on any import between apps.

From these follow:

- **Each app keeps its own ports.** The API's storage port and the web app's API port mean nothing to the other app, so they stay in each app's own domain.
- **The contract is generated and committed.** The API generates its contract from its routes, and each client generates its typed API client from the contract. `./check` fails when either is out of date, so a change to the contract shows up in review, like a change to a stored format. The rules for data that outlives code apply to it: installed clients keep calling the old shape.
- **The client's API adapter parses with the shared rules.** It maps the wire types that the contract describes to domain types, through the shared parse functions, as any adapter parses outside data.
- **The API is the authority.** A client runs the shared rules early, to answer the user before a request is sent. The API checks every request again, because the apps are deployed separately and a client may briefly run an older rule.
- **Clients in other repositories get only the contract.** A mobile app in its own repository generates its client from the same contract and has no shared code. Its checks follow the constraints that the contract states, and the API's answer decides.

A page that combines several features is a screen when it only shows what the slices already offer, unchanged. When the page needs data or decisions of its own, such as failed runs across every resource this week, it is a capability of its own: a new slice with its own use case, which reads the domain's ports. Slices still never import each other.

## State and concurrency

- Prefer immutable values. Shared mutable state has one owner that serializes access, and each check happens in the same call as the action that depends on it.
- A decision based on stored state that others can change uses a transaction or a conditional write.
- A handler for messages that can arrive more than once is idempotent. Generated records get deterministic ids, so a second run creates nothing new.
- Every background task has an owner that awaits or cancels it.

## Verification

`./check` runs everything: the architecture check, the build, the type checker, and the tests. It runs the same way locally, in the agent's Stop hook, and in CI. The main branch always passes it.

- **Machines check first.** A failure at build time beats a failing test, and a failing test beats a review comment.
- **Most tests are domain tests.** Rules are pure, so their tests need no stubs and run in milliseconds.
- **Use case and UI tests stub the ports.** A stub is typed against the port and returns what the test sets. Give it each result the port can return, so that every path through the code runs, and check which port methods the code calls and with which arguments. A stub has no logic, so it needs no tests of its own.
- **Adapters are tested against the real system**: a real database, a temporary directory, or recorded responses from a remote service. These tests show that the adapter produces the results that the port promises, so the stubs in other tests stay realistic.
- **A small fake is fine** for a port whose state a test drives across calls, such as a clock that the test advances. Keep it simple enough that it needs no tests of its own.
- **Composition tests check the wiring**, such as which middleware a slice receives.
- **Tests follow behavior.** They use a module's public interface and assert on results, on state, and on the calls a use case makes to its ports. They never assert on calls between a module's own parts, so a refactor that keeps behavior keeps every test green.
- **Tests are deterministic.** They use a fake clock and fixed ids, never real time, the network, or unseeded randomness. They pass in any order. A flaky test is a bug.
- **Migrations are tested on old data.** A migration that changes existing rows, such as one that adds a required column and fills it, gets a test that runs it on rows written by the previous version.
- **Verification stays honest.** Every bug fix starts with a test that reproduces the bug. No check is made to pass by deleting, skipping, or loosening a test, or by changing a gate file.

## Where new code goes

Ask these questions in order. The first yes decides.

1. Does it decide something by business rules, or compute a business value? A domain rule.
2. Does it describe a business concept? The domain model, with its name in `GLOSSARY.md`.
3. Does it need something from outside the process? A port in the domain and an adapter.
4. Must it happen on every write through a port? Middleware in the domain, applied in the composition root.
5. Does it carry out an operation for one capability? A use case in that capability's slice.
6. Is it a new capability? A new slice, in the shape of the reference slice.
7. Does it show output or receive input? The UI module of its slice, or shared UI when several slices use it and it has no business meaning.
8. Does it create objects, read configuration, or start the process? The composition root.
9. Is it a helper with no business meaning? Utilities.

In a repository with several apps, two questions come before the list:

- Does another app in the repository need the same rule or model? The shared domain, without ports.
- Does it arrange the UI of several slices on one page, with no data or decisions of its own? A screen.

When the code needs something its module may not import:

- If it needs an outside capability, add a port and pass the adapter in through the composition root.
- If it needs something from another slice, move the shared part into the domain.
- If a use case needs data in a form that only an adapter knows, map it to domain types in the adapter.

## How this is enforced

- **The architecture check** (`tools/archcheck.py`, configured in `architecture.json`) maps every source file to a module and checks these things:
  - imports between modules
  - frameworks and libraries per kind
  - I/O calls in modules that must not perform I/O
  - glossary terms in utilities and shared UI
  - the shape of the composition root
  - imports between apps, and imports into a module that bypass its public entry
  - cycles
- **The baseline** (`architecture-baseline.json`) records violations that existed before the rules were adopted. The check fails only when a change adds a violation. When code is fixed, the baseline is lowered.
- **Gate files** define the checks: `architecture.json`, the baseline, `check`, `tools/`, `.claude/`, `.github/`, and the instruction files. A code-owner rule requires the owner's review for every change to them. Never change a gate file to make a check pass.
- **The Stop hook** runs `./check` before an agent finishes a task that changed files.
- **The architecture reviewer** subagent checks the judgment calls in this document before a pull request is opened.

## Changing code safely

- Work in small steps that each leave the check green. Keep refactoring and behavior changes in separate steps.
- Change a contract by expanding first and contracting later: add the new form, move the callers, then remove the old form.
- Build what the task needs and no more. Add options, modules, and dependencies when a need exists.
- When existing code breaks these rules, write new code by the rules instead of copying the old code, and fix the old code in a separate change.
