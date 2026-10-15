# The architecture in Go

This guide shows how each part of `docs/ARCHITECTURE.md` looks in Go. It holds the rules that come from the language. `docs/architecture/stack.md` names the libraries this project uses, such as the HTTP router and the logger, and how the reference slice uses them.

## Layout

```
cmd/server/main.go                    composition root: entry point
internal/app/                         composition root: app.go, config.go, live.go, wire_<slice>.go
internal/domain/                      domain: model, rules, ports
internal/domain/middleware/           domain: middleware
internal/features/<slice>/ui/         UI of a slice
internal/features/<slice>/usecases/   use cases of a slice
internal/sharedui/                    shared UI
internal/adapters/<name>/             one directory per adapter
internal/utilities/
internal/testsupport/
```

A module is a directory and every package below it. `internal/domain/middleware` belongs to the domain module. Slice directories use lowercase names without separators, such as `recurringtransactions`. A new slice copies the files of the reference slice: its `ui` and `usecases` packages, their tests, and `internal/app/wire_<slice>.go`, which `New` in `internal/app/app.go` calls.

## Domain

- **Model.** Structs and named types. A value with rules has unexported fields and a constructor that returns an error, like `NewNoteTitle`. Treat its zero value as invalid.
- **Rules.** Plain functions, like `NewestFirst`.
- **Errors.** Exported sentinel errors or error types, like `ErrTitleEmpty`. Callers check them with `errors.Is` or `errors.As`, and code wraps underlying errors with `fmt.Errorf("...: %w", err)`. A port documents the errors it returns, so callers and their tests can handle each one.
- **Ports.** Interfaces in `ports.go` or in a file per port. Methods that may do I/O take a `context.Context` first.
- **Middleware.** A struct in `domain/middleware` that wraps a port and implements it, like `LoggingNoteStore`.

The domain may import the standard library except the I/O packages that `architecture.json` lists under `io-packages`, such as `net/...`, `os`, and `database/sql`. It may use the `time.Time` type but must not call `time.Now`, `time.Sleep`, or similar functions. Take the time from the `Clock` port.

## Slices

- **Use cases** are structs with unexported port fields, a `NewX` constructor, and a `Run(ctx, ...)` method.
- **The UI package** takes the slice's use cases and a logger in its constructor. Request and response types stay in the UI package and map to and from domain types.
- The UI package logs the errors it handles and maps domain errors to output with `errors.Is`.

UI code may not make outgoing requests or touch the file system. Put that behind a port.

## Adapters

An adapter package imports the domain and whatever libraries it needs. It keeps its stored or wire records unexported and maps them to domain types. Guard mutable state with a `sync.Mutex`. The `filestore` adapter shows atomic writes: it writes a temporary file and then renames it.

For SQL databases, keep numbered migrations in the adapter, and never edit a migration that has shipped.

## Composition root

- `app.go` defines `Dependencies` and `New`. `New` applies the mandatory middleware and calls one `wireX` method per slice.
- `wire_<slice>.go` builds the slice's use cases and UI, and decides which optional middleware the slice gets.
- `live.go` creates the real adapters, and `config.go` reads the environment.
- `cmd/server/main.go` reads the config, builds the app, and starts it.
- Control flow is allowed in `config.go`. Elsewhere only `if err != nil {` and `if err := ...; err != nil {` are allowed, for error handling.

## Tests

- Tests use the standard `testing` package. Domain and middleware tests that need test support live in external test packages, such as `domain_test`, to avoid an import cycle.
- A stub is a struct in test support with exported fields for the results a test sets, like `StubNoteStore`. It records what it receives, guards that record with a mutex, and asserts at compile time that it implements the port: `var _ domain.NoteStore = (*StubNoteStore)(nil)`.
- Test support also holds sample data, like `SampleNote`, and small fakes for ports whose state a test drives, like `FakeClock`.
- The adapter's own tests run against the real system. The `filestore` tests use `t.TempDir()`.
- `internal/app/app_test.go` is the composition test. It builds the app with stubs and checks which middleware the slices receive.

Tests must pass in any order and without data races.
