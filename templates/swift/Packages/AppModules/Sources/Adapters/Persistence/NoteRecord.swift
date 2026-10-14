import Domain
import Foundation

/// The stored form of a note. It never leaves this module; the store maps it
/// to and from the domain type. Its field names are the stored format, so
/// rename them only with a migration.
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
