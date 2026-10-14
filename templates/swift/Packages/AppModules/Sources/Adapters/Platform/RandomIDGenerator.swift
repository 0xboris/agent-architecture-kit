import Domain
import Foundation

public struct RandomIDGenerator: IDGenerator {
    public init() {}

    public func makeID() -> UUID {
        UUID()
    }
}
