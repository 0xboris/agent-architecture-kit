import Domain
import Foundation

/// Sample domain values for tests.
public enum Samples {
    public static func note(_ number: Int, createdAt seconds: TimeInterval = 0) throws -> Note {
        Note(
            id: SequentialIDGenerator.id(number),
            title: try NoteTitle("Note \(number)"),
            createdAt: Date(timeIntervalSince1970: seconds)
        )
    }
}
