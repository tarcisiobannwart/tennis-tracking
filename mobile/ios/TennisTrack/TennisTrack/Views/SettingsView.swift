import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var appState: AppState

    @State private var serverURL: String = ""
    @State private var showLogoutConfirmation: Bool = false

    var body: some View {
        Form {
            // Servidor
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("URL do Servidor")
                        .font(.labelMedium)
                        .foregroundColor(.textSecondary)

                    TextField("https://api.tennistrack.local", text: $serverURL)
                        .textContentType(.URL)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        .keyboardType(.URL)
                        .foregroundColor(.textPrimary)
                        .onSubmit {
                            appState.serverURL = serverURL
                        }
                }
            } header: {
                Text("Servidor")
            } footer: {
                Text("Endereco do servidor de API. Alteracoes sao aplicadas imediatamente.")
            }

            // Video
            Section {
                Picker("Resolucao Padrao", selection: $appState.defaultResolution) {
                    ForEach(VideoResolution.allCases) { resolution in
                        VStack(alignment: .leading) {
                            Text(resolution.displayName)
                        }
                        .tag(resolution)
                    }
                }
                .tint(.courtGreen)

                HStack {
                    Text("Bitrate estimado")
                        .foregroundColor(.textPrimary)

                    Spacer()

                    Text(formatBitrate(appState.defaultResolution.bitrate))
                        .foregroundColor(.textSecondary)
                        .font(.monoSmall)
                }
            } header: {
                Text("Video")
            } footer: {
                Text("A resolucao padrao sera usada ao iniciar novas transmissoes. Pode ser alterada antes de iniciar cada stream.")
            }

            // Audio
            Section {
                Toggle("Audio habilitado", isOn: $appState.audioEnabled)
                    .tint(.courtGreen)
            } header: {
                Text("Audio")
            } footer: {
                Text("Quando desabilitado, a transmissao envia apenas video sem audio.")
            }

            // Conta
            Section {
                if let user = appState.currentUser {
                    HStack {
                        // Avatar
                        ZStack {
                            Circle()
                                .fill(Color.courtGreen.opacity(0.2))
                                .frame(width: 44, height: 44)

                            Text(user.initials)
                                .font(.labelLarge)
                                .foregroundColor(.courtGreen)
                        }

                        VStack(alignment: .leading, spacing: 2) {
                            Text(user.name)
                                .font(.bodyMedium)
                                .foregroundColor(.textPrimary)

                            Text(user.email)
                                .font(.labelSmall)
                                .foregroundColor(.textSecondary)

                            if let role = user.role {
                                Text(role.displayName)
                                    .font(.labelSmall)
                                    .foregroundColor(.textMuted)
                            }
                        }
                    }
                    .padding(.vertical, 4)
                }

                Button(role: .destructive) {
                    showLogoutConfirmation = true
                } label: {
                    HStack {
                        Image(systemName: "rectangle.portrait.and.arrow.right")
                        Text("Sair da conta")
                    }
                    .foregroundColor(.statusLive)
                }
            } header: {
                Text("Conta")
            }

            // Sobre
            Section {
                HStack {
                    Text("Versao")
                        .foregroundColor(.textPrimary)
                    Spacer()
                    Text(appVersion)
                        .foregroundColor(.textSecondary)
                }

                HStack {
                    Text("Build")
                        .foregroundColor(.textPrimary)
                    Spacer()
                    Text(buildNumber)
                        .foregroundColor(.textSecondary)
                }

                HStack {
                    Text("Dispositivo")
                        .foregroundColor(.textPrimary)
                    Spacer()
                    Text(deviceModel)
                        .foregroundColor(.textSecondary)
                        .font(.labelSmall)
                }

                HStack {
                    Text("iOS")
                        .foregroundColor(.textPrimary)
                    Spacer()
                    Text(iosVersion)
                        .foregroundColor(.textSecondary)
                }
            } header: {
                Text("Sobre")
            }
        }
        .scrollContentBackground(.hidden)
        .background(Color.backgroundPrimary.ignoresSafeArea())
        .navigationTitle("Ajustes")
        .onAppear {
            serverURL = appState.serverURL
        }
        .alert("Sair da conta?", isPresented: $showLogoutConfirmation) {
            Button("Cancelar", role: .cancel) {}
            Button("Sair", role: .destructive) {
                appState.logout()
            }
        } message: {
            Text("Voce sera desconectado e precisara fazer login novamente.")
        }
    }

    // MARK: - Helpers

    private func formatBitrate(_ bitrate: Int) -> String {
        let mbps = Double(bitrate) / 1_000_000.0
        return String(format: "%.1f Mbps", mbps)
    }

    private var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
    }

    private var buildNumber: String {
        Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
    }

    private var deviceModel: String {
        var systemInfo = utsname()
        uname(&systemInfo)
        return withUnsafePointer(to: &systemInfo.machine) {
            $0.withMemoryRebound(to: CChar.self, capacity: 1) {
                String(validatingUTF8: $0) ?? "Unknown"
            }
        }
    }

    private var iosVersion: String {
        let version = ProcessInfo.processInfo.operatingSystemVersion
        return "\(version.majorVersion).\(version.minorVersion).\(version.patchVersion)"
    }
}

#Preview {
    NavigationStack {
        SettingsView()
            .environmentObject(AppState())
    }
}
