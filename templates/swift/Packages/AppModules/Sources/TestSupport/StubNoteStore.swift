import Domain

/// A `NoteStore` that returns what a test sets and records the notes it
/// receives. It has no behavior of its own: a test passes the notes and the
/// failure it wants the code under test to handle.
public actor StubNoteStore: NoteStore {
    private let notes: [Note]
    private let failure: (any Error)?
    public private(set) var saved: [Note] = []

    public init(notes: [Note] = [], failure: (any Error)? = nil) {
        self.notes = notes
        self.failure = failure
    }

    public func allNotes() async throws -> [Note] {
        if let failure { throw failure }
        return notes
    }

    public func save(_ note: Note) async throws {
        saved.append(note)
        if let failure { throw failure }
    }
}
