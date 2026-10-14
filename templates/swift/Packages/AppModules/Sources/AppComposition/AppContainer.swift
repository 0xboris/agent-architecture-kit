import Domain

/// The composition root. It applies middleware and builds each slice in an
/// `AppContainer+<Slice>.swift` extension. It holds wiring only: no control
/// flow and no feature code.
@MainActor
public final class AppContainer {
    let dependencies: AppDependencies

    /// Mandatory middleware: applied once here, so no slice receives the bare store.
    let noteStore: any NoteStore

    public init(dependencies: AppDependencies) {
        self.dependencies = dependencies
        noteStore = LoggingNoteStore(dependencies.noteStore, logger: dependencies.logger)
    }
}
