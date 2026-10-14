import Foundation

public protocol IDGenerator: Sendable {
    func makeID() -> UUID
}
