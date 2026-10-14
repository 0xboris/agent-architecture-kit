import Domain
import Foundation

/// Stores notes as JSON in one file. Replace it with Core Data, SwiftData, or
/// SQLite as the app grows; the domain and the slices do not change.
public actor FileNoteStore: NoteStore {
    private let fileURL: URL

    public init(fileURL: URL) {
        self.fileURL = fileURL
    }

    public func allNotes() async throws -> [Note] {
        try readRecords().map { try $0.toDomain() }
    }

    public func save(_ note: Note) async throws {
        var records = try readRecords()
        records.removeAll { $0.id == note.id }
        records.append(NoteRecord(note))
        try write(records)
    }

    private func readRecords() throws -> [NoteRecord] {
        guard FileManager.default.fileExists(atPath: fileURL.path(percentEncoded: false)) else { return [] }
        return try JSONDecoder().decode([NoteRecord].self, from: Data(contentsOf: fileURL))
    }

    private func write(_ records: [NoteRecord]) throws {
        try FileManager.default.createDirectory(
            at: fileURL.deletingLastPathComponent(), withIntermediateDirectories: true)
        try JSONEncoder().encode(records).write(to: fileURL, options: .atomic)
    }
}
