import Foundation
import NotesUseCases
import Persistence
import Testing
import TestSupport

@Test func notesAreListedNewestFirst() async throws {
    let directory = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: directory) }
    let store = FileNoteStore(fileURL: directory.appending(path: "notes.json"))
    let older = try Samples.note(1, createdAt: 100)
    let newer = try Samples.note(2, createdAt: 200)
    try await store.save(older)
    try await store.save(newer)
    let listNotes = ListNotes(store: store)

    #expect(try await listNotes() == [newer, older])
}
