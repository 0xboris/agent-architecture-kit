import Domain

/// A `NoteStore` whose every call throws `failure`, so a test can reach the error paths.
public struct FailingNoteStore: NoteStore {
    private let failure: any Error

    public init(failure: any Error) {
        self.failure = failure
    }

    public func allNotes() async throws -> [Note] {
        throw failure
    }

    public func save(_ note: Note) async throws {
        throw failure
    }
}
