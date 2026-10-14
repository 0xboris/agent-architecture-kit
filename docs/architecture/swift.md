# The architecture in Swift

This guide shows how each part of `docs/ARCHITECTURE.md` looks in this Swift project. The Notes slice is the working example for every section.

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

`python3 tools/new.py slice <Name>` adds the two slice targets, their test targets, and the composition dependencies to `Package.swift` at the `scaffold:` markers. If you add a target by hand, declare every target that its files import. The check builds with `--explicit-target-dependency-import-check=error`, because SwiftPM otherwise lets a target import any module that happens to be built.

SwiftPM does not stop a target from importing a system framework such as SwiftUI or CoreData. The architecture check does: each kind lists the frameworks it may import in `architecture.json`.

## Domain

- **Model.** Structs and enums that are `Sendable` and `Equatable`. A value with rules has a throwing initializer with typed throws and no public memberwise initializer, like `NoteTitle`.
- **Rules.** Pure functions, often as static functions on a caseless enum, like `NoteOrdering.newestFirst`.
- **Ports.** Protocols that refine `Sendable`. Their methods are `async throws` when the real implementation does I/O. The time port is `TimeSource`, because `Clock` is a standard library protocol.
- **Middleware.** A struct that conforms to the port and wraps another instance of it, like `LoggingNoteStore`.

The domain imports only Foundation, for value types such as `Date` and `UUID`. It must not call `Date()`, `UUID()`, `FileManager`, `UserDefaults`, `Locale.current`, or similar APIs; the check lists them. Take the time and ids from ports.

## Slices

- **Use cases** are `Sendable` structs that take ports in their initializer and expose `callAsFunction`. They throw domain errors unchanged, so the UI can tell the cases apart.
- **View models** are `@MainActor @Observable final class`es that take use cases in their initializer. Their state is one enum, such as loading, loaded, and failed.
- **Screens** are SwiftUI views that hold the view model in `@State` and call it from `.task` or actions.

A SwiftUI view may read dependencies from `@Environment`; all other types take them through initializers. `@Query`, `@FetchRequest`, and `@AppStorage` read storage directly, so they are not allowed in UI modules. Read stored data through a use case. For previews, define small sample data or a private in-memory port implementation inside `#if DEBUG` in the UI module; TestSupport stays test-only.

## Adapters

An adapter target imports the domain and its library. It maps between its own records and domain types; `NoteRecord` never leaves Persistence. Use an `actor` when the adapter has mutable state.

For Core Data or SwiftData, put the managed objects or `@Model` types in the Persistence adapter and map them to domain structs there. Keep each versioned schema in its own file, and never change a schema that has shipped. Add a new version with a migration stage instead.

## Composition root

- `AppDependencies` lists the adapters. `LiveDependencies.swift` creates the real ones.
- `AppContainer` applies the mandatory middleware in its initializer.
- `AppContainer+<Slice>.swift` builds each slice's view models and decides which optional middleware the slice gets.
- `RootView` creates the root view models and shows the screens.
- Control flow is allowed only in `LaunchConfiguration.swift` and `BackgroundTasks.swift`. Register background tasks in `BackgroundTasks.swift`, and call a slice's use case from there.

Allowed file names and the size limit are in `architecture.json`.

## Test support and tests

Tests use Swift Testing: `import Testing`, `@Test`, and `#expect`.

- Fakes are actors or `final class`es that guard their state with `OSAllocatedUnfairLock`. Each fake can inject a failure, like `FakeNoteStore.failNextCall(with:)`.
- `FakeTimeSource` and `SequentialIDGenerator` make time and ids predictable.
- A contract is an enum with a `verify` function that throws on a mismatch, like `NoteStoreContract`. `TestSupportTests` runs it against the fake, and the adapter's test target runs it against the real implementation.
- `AppCompositionTests` builds `AppContainer` with fakes and checks the wiring.
- Unwrap with `#require` instead of `!` or `try!`.

## Concurrency

The package uses the Swift 6 language mode, so the compiler reports data races. Shared mutable state lives in an actor or on the main actor. Inside an actor, every `await` lets other calls run, so keep a check and the action that depends on it free of any `await` between them. Keep each `Task` you start in a property of its owner, and cancel it when the owner goes away.

## Building the app

`./check` builds and tests the package on macOS. Once the Xcode project exists, also build the app for iOS in CI, for example with `xcodebuild -scheme <Name> -destination "generic/platform=iOS Simulator" build`. That build catches iOS-only API use in UI targets that the macOS package build cannot see.
