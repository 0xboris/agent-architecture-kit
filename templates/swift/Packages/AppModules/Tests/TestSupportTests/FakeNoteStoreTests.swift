import Testing
import TestSupport

@Test func fakeNoteStoreMeetsTheContract() async throws {
    try await NoteStoreContract.verify { FakeNoteStore() }
}
