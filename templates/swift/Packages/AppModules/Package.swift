// swift-tools-version: 6.0
import PackageDescription

// Every module of the app lives in this package. The Xcode app target only holds
// the @main file and links the AppComposition product.
//
// `python3 tools/new.py slice <Name>` adds targets at the `scaffold:` markers.
// tools/archcheck.py enforces the import rules; this manifest only declares
// build dependencies. Declare every target that a file imports, so that
// `swift build --explicit-target-dependency-import-check=error` passes.
let package = Package(
    name: "AppModules",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "AppComposition", targets: ["AppComposition"]),
    ],
    targets: [
        // Utilities: helpers with no business meaning.
        .target(name: "Utilities", path: "Sources/Utilities"),

        // Domain: model, rules, ports, and middleware.
        .target(name: "Domain", dependencies: ["Utilities"], path: "Sources/Domain"),
        .testTarget(name: "DomainTests", dependencies: ["Domain", "Utilities", "TestSupport"], path: "Tests/DomainTests"),

        // Shared UI.
        .target(name: "DesignSystem", dependencies: ["Utilities"], path: "Sources/DesignSystem"),

        // Adapters.
        .target(name: "Persistence", dependencies: ["Domain", "Utilities"], path: "Sources/Adapters/Persistence"),
        .testTarget(name: "PersistenceTests", dependencies: ["Persistence", "Domain", "TestSupport"], path: "Tests/PersistenceTests"),
        .target(name: "Platform", dependencies: ["Domain", "Utilities"], path: "Sources/Adapters/Platform"),

        // Feature slices: one UI target and one use case target each.
        .target(name: "NotesUseCases", dependencies: ["Domain", "Utilities"], path: "Sources/Features/Notes/UseCases"),
        .target(name: "NotesUI", dependencies: ["NotesUseCases", "Domain", "DesignSystem", "Utilities"], path: "Sources/Features/Notes/UI"),
        .testTarget(name: "NotesUseCasesTests", dependencies: ["NotesUseCases", "Domain", "TestSupport"], path: "Tests/NotesUseCasesTests"),
        .testTarget(name: "NotesUITests", dependencies: ["NotesUI", "NotesUseCases", "Domain", "TestSupport"], path: "Tests/NotesUITests"),
        // scaffold:slices

        // Test support: shared fakes and contract suites. Only test targets depend on it.
        .target(name: "TestSupport", dependencies: ["Domain", "Utilities"], path: "Sources/TestSupport"),
        .testTarget(name: "TestSupportTests", dependencies: ["TestSupport", "Domain"], path: "Tests/TestSupportTests"),

        // Composition root.
        .target(
            name: "AppComposition",
            dependencies: [
                "Domain", "Utilities", "DesignSystem", "Persistence", "Platform",
                "NotesUI", "NotesUseCases",
                // scaffold:composition
            ],
            path: "Sources/AppComposition"
        ),
        .testTarget(
            name: "AppCompositionTests",
            dependencies: ["AppComposition", "Domain", "TestSupport", "NotesUI"],
            path: "Tests/AppCompositionTests"
        ),
    ]
)
