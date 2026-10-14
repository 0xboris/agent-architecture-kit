import os
import Utilities

public struct OSAppLogger: AppLogger {
    private let logger: os.Logger

    public init(subsystem: String, category: String) {
        logger = os.Logger(subsystem: subsystem, category: category)
    }

    public func info(_ message: String, metadata: [String: String]) {
        logger.info("\(message, privacy: .public) \(Self.format(metadata), privacy: .private)")
    }

    public func error(_ message: String, metadata: [String: String]) {
        logger.error("\(message, privacy: .public) \(Self.format(metadata), privacy: .private)")
    }

    private static func format(_ metadata: [String: String]) -> String {
        metadata.sorted { $0.key < $1.key }.map { "\($0.key)=\($0.value)" }.joined(separator: " ")
    }
}
