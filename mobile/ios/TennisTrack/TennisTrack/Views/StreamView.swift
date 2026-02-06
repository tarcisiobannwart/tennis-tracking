import SwiftUI
import AVFoundation

struct StreamView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) private var dismiss

    @StateObject private var publisher = RTMPPublisher()

    let match: Match

    @State private var cameraLabel: String = "Camera 1"
    @State private var selectedResolution: VideoResolution = .hd720
    @State private var showQualityPicker: Bool = false
    @State private var showDismissConfirmation: Bool = false
    @State private var streamResponse: StreamResponse? = nil
    @State private var isCreatingStream: Bool = false
    @State private var permissionsGranted: Bool = false
    @State private var showError: Bool = false
    @State private var errorText: String = ""

    var body: some View {
        ZStack {
            // Camera preview (background)
            CameraPreviewView(stream: publisher.currentStream)
                .ignoresSafeArea()

            // Overlay de controles
            streamOverlay

            // Quality picker overlay
            if showQualityPicker {
                qualityPickerOverlay
            }
        }
        .statusBarHidden(true)
        .persistentSystemOverlays(.hidden)
        .onAppear {
            selectedResolution = appState.defaultResolution
            publisher.configureStream(resolution: selectedResolution)
            checkPermissionsAndSetup()
        }
        .onDisappear {
            publisher.stopPublishing()
        }
        .alert("Encerrar transmissao?", isPresented: $showDismissConfirmation) {
            Button("Continuar", role: .cancel) {}
            Button("Encerrar", role: .destructive) {
                endStreamAndDismiss()
            }
        } message: {
            Text("A transmissao sera encerrada e os espectadores serao desconectados.")
        }
        .alert("Erro", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorText)
        }
    }

    // MARK: - Stream Overlay

    private var streamOverlay: some View {
        VStack {
            // Top bar
            topControlBar

            Spacer()

            // Bottom controls
            bottomControlBar
        }
        .padding(20)
    }

    // MARK: - Top Control Bar

    private var topControlBar: some View {
        HStack(alignment: .top) {
            // Dismiss button
            Button {
                if publisher.isStreaming {
                    showDismissConfirmation = true
                } else {
                    dismiss()
                }
            } label: {
                Image(systemName: "xmark")
                    .streamControlButton()
            }

            Spacer()

            // Status central
            VStack(spacing: 6) {
                ConnectionStatusView(state: publisher.connectionState)

                if publisher.isStreaming {
                    // Duration
                    HStack(spacing: 4) {
                        Circle()
                            .fill(Color.statusLive)
                            .frame(width: 8, height: 8)
                            .opacity(pulsingOpacity)

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

            Spacer()

            // Bitrate e camera label
            VStack(alignment: .trailing, spacing: 6) {
                Text(cameraLabel)
                    .font(.labelSmall)
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(Color.black.opacity(0.5))
                    .cornerRadius(6)

                if publisher.isStreaming {
                    Text(publisher.formattedBitrate)
                        .font(.monoSmall)
                        .foregroundColor(.ballYellow)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Color.black.opacity(0.5))
                        .cornerRadius(6)
                }
            }
        }
    }

    // MARK: - Bottom Control Bar

    private var bottomControlBar: some View {
        HStack(alignment: .bottom, spacing: 24) {
            // Qualidade
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showQualityPicker.toggle()
                }
            } label: {
                VStack(spacing: 4) {
                    Image(systemName: "slider.horizontal.3")
                        .streamControlButton()
                    Text(selectedResolution.rawValue)
                        .font(.labelSmall)
                        .foregroundColor(.white)
                }
            }
            .disabled(publisher.isStreaming)
            .opacity(publisher.isStreaming ? 0.5 : 1.0)

            // Torch
            Button {
                publisher.toggleTorch()
            } label: {
                VStack(spacing: 4) {
                    Image(systemName: publisher.isTorchOn ? "flashlight.on.fill" : "flashlight.off.fill")
                        .streamControlButton()
                    Text("Flash")
                        .font(.labelSmall)
                        .foregroundColor(.white)
                }
            }
            .disabled(publisher.isFrontCamera)
            .opacity(publisher.isFrontCamera ? 0.5 : 1.0)

            Spacer()

            // Record button (centro)
            recordButton

            Spacer()

            // Camera flip
            Button {
                publisher.switchCamera()
            } label: {
                VStack(spacing: 4) {
                    Image(systemName: "camera.rotate")
                        .streamControlButton()
                    Text("Inverter")
                        .font(.labelSmall)
                        .foregroundColor(.white)
                }
            }

            // Placeholder para simetria
            Color.clear
                .frame(width: 44, height: 44)
        }
    }

    // MARK: - Record Button

    private var recordButton: some View {
        Button {
            if publisher.isStreaming {
                showDismissConfirmation = true
            } else {
                startStream()
            }
        } label: {
            ZStack {
                Circle()
                    .stroke(Color.white, lineWidth: 4)
                    .frame(width: 72, height: 72)

                if publisher.isStreaming {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color.statusLive)
                        .frame(width: 28, height: 28)
                } else if isCreatingStream {
                    ProgressView()
                        .tint(.white)
                } else {
                    Circle()
                        .fill(Color.statusLive)
                        .frame(width: 58, height: 58)
                }
            }
            .opacity(publisher.isStreaming ? pulsingOpacity : 1.0)
        }
        .disabled(isCreatingStream || !permissionsGranted)
    }

    // MARK: - Quality Picker

    private var qualityPickerOverlay: some View {
        VStack {
            Spacer()

            VStack(spacing: 0) {
                HStack {
                    Text("Qualidade de Video")
                        .font(.titleSmall)
                        .foregroundColor(.textPrimary)

                    Spacer()

                    Button {
                        withAnimation {
                            showQualityPicker = false
                        }
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.textMuted)
                            .font(.title3)
                    }
                }
                .padding(16)

                ForEach(VideoResolution.allCases) { resolution in
                    Button {
                        selectedResolution = resolution
                        publisher.configureStream(resolution: resolution)
                        withAnimation {
                            showQualityPicker = false
                        }
                    } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(resolution.displayName)
                                    .font(.bodyMedium)
                                    .foregroundColor(.textPrimary)

                                Text("\(resolution.width)x\(resolution.height) - \(resolution.bitrate / 1_000_000) Mbps")
                                    .font(.labelSmall)
                                    .foregroundColor(.textMuted)
                            }

                            Spacer()

                            if resolution == selectedResolution {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.courtGreen)
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                    }

                    if resolution != VideoResolution.allCases.last {
                        Divider()
                            .background(Color.backgroundTertiary)
                            .padding(.horizontal, 16)
                    }
                }
            }
            .background(Color.backgroundSecondary)
            .cornerRadius(16)
            .padding(.horizontal, 20)
            .padding(.bottom, 100)
        }
        .background(Color.black.opacity(0.4))
        .onTapGesture {
            withAnimation {
                showQualityPicker = false
            }
        }
    }

    // MARK: - Pulsing Animation

    @State private var isPulsing: Bool = false

    private var pulsingOpacity: Double {
        isPulsing ? 0.6 : 1.0
    }

    // MARK: - Actions

    private func checkPermissionsAndSetup() {
        Task {
            let permissions = await CameraSession.checkPermissions()

            if !permissions.camera {
                await MainActor.run {
                    errorText = "Permissao de camera negada. Habilite nas Configuracoes."
                    showError = true
                }
                return
            }

            await MainActor.run {
                permissionsGranted = true
            }

            await publisher.attachCamera()

            // Animacao de pulso
            withAnimation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true)) {
                isPulsing = true
            }
        }
    }

    private func startStream() {
        guard !isCreatingStream else { return }

        isCreatingStream = true

        Task {
            do {
                let response = try await APIService.shared.createStream(
                    matchId: match.id,
                    cameraLabel: cameraLabel,
                    resolution: selectedResolution
                )

                await MainActor.run {
                    streamResponse = response
                    isCreatingStream = false
                    publisher.startPublishing(
                        rtmpUrl: response.rtmpUrl,
                        streamKey: response.streamKey
                    )
                }
            } catch {
                await MainActor.run {
                    isCreatingStream = false
                    errorText = (error as? APIError)?.errorDescription
                        ?? "Falha ao criar stream."
                    showError = true
                }
            }
        }
    }

    private func endStreamAndDismiss() {
        publisher.stopPublishing()

        if let streamId = streamResponse?.id {
            Task {
                try? await APIService.shared.endStream(id: streamId)
            }
        }

        dismiss()
    }
}

#Preview {
    StreamView(
        match: Match(
            id: "1",
            player1: "Rafael Nadal",
            player2: "Roger Federer",
            score: "6-4 3-2",
            status: .live,
            surface: .clay,
            date: "2025-01-15T14:00:00Z",
            tournament: "Roland Garros",
            round: "Final"
        )
    )
    .environmentObject(AppState())
}
