import Foundation

public struct Note: Identifiable, Equatable, Sendable {
    public let id: UUID
    public let title: NoteTitle
    public let createdAt: Date

    public init(id: UUID, title: NoteTitle, createdAt: Date) {
        self.id = id
        self.title = title
        self.createdAt = createdAt
    }
}
