import Domain
import Foundation

/// The shared fake for `NoteStore`. `NoteStoreContract` checks that it behaves
/// like the real store. Use `failNextCall(with:)` to test error handling.
public actor FakeNoteStore: NoteStore {
    private var notes: [UUID: Note]
    private var nextFailure: (any Error)?

    public init(notes: [Note] = []) {
        self.notes = Dictionary(uniqueKeysWithValues: notes.map { ($0.id, $0) })
    }

    public func failNextCall(with error: any Error) {
        nextFailure = error
    }

    public func allNotes() async throws -> [Note] {
        try throwPendingFailure()
        return Array(notes.values)
    }

    public func save(_ note: Note) async throws {
        try throwPendingFailure()
        notes[note.id] = note
    }

    private func throwPendingFailure() throws {
        if let failure = nextFailure {
            nextFailure = nil
            throw failure
        }
    }
}
