import Domain
import Foundation
import NotesUseCases
import Persistence
import Testing
import TestSupport

@Test func createdNoteGetsIDAndTimeFromThePortsAndIsStored() async throws {
    let directory = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: directory) }
    let store = FileNoteStore(fileURL: directory.appending(path: "notes.json"))
    let time = FakeTimeSource(now: Date(timeIntervalSince1970: 500))
    let createNote = CreateNote(store: store, time: time, ids: SequentialIDGenerator())

    let note = try await createNote(title: "Groceries")

    #expect(note.id == SequentialIDGenerator.id(1))
    #expect(note.createdAt == Date(timeIntervalSince1970: 500))
    #expect(try await store.allNotes() == [note])
}

@Test func invalidTitleIsNotStored() async throws {
    let directory = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: directory) }
    let store = FileNoteStore(fileURL: directory.appending(path: "notes.json"))
    let createNote = CreateNote(store: store, time: FakeTimeSource(), ids: SequentialIDGenerator())

    await #expect(throws: NoteTitle.Invalid.empty) { try await createNote(title: "") }
    #expect(try await store.allNotes().isEmpty)
}

@Test func failedSaveReachesTheCaller() async throws {
    struct Offline: Error {}
    let createNote = CreateNote(
        store: FailingNoteStore(failure: Offline()), time: FakeTimeSource(), ids: SequentialIDGenerator())

    await #expect(throws: Offline.self) { try await createNote(title: "Groceries") }
}
