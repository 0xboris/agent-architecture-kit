import Domain
import Foundation

public struct CreateNote: Sendable {
    private let store: any NoteStore
    private let time: any TimeSource
    private let ids: any IDGenerator

    public init(store: any NoteStore, time: any TimeSource, ids: any IDGenerator) {
        self.store = store
        self.time = time
        self.ids = ids
    }

    public func callAsFunction(title rawTitle: String) async throws -> Note {
        let title = try NoteTitle(rawTitle)
        let note = Note(id: ids.makeID(), title: title, createdAt: time.now())
        try await store.save(note)
        return note
    }
}
