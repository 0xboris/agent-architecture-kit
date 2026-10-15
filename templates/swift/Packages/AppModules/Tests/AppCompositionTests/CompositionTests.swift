import AppComposition
import Testing
import TestSupport

/// Composition tests check the wiring in AppContainer: which middleware each
/// slice receives. Unit tests of a slice build their use cases directly and
/// never see the wiring.
@MainActor
@Test func notesSliceStoresThroughTheLoggingMiddleware() async throws {
    let store = StubNoteStore()
    let logger = RecordingLogger()
    let container = AppContainer(dependencies: AppDependencies(
        noteStore: store, time: FakeTimeSource(), ids: SequentialIDGenerator(), logger: logger))
    let viewModel = container.makeNotesViewModel()
    viewModel.draftTitle = "Groceries"

    await viewModel.add()

    #expect(await store.saved.count == 1)
    #expect(logger.recorded.map(\.message) == ["note saved"])
}
