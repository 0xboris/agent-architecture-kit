import Foundation

/// A note title that follows the title rules. The only way to create one is
/// the checking initializer, so every `NoteTitle` in the app is valid.
public struct NoteTitle: Equatable, Sendable {
    public static let maximumLength = 200

    public enum Invalid: Error, Equatable {
        case empty
        case tooLong(limit: Int)
    }

    public let value: String

    public init(_ raw: String) throws(Invalid) {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw .empty }
        guard trimmed.count <= Self.maximumLength else { throw .tooLong(limit: Self.maximumLength) }
        value = trimmed
    }
}
