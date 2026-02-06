import Foundation

struct Match: Codable, Identifiable {
    let id: String
    let player1: String
    let player2: String
    let score: String?
    let status: MatchStatus
    let surface: Surface
    let date: String
    let tournament: String?
    let round: String?

    var displayDate: String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

        guard let parsedDate = formatter.date(from: date)
                ?? ISO8601DateFormatter().date(from: date) else {
            return date
        }

        let displayFormatter = DateFormatter()
        displayFormatter.locale = Locale(identifier: "pt_BR")
        displayFormatter.dateStyle = .medium
        displayFormatter.timeStyle = .short
        return displayFormatter.string(from: parsedDate)
    }

    var matchTitle: String {
        "\(player1) vs \(player2)"
    }
}

enum MatchStatus: String, Codable {
    case scheduled
    case live
    case completed
    case cancelled

    var displayName: String {
        switch self {
        case .scheduled: return "Agendada"
        case .live: return "Ao Vivo"
        case .completed: return "Finalizada"
        case .cancelled: return "Cancelada"
        }
    }

    var iconName: String {
        switch self {
        case .scheduled: return "clock"
        case .live: return "record.circle"
        case .completed: return "checkmark.circle"
        case .cancelled: return "xmark.circle"
        }
    }
}

enum Surface: String, Codable {
    case hard
    case clay
    case grass
    case indoor

    var displayName: String {
        switch self {
        case .hard: return "Dura"
        case .clay: return "Saibro"
        case .grass: return "Grama"
        case .indoor: return "Indoor"
        }
    }

    var iconName: String {
        switch self {
        case .hard: return "square.fill"
        case .clay: return "circle.fill"
        case .grass: return "leaf.fill"
        case .indoor: return "building.2.fill"
        }
    }

    var color: String {
        switch self {
        case .hard: return "#1565C0"
        case .clay: return "#BF360C"
        case .grass: return "#2E7D32"
        case .indoor: return "#37474F"
        }
    }
}

struct MatchListResponse: Codable {
    let matches: [Match]
    let total: Int?
}
