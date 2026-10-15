# Stack

The libraries this project uses, and how the reference slice uses them. `docs/architecture/go.md` holds the rules that hold for any library. This file belongs to the project: when the project changes a library, it updates this file in the same change. Like everything in `docs/architecture/`, it is a gate file, so changes need the owner's review.

The kit's template uses the standard library only.

## HTTP

- Handlers use `net/http` with `http.ServeMux` and method patterns, such as `"POST /notes"`.
- A slice's UI package has a `Handler` with `NewHandler(useCases..., logger)` and `Register(mux)`, like the notes slice. `New` in `internal/app/app.go` creates one mux, and each `wireX` registers its slice on it.
- `internal/sharedui/httpjson` reads and writes JSON. Reading ignores unknown fields, so newer clients can send fields that this version does not know yet.

## Logging

The platform adapter implements `utilities.Logger` with `log/slog`.

## Tests

- Tests use `testing`, and handler tests use `net/http/httptest` with `httptest.NewRecorder`.
- A stub sets its results in fields and records its calls:

  ```go
  store := &testsupport.StubNoteStore{Err: errors.New("offline")}
  // ... run the use case ...
  if saved := store.Saved(); len(saved) != 1 { t.Fatalf(...) }
  ```

## Storage

The `filestore` adapter keeps the notes in a JSON file. It stands in for a real database until the project needs one.

## Commands

`./check` runs the architecture check, `gofmt`, `go vet`, and `go test -race -shuffle=on`. Run `go mod tidy` after adding a dependency.

## Changing a library

1. Allow the new package for the kinds that use it in `architecture.json`, under `external.allow`. Frameworks belong in UI, adapters, and the composition root, never in the domain or use cases.
2. Rewrite the reference slice and its tests with the new library, so that agents copy the new patterns. Keep what the slice does unchanged: it exists to show patterns, and new behavior belongs in real slices.
3. Update the commands in `./check` and the CI workflow.
4. Add any new compiler, linter, or test runner settings file to `.github/CODEOWNERS` if it does not match a listed pattern yet.
5. Update this file. List libraries that the project has chosen but no code uses yet under a heading such as "Chosen, not set up yet", so that the next agent knows they are decided.
