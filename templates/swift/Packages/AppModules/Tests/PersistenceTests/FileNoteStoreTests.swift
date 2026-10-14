import Domain
import Foundation
import Persistence
import Testing
import TestSupport

@Test func fileNoteStoreMeetsTheContract() async throws {
    let directory = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString)
    defer { try? FileManager.default.removeItem(at: directory) }

    try await NoteStoreContract.verify {
        FileNoteStore(fileURL: directory.appending(path: "\(UUID().uuidString).json"))
    }
}
