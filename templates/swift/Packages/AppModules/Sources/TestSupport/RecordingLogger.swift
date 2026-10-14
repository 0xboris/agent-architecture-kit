import os
import Utilities

/// Records every log call so tests can assert on what was logged.
public final class RecordingLogger: AppLogger {
    public struct Entry: Equatable, Sendable {
        public let level: String
        public let message: String
        public let metadata: [String: String]
    }

    private let entries = OSAllocatedUnfairLock(initialState: [Entry]())

    public init() {}

    public var recorded: [Entry] {
        entries.withLock { $0 }
    }

    public func info(_ message: String, metadata: [String: String]) {
        entries.withLock { $0.append(Entry(level: "info", message: message, metadata: metadata)) }
    }

    public func error(_ message: String, metadata: [String: String]) {
        entries.withLock { $0.append(Entry(level: "error", message: message, metadata: metadata)) }
    }
}
