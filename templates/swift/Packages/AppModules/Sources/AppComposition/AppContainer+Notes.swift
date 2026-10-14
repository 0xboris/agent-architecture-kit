import NotesUI
import NotesUseCases

extension AppContainer {
    public func makeNotesViewModel() -> NotesViewModel {
        NotesViewModel(
            createNote: CreateNote(store: noteStore, time: dependencies.time, ids: dependencies.ids),
            listNotes: ListNotes(store: noteStore)
        )
    }
}
