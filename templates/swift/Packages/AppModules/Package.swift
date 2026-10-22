// swift-tools-version: 6.0
import PackageDescription

// Declare every target that a file imports, so that
// `swift build --explicit-target-dependency-import-check=error` passes.
let package = Package(
    name: "AppModules",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "AppComposition", targets: ["AppComposition"]),
    ],
    targets: [
        .target(name: "Utilities", path: "Sources/Utilities"),

        .target(name: "Domain", dependencies: ["Utilities"], path: "Sources/Domain"),
        .testTarget(name: "DomainTests", dependencies: ["Domain", "Utilities", "Persistence", "TestSupport"], path: "Tests/DomainTests"),

        .target(name: "DesignSystem", dependencies: ["Utilities"], path: "Sources/DesignSystem"),

        .target(name: "Persistence", dependencies: ["Domain", "Utilities"], path: "Sources/Adapters/Persistence"),
        .testTarget(name: "PersistenceTests", dependencies: ["Persistence", "Domain", "TestSupport"], path: "Tests/PersistenceTests"),
        .target(name: "Platform", dependencies: ["Domain", "Utilities"], path: "Sources/Adapters/Platform"),

        .target(name: "NotesUseCases", dependencies: ["Domain", "Utilities"], path: "Sources/Features/Notes/UseCases"),
        .target(name: "NotesUI", dependencies: ["NotesUseCases", "Domain", "DesignSystem", "Utilities"], path: "Sources/Features/Notes/UI"),
        .testTarget(name: "NotesUseCasesTests", dependencies: ["NotesUseCases", "Domain", "Persistence", "TestSupport"], path: "Tests/NotesUseCasesTests"),
        .testTarget(name: "NotesUITests", dependencies: ["NotesUI", "NotesUseCases", "Domain", "Persistence", "TestSupport"], path: "Tests/NotesUITests"),

        .target(name: "TestSupport", dependencies: ["Domain", "Utilities"], path: "Sources/TestSupport"),

        .target(
            name: "AppComposition",
            dependencies: [
                "Domain", "Utilities", "DesignSystem", "Persistence", "Platform",
                "NotesUI", "NotesUseCases",
            ],
            path: "Sources/AppComposition"
        ),
        .testTarget(
            name: "AppCompositionTests",
            dependencies: ["AppComposition", "Domain", "Persistence", "TestSupport", "NotesUI"],
            path: "Tests/AppCompositionTests"
        ),
    ]
)
