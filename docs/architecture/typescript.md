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
