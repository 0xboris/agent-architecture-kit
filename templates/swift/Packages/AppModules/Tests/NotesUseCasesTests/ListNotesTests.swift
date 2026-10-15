import NotesUseCases
import Testing
import TestSupport

@Test func notesAreListedNewestFirst() async throws {
    let older = try Samples.note(1, createdAt: 100)
    let newer = try Samples.note(2, createdAt: 200)
    let listNotes = ListNotes(store: StubNoteStore(notes: [older, newer]))

    #expect(try await listNotes() == [newer, older])
}
