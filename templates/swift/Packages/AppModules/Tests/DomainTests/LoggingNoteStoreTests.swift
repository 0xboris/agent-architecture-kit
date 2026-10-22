import Domain
import Foundation
import Persistence
import Testing
import TestSupport

@Test func noteSavedThroughTheMiddlewareIsStoredAndLogged() async throws {
    let store = FileNoteStore(fileURL: FileManager.default.temporaryDirectory
        .appending(path: UUID().uuidString).appending(path: "notes.json"))
    let logger = RecordingLogger()
    let note = try Samples.note(1)

    try await LoggingNoteStore(store, logger: logger).save(note)

    #expect(try await store.allNotes() == [note])
    #expect(logger.recorded.map(\.message) == ["note saved"])
}

@Test func failedSaveIsNotLogged() async throws {
    struct Offline: Error {}
    let logger = RecordingLogger()

    await #expect(throws: Offline.self) {
        try await LoggingNoteStore(FailingNoteStore(failure: Offline()), logger: logger).save(try Samples.note(1))
    }
    #expect(logger.recorded.isEmpty)
}
