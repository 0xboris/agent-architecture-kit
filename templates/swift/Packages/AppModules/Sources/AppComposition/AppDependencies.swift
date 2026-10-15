import Domain
import Utilities

/// The adapters that the app runs with. `live()` creates the real ones;
/// the composition test passes stubs from TestSupport.
public struct AppDependencies: Sendable {
    public var noteStore: any NoteStore
    public var time: any TimeSource
    public var ids: any IDGenerator
    public var logger: any AppLogger

    public init(noteStore: any NoteStore, time: any TimeSource, ids: any IDGenerator, logger: any AppLogger) {
        self.noteStore = noteStore
        self.time = time
        self.ids = ids
        self.logger = logger
    }
}
