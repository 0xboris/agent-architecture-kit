/// Stores notes between runs. Persistence implements it, TestSupport fakes it,
/// and `NoteStoreContract` checks that both behave the same.
public protocol NoteStore: Sendable {
    func allNotes() async throws -> [Note]
    func save(_ note: Note) async throws
}
