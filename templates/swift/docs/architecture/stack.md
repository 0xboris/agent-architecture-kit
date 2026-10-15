# Stack

The frameworks this project uses, and how the reference slice uses them. `docs/architecture/swift.md` holds the rules that hold for any framework. This file belongs to the project: when the project changes a framework, it updates this file in the same change.

## UI

- **View models** are `@MainActor @Observable final class`es from Observation that take use cases in their initializer. Their state is one enum, such as loading, loaded, and failed.
- **Screens** are SwiftUI views that hold the view model in `@State` and call it from `.task` or actions.
- A SwiftUI view may read dependencies from `@Environment`; all other types take them through initializers. `@Query`, `@FetchRequest`, and `@AppStorage` read storage directly, so they are not allowed in UI targets.
- For previews, define small sample data or a private in-memory port implementation inside `#if DEBUG` in the UI target; TestSupport stays test-only.

## Logging

The Platform adapter implements `AppLogger` with `os.Logger`. Test support guards its state with `OSAllocatedUnfairLock`.

## Tests

- Tests use Swift Testing: `import Testing`, `@Test`, and `#expect`. Unwrap with `#require` instead of `!` or `try!`.
- A stub takes its results in its initializer and records its calls:

  ```swift
  let store = StubNoteStore(failure: Offline())
  // ... run the use case ...
  #expect(await store.saved.isEmpty)
  ```

## Storage

`FileNoteStore` keeps the notes in a JSON file. It stands in for Core Data or SwiftData until the app needs one.

## Commands

`./check` runs the architecture check, `swift build` with the explicit import check, `swift test`, and SwiftLint when it is installed. It builds and tests the package on macOS. Once the Xcode project exists, also build the app for iOS in CI, for example with `xcodebuild -scheme <Name> -destination "generic/platform=iOS Simulator" build`. That build catches iOS-only API use in UI targets that the macOS package build cannot see.

## Changing a framework

1. Allow the new framework for the kinds that use it in `architecture.json`, under `external.allow`. Frameworks belong in UI, adapters, and the composition root, never in the domain or use cases.
2. Rewrite the reference slice and its tests with the new framework, so that agents copy the new patterns.
3. Update the commands in `./check` and the CI workflow.
4. Update this file.
