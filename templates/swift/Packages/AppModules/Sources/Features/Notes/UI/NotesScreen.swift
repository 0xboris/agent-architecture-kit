import DesignSystem
import SwiftUI

public struct NotesScreen: View {
    @State private var viewModel: NotesViewModel

    public init(viewModel: NotesViewModel) {
        _viewModel = State(initialValue: viewModel)
    }

    public var body: some View {
        NavigationStack {
            List {
                Section {
                    TextField("New note", text: $viewModel.draftTitle)
                    if let error = viewModel.draftError {
                        Text(error).foregroundStyle(.red)
                    }
                    PrimaryButton("Add") {
                        Task { await viewModel.add() }
                    }
                }
                Section {
                    switch viewModel.state {
                    case .loading:
                        ProgressView()
                    case .loaded(let notes):
                        ForEach(notes) { note in
                            Text(note.title.value)
                        }
                    case .failed:
                        Text("The notes could not be loaded.")
                    }
                }
            }
            .navigationTitle("Notes")
            .task { await viewModel.load() }
        }
    }
}
