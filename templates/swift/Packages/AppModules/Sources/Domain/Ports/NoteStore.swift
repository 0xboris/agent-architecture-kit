/// Stores notes between runs. Persistence implements it.
public protocol NoteStore: Sendable {
    func allNotes() async throws -> [Note]
    func save(_ note: Note) async throws
}
