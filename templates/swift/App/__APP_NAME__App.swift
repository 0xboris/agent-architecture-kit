import AppComposition
import SwiftUI

@main
struct __APP_NAME__App: App {
    private let container = AppContainer(dependencies: .live())

    var body: some Scene {
        WindowGroup {
            RootView(container: container)
        }
    }
}
