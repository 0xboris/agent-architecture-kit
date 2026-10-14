import Domain
import Foundation
import os

/// Returns predictable ids: 00000000-0000-0000-0000-000000000001, then ...002, and so on.
public final class SequentialIDGenerator: IDGenerator {
    private let counter = OSAllocatedUnfairLock(initialState: 0)

    public init() {}

    public func makeID() -> UUID {
        Self.id(counter.withLock { value in
            value += 1
            return value
        })
    }

    public static func id(_ number: Int) -> UUID {
        let n = UInt64(number)
        return UUID(uuid: (
            0, 0, 0, 0, 0, 0, 0, 0,
            UInt8(truncatingIfNeeded: n >> 56), UInt8(truncatingIfNeeded: n >> 48),
            UInt8(truncatingIfNeeded: n >> 40), UInt8(truncatingIfNeeded: n >> 32),
            UInt8(truncatingIfNeeded: n >> 24), UInt8(truncatingIfNeeded: n >> 16),
            UInt8(truncatingIfNeeded: n >> 8), UInt8(truncatingIfNeeded: n)
        ))
    }
}
