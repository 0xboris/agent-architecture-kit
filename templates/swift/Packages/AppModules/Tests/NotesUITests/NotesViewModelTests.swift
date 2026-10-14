import Domain
import NotesUI
import NotesUseCases
import Testing
import TestSupport

@MainActor
struct NotesViewModelTests {
    let store = FakeNoteStore()

    func makeViewModel() -> NotesViewModel {
        NotesViewModel(
            createNote: CreateNote(store: store, time: FakeTimeSource(), ids: SequentialIDGenerator()),
            listNotes: ListNotes(store: store)
        )
    }

    @Test func addingANoteShowsItAndClearsTheDraft() async throws {
        let viewModel = makeViewModel()
        viewModel.draftTitle = "Groceries"

        await viewModel.add()

        let stored = try await store.allNotes()
        #expect(viewModel.state == .loaded(stored))
        #expect(stored.map(\.title.value) == ["Groceries"])
        #expect(viewModel.draftTitle.isEmpty)
    }

    @Test func emptyTitleShowsAMessageAndStoresNothing() async throws {
        let viewModel = makeViewModel()
        viewModel.draftTitle = "  "

        await viewModel.add()

        #expect(viewModel.draftError == "Enter a title.")
        #expect(try await store.allNotes().isEmpty)
    }

    @Test func failedLoadShowsTheFailedState() async {
        struct Offline: Error {}
        await store.failNextCall(with: Offline())
        let viewModel = makeViewModel()

        await viewModel.load()

        #expect(viewModel.state == .failed)
    }
}
