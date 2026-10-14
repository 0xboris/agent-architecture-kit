import Domain
import Foundation

/// The behavior every `NoteStore` must have. The fake runs it in
/// TestSupportTests, and the real store runs it in PersistenceTests, so the
/// fake cannot drift from the real implementation.
public enum NoteStoreContract {
    public struct Failure: Error, CustomStringConvertible {
        public let description: String
    }

    public static func verify(_ makeStore: () async throws -> any NoteStore) async throws {
        try await emptyStoreHasNoNotes(try await makeStore())
        try await savedNoteIsListed(try await makeStore())
        try await savingTheSameIDReplacesTheNote(try await makeStore())
    }

    static func emptyStoreHasNoNotes(_ store: any NoteStore) async throws {
        let notes = try await store.allNotes()
        try expect(notes.isEmpty, "an empty store lists no notes, got \(notes)")
    }

    static func savedNoteIsListed(_ store: any NoteStore) async throws {
        let note = try Samples.note(1)
        try await store.save(note)
        let notes = try await store.allNotes()
        try expect(notes == [note], "a saved note is listed, got \(notes)")
    }

    static func savingTheSameIDReplacesTheNote(_ store: any NoteStore) async throws {
        let original = try Samples.note(1)
        let replacement = Note(id: original.id, title: try NoteTitle("Changed"), createdAt: original.createdAt)
        try await store.save(original)
        try await store.save(replacement)
        let notes = try await store.allNotes()
        try expect(notes == [replacement], "saving the same id replaces the note, got \(notes)")
    }

    private static func expect(_ condition: Bool, _ description: String) throws {
        guard condition else { throw Failure(description: description) }
    }
}
