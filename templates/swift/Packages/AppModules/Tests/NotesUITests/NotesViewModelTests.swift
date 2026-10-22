import Domain
import Foundation
import NotesUI
import NotesUseCases
import Persistence
import Testing
import TestSupport

@MainActor
struct NotesViewModelTests {
    let store = FileNoteStore(fileURL: FileManager.default.temporaryDirectory
        .appending(path: UUID().uuidString).appending(path: "notes.json"))

    func makeViewModel(store: any NoteStore) -> NotesViewModel {
        NotesViewModel(
            createNote: CreateNote(store: store, time: FakeTimeSource(), ids: SequentialIDGenerator()),
            listNotes: ListNotes(store: store)
        )
    }

    @Test func addingANoteStoresItReloadsAndClearsTheDraft() async throws {
        let viewModel = makeViewModel(store: store)
        viewModel.draftTitle = "Groceries"

        await viewModel.add()

        let stored = try await store.allNotes()
        #expect(stored.map(\.title.value) == ["Groceries"])
        #expect(viewModel.state == .loaded(stored))
        #expect(viewModel.draftTitle.isEmpty)
    }

    @Test func emptyTitleShowsAMessageAndStoresNothing() async throws {
        let viewModel = makeViewModel(store: store)
        viewModel.draftTitle = "  "

        await viewModel.add()

        #expect(viewModel.draftError == "Enter a title.")
        #expect(try await store.allNotes().isEmpty)
    }

    @Test func failedLoadShowsTheFailedState() async {
        struct Offline: Error {}
        let viewModel = makeViewModel(store: FailingNoteStore(failure: Offline()))

        await viewModel.load()

        #expect(viewModel.state == .failed)
    }
}
