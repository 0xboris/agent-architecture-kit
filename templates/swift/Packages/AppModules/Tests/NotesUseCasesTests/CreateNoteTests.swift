import Domain
import Foundation
import NotesUseCases
import Testing
import TestSupport

@Test func createdNoteGetsIDAndTimeFromThePorts() async throws {
    let store = FakeNoteStore()
    let time = FakeTimeSource(now: Date(timeIntervalSince1970: 500))
    let createNote = CreateNote(store: store, time: time, ids: SequentialIDGenerator())

    let note = try await createNote(title: "Groceries")

    #expect(note.id == SequentialIDGenerator.id(1))
    #expect(note.createdAt == Date(timeIntervalSince1970: 500))
    #expect(try await store.allNotes() == [note])
}

@Test func invalidTitleIsNotStored() async throws {
    let store = FakeNoteStore()
    let createNote = CreateNote(store: store, time: FakeTimeSource(), ids: SequentialIDGenerator())

    await #expect(throws: NoteTitle.Invalid.empty) { try await createNote(title: "") }
    #expect(try await store.allNotes().isEmpty)
}
