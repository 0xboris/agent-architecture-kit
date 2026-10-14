import Domain
import Testing

@Test func titleIsTrimmed() throws {
    #expect(try NoteTitle("  Groceries  ").value == "Groceries")
}

@Test func emptyTitleIsRejected() {
    #expect(throws: NoteTitle.Invalid.empty) { try NoteTitle("   ") }
}

@Test func titleLongerThanTheLimitIsRejected() {
    let tooLong = String(repeating: "a", count: NoteTitle.maximumLength + 1)
    #expect(throws: NoteTitle.Invalid.tooLong(limit: NoteTitle.maximumLength)) { try NoteTitle(tooLong) }
}
