import SwiftUI

struct LoginView: View {
    @EnvironmentObject var appState: AppState

    @State private var login: String = ""
    @State private var password: String = ""
    @State private var isLoading: Bool = false
    @State private var showError: Bool = false
    @State private var errorMessage: String = ""
    @FocusState private var focusedField: LoginField?

    private enum LoginField {
        case login, password
    }

    var body: some View {
        GeometryReader { geometry in
            ScrollView {
                VStack(spacing: 0) {
                    Spacer()
                        .frame(minHeight: geometry.size.height * 0.08)

                    // Logo e titulo
                    logoSection

                    Spacer()
                        .frame(height: 48)

                    // Formulario
                    formSection

                    Spacer()
                        .frame(height: 32)

                    // Botao de login
                    loginButton

                    Spacer()
                        .frame(minHeight: geometry.size.height * 0.1)

                    // Versao do app
                    versionLabel
                }
                .padding(.horizontal, 32)
                .frame(minHeight: geometry.size.height)
            }
        }
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .onTapGesture {
            focusedField = nil
        }
        .alert("Erro de Login", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }

    // MARK: - Logo Section

    private var logoSection: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(Color.courtGreen.opacity(0.15))
                    .frame(width: 100, height: 100)

                Image(systemName: "tennisball.fill")
                    .font(.system(size: 44))
                    .foregroundColor(.ballYellow)
            }

            Text("TennisTrack")
                .font(.titleLarge)
                .foregroundColor(.textPrimary)

            Text("Streaming de partidas ao vivo")
                .font(.bodyMedium)
                .foregroundColor(.textSecondary)
        }
    }

    // MARK: - Form Section

    private var formSection: some View {
        VStack(spacing: 16) {
            // Campo de login (email ou CPF)
            VStack(alignment: .leading, spacing: 8) {
                Text("Email ou CPF")
                    .font(.labelMedium)
                    .foregroundColor(.textSecondary)

                HStack(spacing: 12) {
                    Image(systemName: "person.fill")
                        .foregroundColor(.textMuted)
                        .frame(width: 20)

                    TextField("", text: $login)
                        .textContentType(.username)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        .keyboardType(.emailAddress)
                        .focused($focusedField, equals: .login)
                        .foregroundColor(.textPrimary)
                        .placeholder(when: login.isEmpty) {
                            Text("Digite seu email ou CPF")
                                .foregroundColor(.textMuted)
                        }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 14)
                .background(Color.backgroundSecondary)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(
                            focusedField == .login ? Color.courtGreen : Color.clear,
                            lineWidth: 1.5
                        )
                )
            }

            // Campo de senha
            VStack(alignment: .leading, spacing: 8) {
                Text("Senha")
                    .font(.labelMedium)
                    .foregroundColor(.textSecondary)

                HStack(spacing: 12) {
                    Image(systemName: "lock.fill")
                        .foregroundColor(.textMuted)
                        .frame(width: 20)

                    SecureField("", text: $password)
                        .textContentType(.password)
                        .focused($focusedField, equals: .password)
                        .foregroundColor(.textPrimary)
                        .placeholder(when: password.isEmpty) {
                            Text("Digite sua senha")
                                .foregroundColor(.textMuted)
                        }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 14)
                .background(Color.backgroundSecondary)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(
                            focusedField == .password ? Color.courtGreen : Color.clear,
                            lineWidth: 1.5
                        )
                )
            }
        }
    }

    // MARK: - Login Button

    private var loginButton: some View {
        Button(action: performLogin) {
            HStack(spacing: 12) {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "arrow.right.circle.fill")
                    Text("Entrar")
                }
            }
            .primaryButtonStyle(isEnabled: isFormValid && !isLoading)
        }
        .disabled(!isFormValid || isLoading)
    }

    // MARK: - Version Label

    private var versionLabel: some View {
        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
        let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"

        return Text("v\(version) (\(build))")
            .font(.labelSmall)
            .foregroundColor(.textMuted)
            .padding(.bottom, 16)
    }

    // MARK: - Validation

    private var isFormValid: Bool {
        !login.trimmingCharacters(in: .whitespaces).isEmpty
        && !password.isEmpty
    }

    // MARK: - Actions

    private func performLogin() {
        guard isFormValid else { return }

        focusedField = nil
        isLoading = true
        errorMessage = ""

        Task {
            do {
                let response = try await AuthService.shared.login(
                    login: login.trimmingCharacters(in: .whitespaces),
                    password: password
                )

                await MainActor.run {
                    isLoading = false
                    appState.login(token: response.token, user: response.user)
                }
            } catch let error as APIError {
                await MainActor.run {
                    isLoading = false
                    errorMessage = error.errorDescription ?? "Erro desconhecido"
                    showError = true
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = "Falha na conexao. Verifique sua internet."
                    showError = true
                }
            }
        }
    }
}

// MARK: - Placeholder Modifier

extension View {
    func placeholder<Content: View>(
        when shouldShow: Bool,
        alignment: Alignment = .leading,
        @ViewBuilder placeholder: () -> Content
    ) -> some View {
        ZStack(alignment: alignment) {
            placeholder().opacity(shouldShow ? 1 : 0)
            self
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AppState())
}
