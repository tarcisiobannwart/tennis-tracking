import SwiftUI

struct MatchListView: View {
    @EnvironmentObject var appState: AppState

    @State private var matches: [Match] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showStreamView: Bool = false
    @State private var selectedMatchForStream: Match? = nil

    var body: some View {
        ZStack {
            Color.backgroundPrimary.ignoresSafeArea()

            if isLoading && matches.isEmpty {
                loadingView
            } else if let error = errorMessage, matches.isEmpty {
                errorView(message: error)
            } else if matches.isEmpty {
                emptyView
            } else {
                matchList
            }
        }
        .navigationTitle("Partidas")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    Task { await loadMatches() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.courtGreen)
                }
            }
        }
        .task {
            await loadMatches()
        }
        .refreshable {
            await loadMatches()
        }
        .fullScreenCover(item: $selectedMatchForStream) { match in
            StreamView(match: match)
                .environmentObject(appState)
        }
    }

    // MARK: - Match List

    private var matchList: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(matches) { match in
                    MatchCardView(match: match) {
                        selectedMatchForStream = match
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
        }
    }

    // MARK: - Loading

    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .tint(.courtGreen)
                .scaleEffect(1.2)
            Text("Carregando partidas...")
                .font(.bodyMedium)
                .foregroundColor(.textSecondary)
        }
    }

    // MARK: - Empty

    private var emptyView: some View {
        VStack(spacing: 20) {
            Image(systemName: "sportscourt")
                .font(.system(size: 48))
                .foregroundColor(.textMuted)

            Text("Nenhuma partida encontrada")
                .font(.titleSmall)
                .foregroundColor(.textSecondary)

            Text("Aguardando partidas serem agendadas.")
                .font(.bodyMedium)
                .foregroundColor(.textMuted)
                .multilineTextAlignment(.center)

            Button {
                Task { await loadMatches() }
            } label: {
                HStack(spacing: 8) {
                    Image(systemName: "arrow.clockwise")
                    Text("Atualizar")
                }
                .font(.labelLarge)
                .foregroundColor(.courtGreen)
                .padding(.horizontal, 24)
                .padding(.vertical, 12)
                .background(Color.courtGreen.opacity(0.15))
                .cornerRadius(10)
            }
        }
        .padding(32)
    }

    // MARK: - Error

    private func errorView(message: String) -> some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 48))
                .foregroundColor(.ballYellow)

            Text("Erro ao carregar")
                .font(.titleSmall)
                .foregroundColor(.textPrimary)

            Text(message)
                .font(.bodyMedium)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)

            Button {
                Task { await loadMatches() }
            } label: {
                HStack(spacing: 8) {
                    Image(systemName: "arrow.clockwise")
                    Text("Tentar novamente")
                }
                .font(.labelLarge)
                .foregroundColor(.white)
                .padding(.horizontal, 24)
                .padding(.vertical, 12)
                .background(Color.courtGreen)
                .cornerRadius(10)
            }
        }
        .padding(32)
    }

    // MARK: - Data Loading

    private func loadMatches() async {
        isLoading = true
        errorMessage = nil

        do {
            let result = try await APIService.shared.getMatches()
            await MainActor.run {
                matches = result
                isLoading = false
            }
        } catch {
            await MainActor.run {
                errorMessage = (error as? APIError)?.errorDescription
                    ?? "Falha ao carregar partidas."
                isLoading = false
            }
        }
    }
}

// MARK: - Match Card

struct MatchCardView: View {
    let match: Match
    let onStream: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header: status e surface
            HStack {
                statusBadge

                Spacer()

                surfaceBadge
            }

            // Players
            VStack(alignment: .leading, spacing: 4) {
                Text(match.player1)
                    .font(.titleSmall)
                    .foregroundColor(.textPrimary)

                Text("vs")
                    .font(.bodySmall)
                    .foregroundColor(.textMuted)

                Text(match.player2)
                    .font(.titleSmall)
                    .foregroundColor(.textPrimary)
            }

            // Score (se disponivel)
            if let score = match.score, !score.isEmpty {
                Text(score)
                    .font(.monoMedium)
                    .foregroundColor(.ballYellow)
            }

            Divider()
                .background(Color.backgroundTertiary)

            // Footer: data e botao
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    if let tournament = match.tournament {
                        Text(tournament)
                            .font(.labelSmall)
                            .foregroundColor(.textSecondary)
                    }
                    Text(match.displayDate)
                        .font(.labelSmall)
                        .foregroundColor(.textMuted)
                }

                Spacer()

                if match.status == .live || match.status == .scheduled {
                    Button(action: onStream) {
                        HStack(spacing: 6) {
                            Image(systemName: "video.fill")
                            Text("Transmitir")
                        }
                        .font(.labelMedium)
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.courtGreen)
                        .cornerRadius(8)
                    }
                }
            }
        }
        .padding(16)
        .cardStyle()
    }

    private var statusBadge: some View {
        HStack(spacing: 6) {
            if match.status == .live {
                Circle()
                    .fill(Color.statusLive)
                    .frame(width: 8, height: 8)
            }

            Image(systemName: match.status.iconName)
                .font(.labelSmall)

            Text(match.status.displayName)
                .font(.labelSmall)
        }
        .foregroundColor(match.status == .live ? .statusLive : .textSecondary)
        .padding(.horizontal, 10)
        .padding(.vertical, 4)
        .background(
            (match.status == .live ? Color.statusLive : Color.textMuted)
                .opacity(0.15)
        )
        .cornerRadius(6)
    }

    private var surfaceBadge: some View {
        HStack(spacing: 4) {
            Image(systemName: match.surface.iconName)
                .font(.system(size: 10))
            Text(match.surface.displayName)
                .font(.labelSmall)
        }
        .foregroundColor(.textSecondary)
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color.backgroundTertiary)
        .cornerRadius(6)
    }
}

#Preview {
    NavigationStack {
        MatchListView()
            .environmentObject(AppState())
    }
}
