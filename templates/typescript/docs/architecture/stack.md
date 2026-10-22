# Stack

The libraries this project uses, and how the reference slice uses them. `docs/architecture/typescript.md` holds the rules that hold for any library. This file belongs to the project: when the project changes a library, it updates this file in the same change. Like everything in `docs/architecture/`, it is a gate file, so changes need the owner's review.

The kit's template uses Node's built-in modules only, plus TypeScript 7 and oxlint for checking.

## HTTP

- `src/sharedui/http.ts` is a small router on `node:http`. A route is an object with `method`, `path`, and `handle`.
- A slice's UI module is a function that takes the bound use cases and a logger and returns the slice's routes, like `notesRoutes`. `createApp` collects the routes of every slice into one router.
- `readJson`, `sendJson`, and `sendError` read and write JSON bodies.

## Tests

- Tests use `node:test` and `node:assert/strict`.
- Run a use case on a temporary store, then read back what it stored. `temporaryNoteStore(t)` deletes the store's directory when the test ends:

  ```ts
  const store = await temporaryNoteStore(t);
  const result = await createNote({ store, clock: new FakeClock(), ids: new SequentialIds() }, 'Groceries');
  assert.ok(result.ok);
  assert.deepEqual(await store.allNotes(), [result.value]);
  ```

- `failingNoteStore(error)` from test support rejects every call, for the error paths.
- `startTestServer` from test support runs routes on a free port for one test.
- A test double that only returns a value is written as `() => Promise.resolve(value)` or `() => Promise.reject(error)`. The linter's `require-await` rejects an `async` function without `await`.

## Storage

`FileNoteStore` keeps the notes in a JSON file. It stands in for a real database until the project needs one. It serializes access with a promise queue and writes atomically with a temporary file and a rename. Its tests run against the real file system in a temporary directory, and `testdata/notes-v1.json` pins the stored format.

## Lint

oxlint with type-aware rules, in `.oxlintrc.json`. `./check` runs it with `--disable-nested-config`, so a settings file in a subfolder cannot switch rules off. oxlint-tsgolint gives the type-aware rules their type information. It is built on TypeScript 7, so it reads `tsconfig.json` with the same compiler as `tsc`. typescript-eslint supports only TypeScript below 6.1, so it does not work here.

- The rules are the correctness category plus the rules of ESLint's and typescript-eslint's recommended sets, including the type-aware ones of `recommendedTypeChecked`.
- `consistent-type-assertions` with `assertionStyle: "never"` rejects type assertions, such as `'x' as NoteTitle`, in all production code. A branded value comes from its type guard, such as `isNoteTitle`. Tests, `*.testing.ts` files, and test support may assert. `as const` is allowed everywhere. The rule's message suggests a type annotation instead. For a branded type, use its type guard or parse function.
- `no-unsafe-assignment`, `no-unsafe-return`, and the other `no-unsafe` rules reject an `any` value, such as the result of `JSON.parse`, flowing into a typed value. Parse outside data with a parse function instead.
- `no-floating-promises` allows `test` from `node:test`, whose promise the runner awaits.
- Warnings fail the step, and so do unused disable comments.

## Commands

- `npm install` installs the dependencies. `./check` runs it when `node_modules` is missing.
- `./check` runs the architecture check, oxlint, `tsc --noEmit`, and `node --test`. CI runs `npm ci` and then `./check`.
- `.claude/skills/verify-<name>/scripts/app` starts the service on a temporary data directory, sends requests to it, and keeps each request and response as evidence. Its `SKILL.md` has the steps.
- `npm run lint` runs oxlint alone.

## Changing a library

1. Allow the new package for the kinds that use it in `architecture.json`, under `external.allow`. Frameworks belong in UI, adapters, and the composition root, never in the domain or use cases. A pure library that does no I/O, such as Zod or a decimal library, may go in the domain. Other modules then import only the domain's types and parse functions, never the library's schemas or errors, and the domain maps the library's errors to its own error unions. A major upgrade of the library then changes only the domain. Write a scoped npm package with its scope, such as `@scope/package` or `@scope/*`. An entry like `@name` without a slash refers to a set in `externalSets`.
2. Rewrite the reference slice and its tests with the new library, so that agents copy the new patterns. Keep what the slice does unchanged, because it exists to show patterns, and new behavior belongs in real slices. Wire details that the new library decides, such as its validation errors, may change. Note them here.
3. Update the commands in `./check` and the CI workflow. When you change the package manager, also replace the lockfile and the install step in `./check`. Check that every new tool supports the project's TypeScript version: some linters lag behind the newest TypeScript, and tools that call the compiler's JavaScript API do not work with TypeScript 7.0. `docs/architecture/typescript.md` says how to give such a tool an older TypeScript of its own.
4. Add any new compiler, linter, or test runner settings file to `.github/CODEOWNERS` if it does not match a listed pattern yet.
5. Update this file. List libraries that the project has chosen but no code uses yet under a heading such as "Chosen, not set up yet", so that the next agent knows they are decided.
