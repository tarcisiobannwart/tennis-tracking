import SwiftUI

/// View reutilizavel de controles de streaming com fundo semi-transparente
struct StreamControlsView: View {
    @ObservedObject var publisher: RTMPPublisher

    let selectedResolution: VideoResolution
    let onRecord: () -> Void
    let onSwitchCamera: () -> Void
    let onToggleTorch: () -> Void
    let onSelectQuality: () -> Void
    let onDismiss: () -> Void

    var body: some View {
        VStack {
            // Barra superior
            topBar

            Spacer()

            // Barra inferior
            bottomBar
        }
        .padding(16)
    }

    // MARK: - Top Bar

    private var topBar: some View {
        HStack {
            // Botao fechar
            ControlButton(
                iconName: "xmark",
                label: nil,
                action: onDismiss
            )

            Spacer()

            // Status e duracao
            VStack(spacing: 4) {
                ConnectionStatusView(state: publisher.connectionState)

                if publisher.isStreaming {
                    durationBadge
                }
            }

            Spacer()

            // Bitrate
            if publisher.isStreaming {
                Text(publisher.formattedBitrate)
                    .font(.monoSmall)
                    .foregroundColor(.ballYellow)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.black.opacity(0.5))
                    .cornerRadius(8)
            } else {
                Color.clear.frame(width: 44, height: 44)
            }
        }
    }

    // MARK: - Bottom Bar

    private var bottomBar: some View {
        HStack(alignment: .bottom, spacing: 20) {
            // Qualidade
            ControlButton(
                iconName: "slider.horizontal.3",
                label: selectedResolution.rawValue,
                action: onSelectQuality,
                isDisabled: publisher.isStreaming
            )

            // Torch
            ControlButton(
                iconName: publisher.isTorchOn ? "flashlight.on.fill" : "flashlight.off.fill",
                label: "Flash",
                action: onToggleTorch,
                isDisabled: publisher.isFrontCamera
            )

            Spacer()

            // Botao de gravar
            RecordButton(
                isStreaming: publisher.isStreaming,
                isLoading: false,
                action: onRecord
            )

            Spacer()

            // Inverter camera
            ControlButton(
                iconName: "camera.rotate",
                label: "Inverter",
                action: onSwitchCamera
            )

            // Spacer para simetria
            Color.clear.frame(width: 44, height: 44)
        }
    }

    // MARK: - Duration Badge

    private var durationBadge: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(Color.statusLive)
                .frame(width: 8, height: 8)

            Text(publisher.formattedDuration)
                .font(.monoMedium)
                .foregroundColor(.white)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(Color.black.opacity(0.6))
        .cornerRadius(8)
    }
}

// MARK: - Control Button

struct ControlButton: View {
    let iconName: String
    let label: String?
    let action: () -> Void
    var isDisabled: Bool = false

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: iconName)
                    .font(.system(size: 20))
                    .foregroundColor(.white)
                    .frame(width: 44, height: 44)
                    .background(Color.black.opacity(0.5))
                    .clipShape(Circle())

                if let label = label {
                    Text(label)
                        .font(.labelSmall)
                        .foregroundColor(.white)
                }
            }
        }
        .disabled(isDisabled)
        .opacity(isDisabled ? 0.5 : 1.0)
    }
}

// MARK: - Record Button

struct RecordButton: View {
    let isStreaming: Bool
    let isLoading: Bool
    let action: () -> Void

    @State private var isPulsing = false

    var body: some View {
        Button(action: action) {
            ZStack {
                // Anel externo
                Circle()
                    .stroke(Color.white, lineWidth: 4)
                    .frame(width: 72, height: 72)

                // Centro
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else if isStreaming {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color.statusLive)
                        .frame(width: 28, height: 28)
                } else {
                    Circle()
                        .fill(Color.statusLive)
                        .frame(width: 58, height: 58)
                }
            }
            .scaleEffect(isStreaming && isPulsing ? 0.92 : 1.0)
        }
        .disabled(isLoading)
        .onAppear {
            withAnimation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true)) {
                isPulsing = true
            }
        }
    }
}

#Preview {
    ZStack {
        Color.black.ignoresSafeArea()

        StreamControlsView(
            publisher: RTMPPublisher(),
            selectedResolution: .hd720,
            onRecord: {},
            onSwitchCamera: {},
            onToggleTorch: {},
            onSelectQuality: {},
            onDismiss: {}
        )
    }
}
