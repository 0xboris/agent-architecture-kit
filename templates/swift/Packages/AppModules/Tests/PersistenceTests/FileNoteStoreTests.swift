import Domain
import Foundation
import Persistence
import Testing
import TestSupport

/// The adapter is tested against the real file system, in a temporary directory.
struct FileNoteStoreTests {
    let directory = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)

    func makeStore() -> FileNoteStore {
        FileNoteStore(fileURL: directory.appending(path: "notes.json"))
    }

    @Test func newStoreListsNoNotes() async throws {
        defer { try? FileManager.default.removeItem(at: directory) }
        #expect(try await makeStore().allNotes().isEmpty)
    }

    @Test func savedNoteIsListed() async throws {
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = makeStore()
        let note = try Samples.note(1)

        try await store.save(note)

        #expect(try await store.allNotes() == [note])
    }

    @Test func savingTheSameIDReplacesTheNote() async throws {
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = makeStore()
        let original = try Samples.note(1)
        let replacement = Note(id: original.id, title: try NoteTitle("Changed"), createdAt: original.createdAt)

        try await store.save(original)
        try await store.save(replacement)

        #expect(try await store.allNotes() == [replacement])
    }
}
