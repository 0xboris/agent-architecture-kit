import Foundation

/// The current time. Named `TimeSource` because `Clock` is a standard library protocol.
public protocol TimeSource: Sendable {
    func now() -> Date
}
