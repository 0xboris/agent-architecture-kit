import NotesUI
import SwiftUI

public struct RootView: View {
    @State private var notes: NotesViewModel

    public init(container: AppContainer) {
        _notes = State(initialValue: container.makeNotesViewModel())
    }

    public var body: some View {
        NotesScreen(viewModel: notes)
    }
}
