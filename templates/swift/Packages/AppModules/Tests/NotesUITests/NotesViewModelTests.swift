import Domain
import NotesUI
import NotesUseCases
import Testing
import TestSupport

@MainActor
struct NotesViewModelTests {
    func makeViewModel(store: StubNoteStore) -> NotesViewModel {
        NotesViewModel(
            createNote: CreateNote(store: store, time: FakeTimeSource(), ids: SequentialIDGenerator()),
            listNotes: ListNotes(store: store)
        )
    }

    @Test func addingANoteSavesItReloadsAndClearsTheDraft() async throws {
        let listed = [try Samples.note(1)]
        let store = StubNoteStore(notes: listed)
        let viewModel = makeViewModel(store: store)
        viewModel.draftTitle = "Groceries"

        await viewModel.add()

        #expect(await store.saved.map(\.title.value) == ["Groceries"])
        #expect(viewModel.state == .loaded(listed))
        #expect(viewModel.draftTitle.isEmpty)
    }

    @Test func emptyTitleShowsAMessageAndSavesNothing() async throws {
        let store = StubNoteStore()
        let viewModel = makeViewModel(store: store)
        viewModel.draftTitle = "  "

        await viewModel.add()

        #expect(viewModel.draftError == "Enter a title.")
        #expect(await store.saved.isEmpty)
    }

    @Test func failedLoadShowsTheFailedState() async {
        struct Offline: Error {}
        let viewModel = makeViewModel(store: StubNoteStore(failure: Offline()))

        await viewModel.load()

        #expect(viewModel.state == .failed)
    }
}
