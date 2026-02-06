import Foundation

struct User: Codable, Identifiable {
    let id: String
    let name: String
    let email: String
    let role: UserRole?
    let avatarUrl: String?
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case email
        case role
        case avatarUrl = "avatar_url"
        case createdAt = "created_at"
    }

    var initials: String {
        let components = name.split(separator: " ")
        let first = components.first?.prefix(1) ?? ""
        let last = components.count > 1 ? components.last?.prefix(1) ?? "" : ""
        return "\(first)\(last)".uppercased()
    }
}

enum UserRole: String, Codable {
    case admin
    case operator_
    case viewer

    enum CodingKeys: String, CodingKey {
        case admin
        case operator_ = "operator"
        case viewer
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let value = try container.decode(String.self)
        switch value {
        case "admin": self = .admin
        case "operator": self = .operator_
        case "viewer": self = .viewer
        default: self = .viewer
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .admin: try container.encode("admin")
        case .operator_: try container.encode("operator")
        case .viewer: try container.encode("viewer")
        }
    }

    var displayName: String {
        switch self {
        case .admin: return "Administrador"
        case .operator_: return "Operador"
        case .viewer: return "Visualizador"
        }
    }
}

struct LoginRequest: Codable {
    let login: String
    let password: String
}

struct LoginResponse: Codable {
    let token: String
    let user: User
    let expiresAt: String?

    enum CodingKeys: String, CodingKey {
        case token
        case user
        case expiresAt = "expires_at"
    }
}
