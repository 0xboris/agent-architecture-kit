import Domain

@MainActor
public final class AppContainer {
    let dependencies: AppDependencies

    let noteStore: any NoteStore

    public init(dependencies: AppDependencies) {
        self.dependencies = dependencies
        noteStore = LoggingNoteStore(dependencies.noteStore, logger: dependencies.logger)
    }
}
