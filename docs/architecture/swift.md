# The architecture in Swift

This guide shows how each part of `docs/ARCHITECTURE.md` looks in Swift. It holds the rules that come from the language and from Swift packages. `docs/architecture/stack.md` names the frameworks this project uses, such as the UI framework and the test framework, and how the reference slice uses them.

This guide belongs to the kit, and a kit upgrade replaces it, so the project does not edit it. Its examples name the kit's Notes slice. Once Notes is gone, the reference slice that `AGENTS.md` names shows the same patterns.

## Layout

All modules are targets of one local package, `Packages/AppModules`. The Xcode app target holds only `App/<Name>App.swift`, which creates the `AppContainer` and shows `RootView`.

```
App/<Name>App.swift                        composition root (@main)
Packages/AppModules/
  Package.swift                            targets and build dependencies
  Sources/
    AppComposition/                        composition root
    Domain/Model, Rules, Ports, Middleware domain
    Features/<Slice>/UI                    target <Slice>UI
    Features/<Slice>/UseCases              target <Slice>UseCases
    DesignSystem/                          shared UI
    Adapters/<Name>/                       one target per adapter
    Utilities/
    TestSupport/
  Tests/<Target>Tests/                     one test target per target
```

A new slice copies the reference slice: its two targets, their test targets, and `AppContainer+<Slice>.swift`. Add the targets to `Package.swift` next to the reference slice's targets, and add the UI and use case targets to the dependencies of `AppComposition`. Declare every target that a target's files import. The check builds with `--explicit-target-dependency-import-check=error`, because SwiftPM otherwise lets a target import any module that happens to be built.

SwiftPM does not stop a target from importing a system framework such as SwiftUI or CoreData. The architecture check does, because each kind lists the frameworks it may import in `architecture.json`.

## Domain

- **Model.** Structs and enums that are `Sendable` and `Equatable`. A value with rules has a throwing initializer with typed throws and no public memberwise initializer, like `NoteTitle`.
- **Rules.** Pure functions, often as static functions on a caseless enum, like `NoteOrdering.newestFirst`.
- **Ports.** Protocols that refine `Sendable`. Their methods are `async throws` when the real implementation does I/O. When a call has several expected outcomes, return an enum of them, so that callers handle each one. The time port is `TimeSource`, because `Clock` is a standard library protocol.
- **Middleware.** A struct that conforms to the port and wraps another instance of it, like `LoggingNoteStore`.

The domain imports only Foundation, for value types such as `Date` and `UUID`. It must not call `Date()`, `UUID()`, `FileManager`, `UserDefaults`, `Locale.current`, or similar APIs. The check lists them. Take the time and ids from ports.

## Slices

- **Use cases** are `Sendable` structs that take ports and settings in their initializer and expose `callAsFunction`. Settings are plain values, such as a retention period, that the composition root passes in. They throw domain errors unchanged, so the UI can tell the cases apart.
- **The UI target** takes the slice's use cases in its initializers and holds no storage access of its own. Read stored data through a use case.

## Adapters

An adapter target imports the domain and its library. It maps between its own records and domain types, and its records never leave the adapter. Use an `actor` when the adapter has mutable state.

For Core Data or SwiftData, put the managed objects or `@Model` types in the persistence adapter and map them to domain structs there. Keep each versioned schema in its own file, and never change a schema that has shipped. Add a new version with a migration stage instead.

## Composition root

- `AppDependencies` lists the adapters. `LiveDependencies.swift` creates the real ones.
- `AppContainer` applies the mandatory middleware in its initializer.
- `AppContainer+<Slice>.swift` builds each slice's UI objects and decides which optional middleware the slice gets.
- `RootView` creates the root UI objects and shows the screens.
- Control flow is allowed only in `LaunchConfiguration.swift` and `BackgroundTasks.swift`. Register background tasks in `BackgroundTasks.swift`, and call a slice's use case from there.

Allowed file names and the size limit are in `architecture.json`.

## Tests

- Use case, UI, middleware, and composition tests use the real adapter, such as a `FileNoteStore` in a temporary directory, and assert what the store returns afterwards. Their test targets depend on the adapter's target.
- TestSupport holds sample data, like `Samples.note`, small fakes for ports whose state a test drives, like `FakeTimeSource` and `SequentialIDGenerator`, and implementations that fail, like `FailingNoteStore`.
- The adapter's own tests run against the real system, such as a temporary directory. A stored format has a test that loads data in that format as an earlier version wrote it, like `fileWrittenByVersion1StillLoads`.
- `AppCompositionTests` builds `AppContainer` on a temporary store and checks which middleware the slices receive.

## Concurrency

The package uses the Swift 6 language mode, so the compiler reports data races. Shared mutable state lives in an actor or on the main actor. Inside an actor, every `await` lets other calls run, so keep a check and the action that depends on it free of any `await` between them. Keep each `Task` you start in a property of its owner, and cancel it when the owner goes away.
