# The architecture in TypeScript

This guide shows how each part of `docs/ARCHITECTURE.md` looks in this TypeScript project. The notes slice is the working example for every section.

## Layout

```
src/app/                         composition root: main.ts, container.ts, config.ts, live.ts, wire-<slice>.ts
src/domain/                      domain: model, rules, ports
src/domain/middleware/           domain: middleware
src/features/<slice>/ui/         UI of a slice (routes)
src/features/<slice>/usecases/   use cases of a slice
src/sharedui/                    shared UI, such as the router and JSON helpers
src/adapters/<name>/             one directory per adapter
src/utilities/
src/testsupport/
```

A module is a directory and everything below it. Slice directories are kebab-case, such as `recurring-transactions`. `python3 tools/new.py slice <Name>` creates the directories, their tests, and the wiring file, and adds the wiring to `src/app/container.ts`.

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
- **Ports.** Interfaces that return promises when the real implementation does I/O.
- **Middleware.** A class that implements a port and wraps another instance of it, like `LoggingNoteStore`.

The domain imports no packages and no Node built-ins. It must not call `Date.now()`, `new Date()` without arguments, `Math.random()`, `crypto.randomUUID()`, `fetch`, timers, or `process.env`, and must not log through `console`. Take the time and ids from ports.

## Slices

- **Use cases** are classes with private `#` fields, a constructor that takes an object of ports, and a `run` method.
- **Routes** are a function that takes the use cases and a logger and returns `Route` objects for the shared router. Request bodies arrive as `unknown` and go through a parse function before use. Response types stay in the routes file.
- Routes log the errors they handle and map result errors to status codes.

## Adapters

An adapter imports the domain and any packages it needs. It parses what it reads, since stored data is outside data, and maps it to domain types. `FileNoteStore` shows how to serialize access with a promise queue and how to write atomically with a temporary file and a rename.

## Composition root

- `container.ts` defines `Dependencies` and `createApp`. `createApp` applies the mandatory middleware and collects the routes of every slice.
- `wire-<slice>.ts` builds the slice's use cases and routes, and decides which optional middleware the slice gets.
- `live.ts` creates the real adapters, `config.ts` reads the environment, and `main.ts` starts the server.
- Control flow is allowed only in `config.ts`.

## Test support and tests

- Tests use `node:test` and `node:assert/strict`. A test file sits next to the code it tests and ends in `.test.ts`.
- Fakes keep state in private fields and can inject a failure, like `FakeNoteStore.failNextCall`.
- A contract is a function that registers a `describe` block for any implementation, like `noteStoreContract`. `fakes.test.ts` runs it against the fake, and the adapter's test runs it against the real implementation in a temporary directory.
- `startTestServer` from test support runs routes on a free port for a test.
- `src/app/container.test.ts` is the composition test. It builds the app with fakes and sends real requests to it.

`./check` installs the dependencies when `node_modules` is missing, then runs the architecture check, `tsc --noEmit`, and the tests.
