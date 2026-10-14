import Domain
import Foundation
import os

/// A time source that tests control. It starts at a fixed date and moves only
/// when a test calls `advance(by:)`.
public final class FakeTimeSource: TimeSource {
    private let current: OSAllocatedUnfairLock<Date>

    public init(now: Date = Date(timeIntervalSince1970: 1_700_000_000)) {
        current = OSAllocatedUnfairLock(initialState: now)
    }

    public func now() -> Date {
        current.withLock { $0 }
    }

    public func advance(by seconds: TimeInterval) {
        current.withLock { $0 += seconds }
    }
}
