# Stack

The libraries this project uses, and how the reference slice uses them. `docs/architecture/typescript.md` holds the rules that hold for any library. This file belongs to the project: when the project changes a library, it updates this file in the same change.

The kit's template uses Node's built-in modules only.

## HTTP

- `src/sharedui/http.ts` is a small router on `node:http`. A route is an object with `method`, `path`, and `handle`.
- A slice's UI module is a function that takes the use cases and a logger and returns the slice's routes, like `notesRoutes`. `createApp` collects the routes of every slice into one router.
- `readJson`, `sendJson`, and `sendError` read and write JSON bodies.

## Tests

- Tests use `node:test` and `node:assert/strict`.
- Record the calls to a port with `mock.fn` from `node:test`:

  ```ts
  const save = mock.fn<NoteStore['save']>(async () => {});
  const store: NoteStore = { allNotes: async () => [], save };
  // ... run the use case ...
  assert.deepEqual(save.mock.calls.map((call) => call.arguments), [[note]]);
  ```

- `startTestServer` from test support runs routes on a free port for one test.

## Storage

`FileNoteStore` keeps the notes in a JSON file. It stands in for a real database until the project needs one.

## Commands

- `npm install` installs the dependencies. `./check` runs it when `node_modules` is missing.
- `./check` runs the architecture check, `tsc --noEmit`, and `node --test`. CI runs `npm ci` and then `./check`.

## Changing a library

1. Allow the new package for the kinds that use it in `architecture.json`, under `external.allow`. Frameworks belong in UI, adapters, and the composition root, never in the domain or use cases.
2. Rewrite the reference slice and its tests with the new library, so that agents copy the new patterns.
3. Update the commands in `./check` and the CI workflow.
4. Update this file.
