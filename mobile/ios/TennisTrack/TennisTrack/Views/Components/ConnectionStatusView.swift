import SwiftUI

/// Badge de status da conexao RTMP.
/// Exibe o estado atual com cores e icones correspondentes.
struct ConnectionStatusView: View {
    let state: ConnectionState

    var body: some View {
        HStack(spacing: 6) {
            // Icone de status
            statusIcon

            // Texto de status
            Text(state.rawValue)
                .font(.labelMedium)
                .foregroundColor(.white)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(statusBackgroundColor.opacity(0.85))
        .cornerRadius(8)
    }

    // MARK: - Status Icon

    @ViewBuilder
    private var statusIcon: some View {
        switch state {
        case .idle:
            Image(systemName: "circle")
                .font(.system(size: 10))
                .foregroundColor(.textMuted)

        case .connecting:
            ProgressView()
                .tint(.white)
                .scaleEffect(0.7)
                .frame(width: 14, height: 14)

        case .connected:
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 12))
                .foregroundColor(.white)

        case .publishing:
            PulsingDot()

        case .disconnected:
            Image(systemName: "wifi.slash")
                .font(.system(size: 12))
                .foregroundColor(.white)

        case .error:
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 12))
                .foregroundColor(.white)
        }
    }

    // MARK: - Background Color

    private var statusBackgroundColor: Color {
        switch state {
        case .idle:
            return Color.backgroundTertiary
        case .connecting:
            return Color.statusConnecting
        case .connected:
            return Color.statusConnected
        case .publishing:
            return Color.statusLive
        case .disconnected:
            return Color.statusDisconnected
        case .error:
            return Color.statusError
        }
    }
}

// MARK: - Pulsing Dot

/// Ponto vermelho pulsante para indicar transmissao ao vivo
struct PulsingDot: View {
    @State private var isPulsing = false

    var body: some View {
        Circle()
            .fill(Color.white)
            .frame(width: 10, height: 10)
            .scaleEffect(isPulsing ? 1.2 : 0.8)
            .opacity(isPulsing ? 1.0 : 0.6)
            .onAppear {
                withAnimation(
                    .easeInOut(duration: 0.6)
                    .repeatForever(autoreverses: true)
                ) {
                    isPulsing = true
                }
            }
    }
}

// MARK: - Compact Variant

/// Versao compacta do status para uso em barras menores
struct ConnectionStatusCompactView: View {
    let state: ConnectionState

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(dotColor)
                .frame(width: 8, height: 8)

            Text(state.rawValue)
                .font(.labelSmall)
                .foregroundColor(.textSecondary)
        }
    }

    private var dotColor: Color {
        switch state {
        case .idle: return .textMuted
        case .connecting: return .statusConnecting
        case .connected: return .statusConnected
        case .publishing: return .statusLive
        case .disconnected: return .statusDisconnected
        case .error: return .statusError
        }
    }
}

#Preview {
    VStack(spacing: 16) {
        ConnectionStatusView(state: .idle)
        ConnectionStatusView(state: .connecting)
        ConnectionStatusView(state: .connected)
        ConnectionStatusView(state: .publishing)
        ConnectionStatusView(state: .disconnected)
        ConnectionStatusView(state: .error)

        Divider()

        ConnectionStatusCompactView(state: .publishing)
        ConnectionStatusCompactView(state: .disconnected)
    }
    .padding()
    .background(Color.backgroundPrimary)
}
