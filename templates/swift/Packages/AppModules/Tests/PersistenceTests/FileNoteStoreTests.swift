import Domain
import Foundation
import Persistence
import Testing
import TestSupport

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

    @Test func fileWrittenByVersion1StillLoads() async throws {
        defer { try? FileManager.default.removeItem(at: directory) }
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let fileURL = directory.appending(path: "notes.json")
        // JSONEncoder writes a Date as seconds since 2001-01-01, so 1970-01-01 is -978307200.
        let version1 = #"[{"id":"00000000-0000-0000-0000-000000000001","title":"Note 1","createdAt":-978307200}]"#
        try Data(version1.utf8).write(to: fileURL)
        let expected = try Samples.note(1)

        #expect(try await FileNoteStore(fileURL: fileURL).allNotes() == [expected])
    }
}
