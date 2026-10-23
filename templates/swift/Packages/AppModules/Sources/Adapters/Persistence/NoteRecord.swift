import Domain
import Foundation

struct NoteRecord: Codable {
    let id: UUID
    let title: String
    let createdAt: Date

    init(_ note: Note) {
        id = note.id
        title = note.title.value
        createdAt = note.createdAt
    }

    func toDomain() throws -> Note {
        Note(id: id, title: try NoteTitle(title), createdAt: createdAt)
    }
}
