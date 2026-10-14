/// The logging interface. The Platform adapter implements it, and tests use
/// `RecordingLogger` from TestSupport.
public protocol AppLogger: Sendable {
    func info(_ message: String, metadata: [String: String])
    func error(_ message: String, metadata: [String: String])
}
