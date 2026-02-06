import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int, message: String?)
    case decodingError(Error)
    case networkError(Error)
    case unauthorized
    case serverError(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "URL invalida."
        case .invalidResponse:
            return "Resposta invalida do servidor."
        case .httpError(let code, let message):
            return message ?? "Erro HTTP \(code)."
        case .decodingError(let error):
            return "Erro ao processar resposta: \(error.localizedDescription)"
        case .networkError(let error):
            return "Erro de rede: \(error.localizedDescription)"
        case .unauthorized:
            return "Sessao expirada. Faca login novamente."
        case .serverError(let message):
            return message
        }
    }
}

final class APIService {
    static let shared = APIService()

    var baseURL: String {
        didSet {
            let trimmed = baseURL.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed != baseURL {
                baseURL = trimmed
            }
        }
    }

    var authToken: String?

    private let session: URLSession
    private let decoder: JSONDecoder

    private init() {
        self.baseURL = UserDefaults.standard.string(forKey: "tt_server_url")
            ?? "https://api.tennistrack.local"
        self.authToken = nil

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)

        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
    }

    // MARK: - Auth

    func login(login: String, password: String) async throws -> LoginResponse {
        let body = LoginRequest(login: login, password: password)
        let response: LoginResponse = try await post(path: "/api/auth/login", body: body)
        self.authToken = response.token
        return response
    }

    // MARK: - Streams

    func createStream(matchId: String, cameraLabel: String, resolution: VideoResolution) async throws -> StreamResponse {
        let deviceInfo = DeviceInfo.current(resolution: resolution)
        let body = CreateStreamRequest(
            matchId: matchId,
            cameraLabel: cameraLabel,
            deviceInfo: deviceInfo
        )
        return try await post(path: "/api/streams", body: body)
    }

    func listStreams(matchId: String? = nil) async throws -> [StreamResponse] {
        var path = "/api/streams"
        if let matchId = matchId {
            path += "?match_id=\(matchId)"
        }
        let response: StreamListResponse = try await get(path: path)
        return response.streams
    }

    func getStream(id: String) async throws -> StreamResponse {
        return try await get(path: "/api/streams/\(id)")
    }

    func endStream(id: String) async throws -> StreamResponse {
        return try await put(path: "/api/streams/\(id)/end", body: EndStreamRequest(streamId: id))
    }

    // MARK: - Matches

    func getMatches(status: MatchStatus? = nil) async throws -> [Match] {
        var path = "/api/matches"
        if let status = status {
            path += "?status=\(status.rawValue)"
        }
        let response: MatchListResponse = try await get(path: path)
        return response.matches
    }

    func getMatch(id: String) async throws -> Match {
        return try await get(path: "/api/matches/\(id)")
    }

    // MARK: - HTTP Methods

    private func get<T: Decodable>(path: String) async throws -> T {
        let request = try buildRequest(method: "GET", path: path)
        return try await execute(request)
    }

    private func post<T: Decodable, B: Encodable>(path: String, body: B) async throws -> T {
        var request = try buildRequest(method: "POST", path: path)
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        request.httpBody = try encoder.encode(body)
        return try await execute(request)
    }

    private func put<T: Decodable, B: Encodable>(path: String, body: B) async throws -> T {
        var request = try buildRequest(method: "PUT", path: path)
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        request.httpBody = try encoder.encode(body)
        return try await execute(request)
    }

    private func delete(path: String) async throws {
        let request = try buildRequest(method: "DELETE", path: path)
        let (_, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            if httpResponse.statusCode == 401 {
                throw APIError.unauthorized
            }
            throw APIError.httpError(statusCode: httpResponse.statusCode, message: nil)
        }
    }

    // MARK: - Request Building

    private func buildRequest(method: String, path: String) throws -> URLRequest {
        let urlString = baseURL.hasSuffix("/")
            ? "\(baseURL.dropLast())\(path)"
            : "\(baseURL)\(path)"

        guard let url = URL(string: urlString) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("TennisTrack-iOS/1.0", forHTTPHeaderField: "User-Agent")

        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        return request
    }

    // MARK: - Execution

    private func execute<T: Decodable>(_ request: URLRequest) async throws -> T {
        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError.networkError(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            if httpResponse.statusCode == 401 {
                throw APIError.unauthorized
            }

            let errorMessage = try? JSONDecoder().decode(APIErrorResponse.self, from: data)
            throw APIError.httpError(
                statusCode: httpResponse.statusCode,
                message: errorMessage?.message ?? errorMessage?.error
            )
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }
}

private struct APIErrorResponse: Codable {
    let error: String?
    let message: String?
}
