import Domain

public struct ListNotes: Sendable {
    private let store: any NoteStore

    public init(store: any NoteStore) {
        self.store = store
    }

    public func callAsFunction() async throws -> [Note] {
        NoteOrdering.newestFirst(try await store.allNotes())
    }
}
