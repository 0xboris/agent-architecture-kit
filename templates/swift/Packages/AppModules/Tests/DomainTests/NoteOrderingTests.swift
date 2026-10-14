import Domain
import Testing
import TestSupport

@Test func newestNoteComesFirst() throws {
    let older = try Samples.note(1, createdAt: 100)
    let newer = try Samples.note(2, createdAt: 200)
    #expect(NoteOrdering.newestFirst([older, newer]) == [newer, older])
}

@Test func notesWithTheSameTimeAreOrderedByID() throws {
    let first = try Samples.note(1, createdAt: 100)
    let second = try Samples.note(2, createdAt: 100)
    #expect(NoteOrdering.newestFirst([second, first]) == [first, second])
}
