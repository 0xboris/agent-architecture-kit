import Domain
import Foundation

public struct SystemTimeSource: TimeSource {
    public init() {}

    public func now() -> Date {
        Date()
    }
}
