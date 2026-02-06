// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "TennisTrack",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .library(
            name: "TennisTrack",
            targets: ["TennisTrack"]
        )
    ],
    dependencies: [
        .package(
            url: "https://github.com/shogo4405/HaishinKit.swift",
            from: "1.9.0"
        )
    ],
    targets: [
        .target(
            name: "TennisTrack",
            dependencies: [
                .product(name: "HaishinKit", package: "HaishinKit.swift")
            ],
            path: "TennisTrack"
        )
    ]
)
