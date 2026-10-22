public protocol AppLogger: Sendable {
    func info(_ message: String, metadata: [String: String])
    func error(_ message: String, metadata: [String: String])
}
