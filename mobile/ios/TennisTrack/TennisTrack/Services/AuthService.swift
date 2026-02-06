import Foundation
import Security

final class AuthService {
    static let shared = AuthService()

    private let keychainAccount = "com.tennistrack.auth-token"
    private let keychainService = "TennisTrack"

    private init() {}

    var isLoggedIn: Bool {
        getToken() != nil
    }

    // MARK: - Token Management

    func saveToken(_ token: String) {
        deleteFromKeychain()

        guard let data = token.data(using: .utf8) else { return }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: keychainAccount,
            kSecAttrService as String: keychainService,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status != errSecSuccess {
            // Fallback para UserDefaults se Keychain falhar
            UserDefaults.standard.set(token, forKey: keychainAccount)
        }
    }

    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: keychainAccount,
            kSecAttrService as String: keychainService,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        if status == errSecSuccess, let data = result as? Data {
            return String(data: data, encoding: .utf8)
        }

        // Fallback para UserDefaults
        return UserDefaults.standard.string(forKey: keychainAccount)
    }

    func removeToken() {
        deleteFromKeychain()
        UserDefaults.standard.removeObject(forKey: keychainAccount)
    }

    // MARK: - Auth Actions

    func login(login: String, password: String) async throws -> LoginResponse {
        let response = try await APIService.shared.login(login: login, password: password)
        saveToken(response.token)
        return response
    }

    func logout() {
        removeToken()
        APIService.shared.authToken = nil
    }

    // MARK: - Private

    private func deleteFromKeychain() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: keychainAccount,
            kSecAttrService as String: keychainService
        ]

        SecItemDelete(query as CFDictionary)
    }
}
