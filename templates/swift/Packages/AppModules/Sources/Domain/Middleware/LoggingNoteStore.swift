import Utilities

public struct LoggingNoteStore: NoteStore {
    private let base: any NoteStore
    private let logger: any AppLogger

    public init(_ base: any NoteStore, logger: any AppLogger) {
        self.base = base
        self.logger = logger
    }

    public func allNotes() async throws -> [Note] {
        try await base.allNotes()
    }

    public func save(_ note: Note) async throws {
        try await base.save(note)
        logger.info("note saved", metadata: ["id": note.id.uuidString])
    }
}
