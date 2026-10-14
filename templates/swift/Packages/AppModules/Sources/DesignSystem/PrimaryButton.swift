import SwiftUI

/// The app's main call-to-action button. Shared UI holds no business types.
public struct PrimaryButton: View {
    private let title: String
    private let action: () -> Void

    public init(_ title: String, action: @escaping () -> Void) {
        self.title = title
        self.action = action
    }

    public var body: some View {
        Button(title, action: action)
            .buttonStyle(.borderedProminent)
    }
}
