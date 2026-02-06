import SwiftUI

// MARK: - Color Extensions

extension Color {
    // Court colors
    static let courtGreen = Color(hex: "#2E7D32")
    static let courtGreenLight = Color(hex: "#4CAF50")
    static let courtGreenDark = Color(hex: "#1B5E20")

    // Ball colors
    static let ballYellow = Color(hex: "#F57F17")
    static let ballYellowLight = Color(hex: "#FFB300")

    // Background colors
    static let backgroundPrimary = Color(hex: "#121212")
    static let backgroundSecondary = Color(hex: "#1E1E1E")
    static let backgroundTertiary = Color(hex: "#2C2C2C")
    static let backgroundCard = Color(hex: "#252525")

    // Surface colors
    static let surfaceClay = Color(hex: "#BF360C")
    static let surfaceHard = Color(hex: "#1565C0")
    static let surfaceGrass = Color(hex: "#2E7D32")
    static let surfaceIndoor = Color(hex: "#37474F")

    // Status colors
    static let statusLive = Color(hex: "#D32F2F")
    static let statusConnected = Color(hex: "#2E7D32")
    static let statusConnecting = Color(hex: "#F57F17")
    static let statusDisconnected = Color(hex: "#757575")
    static let statusError = Color(hex: "#D32F2F")

    // Text colors
    static let textPrimary = Color.white
    static let textSecondary = Color(hex: "#B0B0B0")
    static let textMuted = Color(hex: "#757575")

    // Accent
    static let accentGreen = Color(hex: "#66BB6A")

    // Hex initializer
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Font Extensions

extension Font {
    static let titleLarge = Font.system(size: 28, weight: .bold)
    static let titleMedium = Font.system(size: 22, weight: .semibold)
    static let titleSmall = Font.system(size: 18, weight: .semibold)

    static let bodyLarge = Font.system(size: 17, weight: .regular)
    static let bodyMedium = Font.system(size: 15, weight: .regular)
    static let bodySmall = Font.system(size: 13, weight: .regular)

    static let labelLarge = Font.system(size: 15, weight: .medium)
    static let labelMedium = Font.system(size: 13, weight: .medium)
    static let labelSmall = Font.system(size: 11, weight: .medium)

    static let monoMedium = Font.system(size: 15, weight: .medium, design: .monospaced)
    static let monoSmall = Font.system(size: 13, weight: .medium, design: .monospaced)
}

// MARK: - View Modifiers

struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(Color.backgroundCard)
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.3), radius: 4, x: 0, y: 2)
    }
}

struct PrimaryButtonModifier: ViewModifier {
    let isEnabled: Bool

    func body(content: Content) -> some View {
        content
            .font(.labelLarge)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(isEnabled ? Color.courtGreen : Color.textMuted)
            .cornerRadius(12)
    }
}

struct StreamControlButtonModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.system(size: 20))
            .foregroundColor(.white)
            .frame(width: 44, height: 44)
            .background(Color.black.opacity(0.5))
            .clipShape(Circle())
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }

    func primaryButtonStyle(isEnabled: Bool = true) -> some View {
        modifier(PrimaryButtonModifier(isEnabled: isEnabled))
    }

    func streamControlButton() -> some View {
        modifier(StreamControlButtonModifier())
    }
}
