import Foundation
import Persistence
import Platform

extension AppDependencies {
    public static func live() -> AppDependencies {
        AppDependencies(
            noteStore: FileNoteStore(fileURL: .applicationSupportDirectory.appending(path: "notes.json")),
            time: SystemTimeSource(),
            ids: RandomIDGenerator(),
            logger: OSAppLogger(subsystem: "app", category: "app")
        )
    }
}
