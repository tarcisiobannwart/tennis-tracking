import Foundation
import Combine

final class AppState: ObservableObject {
    @Published var isLoggedIn: Bool = false
    @Published var authToken: String? = nil
    @Published var currentUser: User? = nil
    @Published var selectedMatch: Match? = nil
    @Published var serverURL: String {
        didSet {
            UserDefaults.standard.set(serverURL, forKey: Keys.serverURL)
            APIService.shared.baseURL = serverURL
        }
    }
    @Published var defaultResolution: VideoResolution = .hd720 {
        didSet {
            UserDefaults.standard.set(defaultResolution.rawValue, forKey: Keys.defaultResolution)
        }
    }
    @Published var audioEnabled: Bool = true {
        didSet {
            UserDefaults.standard.set(audioEnabled, forKey: Keys.audioEnabled)
        }
    }

    private enum Keys {
        static let serverURL = "tt_server_url"
        static let defaultResolution = "tt_default_resolution"
        static let audioEnabled = "tt_audio_enabled"
    }

    init() {
        self.serverURL = UserDefaults.standard.string(forKey: Keys.serverURL)
            ?? "https://api.tennistrack.local"
        self.audioEnabled = UserDefaults.standard.object(forKey: Keys.audioEnabled) as? Bool ?? true

        if let resolutionRaw = UserDefaults.standard.string(forKey: Keys.defaultResolution),
           let resolution = VideoResolution(rawValue: resolutionRaw) {
            self.defaultResolution = resolution
        }
    }

    func restoreSession() {
        let authService = AuthService.shared
        if authService.isLoggedIn, let token = authService.getToken() {
            self.authToken = token
            self.isLoggedIn = true
            APIService.shared.authToken = token
        }
    }

    func login(token: String, user: User) {
        AuthService.shared.saveToken(token)
        self.authToken = token
        self.currentUser = user
        self.isLoggedIn = true
        APIService.shared.authToken = token
    }

    func logout() {
        AuthService.shared.removeToken()
        self.authToken = nil
        self.currentUser = nil
        self.selectedMatch = nil
        self.isLoggedIn = false
        APIService.shared.authToken = nil
    }
}

enum VideoResolution: String, CaseIterable, Identifiable {
    case sd480 = "480p"
    case hd720 = "720p"
    case fullHD1080 = "1080p"

    var id: String { rawValue }

    var width: Int {
        switch self {
        case .sd480: return 854
        case .hd720: return 1280
        case .fullHD1080: return 1920
        }
    }

    var height: Int {
        switch self {
        case .sd480: return 480
        case .hd720: return 720
        case .fullHD1080: return 1080
        }
    }

    var bitrate: Int {
        switch self {
        case .sd480: return 1_500_000
        case .hd720: return 3_000_000
        case .fullHD1080: return 6_000_000
        }
    }

    var displayName: String {
        switch self {
        case .sd480: return "480p (SD)"
        case .hd720: return "720p (HD)"
        case .fullHD1080: return "1080p (Full HD)"
        }
    }
}
