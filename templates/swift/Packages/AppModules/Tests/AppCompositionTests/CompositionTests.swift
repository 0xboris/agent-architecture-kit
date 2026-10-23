import AppComposition
import Foundation
import Persistence
import Testing
import TestSupport

@MainActor
@Test func notesSliceStoresThroughTheLoggingMiddleware() async throws {
    let directory = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: directory) }
    let store = FileNoteStore(fileURL: directory.appending(path: "notes.json"))
    let logger = RecordingLogger()
    let container = AppContainer(dependencies: AppDependencies(
        noteStore: store, time: FakeTimeSource(), ids: SequentialIDGenerator(), logger: logger))
    let viewModel = container.makeNotesViewModel()
    viewModel.draftTitle = "Groceries"

    await viewModel.add()

    #expect(try await store.allNotes().count == 1)
    #expect(logger.recorded.map(\.message) == ["note saved"])
}
