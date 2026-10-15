import Domain
import Testing
import TestSupport

@Test func savingThroughTheMiddlewareSavesAndLogs() async throws {
    let store = StubNoteStore()
    let logger = RecordingLogger()
    let note = try Samples.note(1)

    try await LoggingNoteStore(store, logger: logger).save(note)

    #expect(await store.saved == [note])
    #expect(logger.recorded.map(\.message) == ["note saved"])
}

@Test func failedSaveIsNotLogged() async throws {
    struct Offline: Error {}
    let store = StubNoteStore(failure: Offline())
    let logger = RecordingLogger()

    await #expect(throws: Offline.self) {
        try await LoggingNoteStore(store, logger: logger).save(try Samples.note(1))
    }
    #expect(logger.recorded.isEmpty)
}
