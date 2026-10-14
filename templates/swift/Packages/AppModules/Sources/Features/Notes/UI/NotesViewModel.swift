import Domain
import NotesUseCases
import Observation

@MainActor
@Observable
public final class NotesViewModel {
    public enum State: Equatable {
        case loading
        case loaded([Note])
        case failed
    }

    public private(set) var state: State = .loading
    public var draftTitle = ""
    public private(set) var draftError: String?

    private let createNote: CreateNote
    private let listNotes: ListNotes

    public init(createNote: CreateNote, listNotes: ListNotes) {
        self.createNote = createNote
        self.listNotes = listNotes
    }

    public func load() async {
        do {
            state = .loaded(try await listNotes())
        } catch {
            state = .failed
        }
    }

    public func add() async {
        do {
            _ = try await createNote(title: draftTitle)
            draftTitle = ""
            draftError = nil
            await load()
        } catch let invalid as NoteTitle.Invalid {
            draftError = Self.message(for: invalid)
        } catch {
            draftError = "The note could not be saved."
        }
    }

    static func message(for invalid: NoteTitle.Invalid) -> String {
        switch invalid {
        case .empty: "Enter a title."
        case .tooLong(let limit): "Use at most \(limit) characters."
        }
    }
}
