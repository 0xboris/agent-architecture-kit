import Domain
import Foundation
import NotesUseCases
import Testing
import TestSupport

@Test func createdNoteGetsIDAndTimeFromThePortsAndIsSaved() async throws {
    let store = StubNoteStore()
    let time = FakeTimeSource(now: Date(timeIntervalSince1970: 500))
    let createNote = CreateNote(store: store, time: time, ids: SequentialIDGenerator())

    let note = try await createNote(title: "Groceries")

    #expect(note.id == SequentialIDGenerator.id(1))
    #expect(note.createdAt == Date(timeIntervalSince1970: 500))
    #expect(await store.saved == [note])
}

@Test func invalidTitleIsNotSaved() async throws {
    let store = StubNoteStore()
    let createNote = CreateNote(store: store, time: FakeTimeSource(), ids: SequentialIDGenerator())

    await #expect(throws: NoteTitle.Invalid.empty) { try await createNote(title: "") }
    #expect(await store.saved.isEmpty)
}

@Test func failedSaveReachesTheCaller() async throws {
    struct Offline: Error {}
    let createNote = CreateNote(store: StubNoteStore(failure: Offline()), time: FakeTimeSource(), ids: SequentialIDGenerator())

    await #expect(throws: Offline.self) { try await createNote(title: "Groceries") }
}
