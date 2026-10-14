import Domain
import Testing
import TestSupport

@Test func savingThroughTheMiddlewareLogsAndStores() async throws {
    let store = FakeNoteStore()
    let logger = RecordingLogger()
    let note = try Samples.note(1)

    try await LoggingNoteStore(store, logger: logger).save(note)

    #expect(try await store.allNotes() == [note])
    #expect(logger.recorded.map(\.message) == ["note saved"])
}

@Test func failedSaveIsNotLogged() async throws {
    struct Offline: Error {}
    let store = FakeNoteStore()
    await store.failNextCall(with: Offline())
    let logger = RecordingLogger()

    await #expect(throws: Offline.self) {
        try await LoggingNoteStore(store, logger: logger).save(try Samples.note(1))
    }
    #expect(logger.recorded.isEmpty)
}
