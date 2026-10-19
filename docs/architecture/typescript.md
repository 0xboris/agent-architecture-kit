# The architecture in TypeScript

This guide shows how each part of `docs/ARCHITECTURE.md` looks in TypeScript. It holds the rules that come from the language. `docs/architecture/stack.md` names the libraries this project uses, such as the HTTP framework and the test runner, and how the reference slice uses them.

This guide belongs to the kit, and a kit upgrade replaces it, so the project does not edit it. Its examples name the kit's Notes slice. Once Notes is gone, the reference slice that `AGENTS.md` names shows the same patterns.

## Layout

```
src/app/                         composition root: main.ts, container.ts, config.ts, live.ts, wire-<slice>.ts
src/domain/                      domain: model, rules, ports
src/domain/middleware/           domain: middleware
src/features/<slice>/ui/         UI of a slice
src/features/<slice>/usecases/   use cases of a slice
src/sharedui/                    shared UI
src/adapters/<name>/             one directory per adapter
src/utilities/
src/testsupport/
```

A module is a directory and everything below it. Slice directories are kebab-case, such as `recurring-transactions`. A new slice copies the files of the reference slice: its UI module, its use case module, their tests, and `src/app/wire-<slice>.ts`, which `src/app/container.ts` calls.

## Language setup

Node runs the TypeScript files directly by stripping types, and `tsc --noEmit` checks them. That sets a few rules:

- Relative imports end in `.ts`, such as `import { newestFirst } from './ordering.ts'`.
- Only erasable syntax is allowed: no `enum`, no `namespace`, and no parameter properties. Use union types, plain objects, and explicit fields.
- Import types with `import type`, or with `type` inside the braces.
- Import Node built-ins with the `node:` prefix, such as `node:http`. The check treats a bare `fs` like any other package.

## Domain

- **Model.** Interfaces with `readonly` fields, and branded types for values with rules, like `NoteTitle`. Only the parse function creates a branded value, and it is the one place where `as NoteTitle` is allowed.
- **Results.** Expected failures are a `Result` from utilities, with a union of error cases, like `NoteTitleError`. Throw only for unexpected failures.
- **Rules.** Plain functions, like `newestFirst`.
- **Ports.** Interfaces that return promises when the real implementation does I/O. When a call has several expected outcomes, return a union of them, so that callers handle each one.
- **Middleware.** A class that implements a port and wraps another instance of it, like `LoggingNoteStore`.

The domain imports no packages and no Node built-ins. It must not call `Date.now()`, `new Date()` without arguments, `Math.random()`, `crypto.randomUUID()`, `fetch`, timers, or `process.env`, and must not log through `console`. Take the time and ids from ports.

## Slices

- **Use cases** are classes with private `#` fields, a constructor that takes an object of ports and settings, and a `run` method. Settings are plain values, such as a retention period, that `config.ts` reads and the wiring file passes in.
- **The UI module** takes the slice's use cases and a logger. Input arrives as `unknown` and goes through a parse function before use. Response and request types stay in the UI module and map to and from domain types.
- The UI module logs the errors it handles and maps result errors to output, such as status codes.

## Other entry points

- A background job or a scheduled task is an entry point of its slice, like a route. Its handler lives in the slice's UI module and calls the slice's use cases.
- The queue or scheduler that runs jobs is an adapter. The composition root registers each slice's jobs with it and sets their schedules from configuration.
- A use case that puts work on a queue does so through a port, which the queue adapter implements.
- When the service runs as more than one process, such as an API and a worker, each process gets its own entry file in `src/app`, such as `main.ts` and `worker.ts`. Add the new file to `allowedFiles` in `architecture.json`.

## Adapters

An adapter imports the domain and any packages it needs. It parses what it reads, since stored data is outside data, and maps it to domain types.

Schema files and migrations belong to the adapter that owns the storage. Never edit a migration that has shipped. A helper that creates a real database for tests lives in the adapter module, next to the adapter's tests, in a `*.testing.ts` file, because test support may not import adapters.

## Composition root

- `container.ts` defines `Dependencies` and `createApp`. `createApp` applies the mandatory middleware and collects every slice.
- `wire-<slice>.ts` builds the slice's use cases and UI, and decides which optional middleware the slice gets.
- `live.ts` creates the real adapters, `config.ts` reads the environment, and `main.ts` starts the process.
- When an adapter holds a resource that must be closed, such as a database pool, `live.ts` returns it next to the dependencies, for example as `{ dependencies, migrate, close }`, and `main.ts` closes it on shutdown.
- Migrations run before the process serves. `main.ts` applies them at start, or a separate entry file such as `migrate.ts` does.
- Control flow is allowed only in `config.ts`. Elsewhere, handle a failed start with `.catch()` on the promise, which the check allows, rather than with `try` and `catch`.

## Tests

- A test file sits next to the code it tests and ends in `.test.ts`.
- A stub is an object literal typed as the port, such as `const store: NoteStore = { ... }`. The compiler then fails the test when the port changes. Record calls with the test runner's mock functions, typed with the port's method, such as `NoteStore['save']`.
- Test support holds sample data, like `sampleNote`, and small fakes for ports whose state a test drives, like `FakeClock`.
- The adapter's own tests run against the real system, such as a real database or a temporary directory.
- Name a helper that only tests use, such as a function that creates a database for the adapter's tests, `*.testing.ts`. The check treats it as test code, so production code cannot import it.
- `src/app/container.test.ts` is the composition test. It builds the app with stubs and checks which middleware the slices receive.

## Several apps in one repository

A pnpm workspace holds the apps and the shared domain. `docs/ARCHITECTURE.md` gives the rules; this is how they look in TypeScript.

```
packages/domain/src/             shared domain: model, parse functions, pure rules, Result; index.ts is its entry
apps/api/                        the service, laid out as above, with openapi.json next to its package.json
apps/web/src/app/                composition root: main.tsx, container.tsx, routes.tsx, config.ts, live.ts, wire-<slice>.ts
apps/web/src/domain/             the web app's ports, such as the API it calls
apps/web/src/features/<slice>/   usecases/ and ui/, with ui/index.ts as the UI's public entry
apps/web/src/screens/<name>/     pages that arrange the public UI of slices
apps/web/src/sharedui/           layout, styles, and components without business meaning
apps/web/src/adapters/api/       the generated API client and the adapter that parses its responses
```

- **One `architecture.json` at the root** maps the modules of every app. Each module of an app has an `"app"` field, and the shared domain has none. An import between apps fails as `app`.
- **The shared domain is a workspace package**, such as `@acme/domain`, whose `exports` field points at `src/index.ts`. Apps import it by name, and `typescript.aliases` in `architecture.json` maps the name to its directory, so the check sees the import. Its `tsconfig.json` sets `"types": []`, so code that needs Node does not compile there. It holds `Result` too, since it may not import an app's utilities.
- **Kinds differ per app where the libraries differ.** An app whose UI uses other libraries gets kinds of its own, such as `web-ui` and `web-composition` next to `ui` and `composition`. Kinds without libraries, such as `domain` and `usecases`, are shared by every app.
- **A slice's UI has a public entry.** `"publicEntry": ["index.ts"]` on the UI kind makes every other module, screens and the composition root included, import the slice's UI from `ui/index.ts`. The check reports any import that reaches past it.
- **UI components get their use cases from the slice.** The slice's UI exports a provider, such as `NotesProvider`, that the composition root fills with the slice's use cases. Components read them from it, so a screen can place a component without knowing its use cases.
- **Screens import slice UI and shared UI only.** Routes are defined in code in the composition root, not by a framework's file layout, and each route shows one screen.
- **The contract lives with the API.** A composition file, such as `openapi.ts`, prints the OpenAPI document from the routes, and the API commits it as `openapi.json`. The web app generates its client types from it into `adapters/api/`. `./check` regenerates both and fails when either differs from the committed file.
- **The API adapter of a client** implements the client's port with the generated client and parses every response with the shared parse functions. Its tests answer requests with recorded responses in the contract's shape.
- **Tests of UI components** render them with real use cases on a stubbed port, inside the providers they need. A helper that sets this up is a `*.testing.tsx` file in the slice's UI, so production code cannot import it.

