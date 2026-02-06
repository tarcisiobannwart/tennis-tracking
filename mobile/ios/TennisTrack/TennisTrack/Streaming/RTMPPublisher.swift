import AVFoundation
import Combine
import HaishinKit

enum ConnectionState: String {
    case idle = "Inativo"
    case connecting = "Conectando"
    case connected = "Conectado"
    case publishing = "Ao Vivo"
    case disconnected = "Desconectado"
    case error = "Erro"

    var isLive: Bool {
        self == .publishing
    }
}

final class RTMPPublisher: ObservableObject {
    @Published var isStreaming: Bool = false
    @Published var connectionState: ConnectionState = .idle
    @Published var currentBitrate: Int = 3_000_000
    @Published var streamDuration: TimeInterval = 0
    @Published var isFrontCamera: Bool = false
    @Published var isTorchOn: Bool = false
    @Published var errorMessage: String? = nil

    private var rtmpConnection = RTMPConnection()
    private var rtmpStream: RTMPStream!
    private var durationTimer: Timer?
    private var streamStartTime: Date?
    private var retryCount = 0
    private let maxRetries = 3
    private var cancellables = Set<AnyCancellable>()

    var currentStream: RTMPStream {
        rtmpStream
    }

    init() {
        rtmpStream = RTMPStream(connection: rtmpConnection)
        configureStream(resolution: .hd720)
        setupConnectionHandlers()
    }

    deinit {
        stopPublishing()
    }

    // MARK: - Configuration

    func configureStream(resolution: VideoResolution) {
        let videoSettings = VideoCodecSettings()
        videoSettings.videoSize = CGSize(width: resolution.width, height: resolution.height)
        videoSettings.bitRate = resolution.bitrate
        videoSettings.profileLevel = kVTProfileLevel_H264_Baseline_AutoLevel as String
        videoSettings.maxKeyFrameIntervalDuration = 2
        rtmpStream.videoSettings = videoSettings

        let audioSettings = AudioCodecSettings()
        audioSettings.bitRate = 128_000
        rtmpStream.audioSettings = audioSettings

        currentBitrate = resolution.bitrate
    }

    func setVideoSettings(width: Int, height: Int, bitrate: Int) {
        let videoSettings = VideoCodecSettings()
        videoSettings.videoSize = CGSize(width: width, height: height)
        videoSettings.bitRate = bitrate
        videoSettings.profileLevel = kVTProfileLevel_H264_Baseline_AutoLevel as String
        videoSettings.maxKeyFrameIntervalDuration = 2
        rtmpStream.videoSettings = videoSettings

        currentBitrate = bitrate
    }

    // MARK: - Camera Attachment

    func attachCamera() async {
        do {
            let position: AVCaptureDevice.Position = isFrontCamera ? .front : .back
            let device = CameraSession.captureDevice(position: position)

            try await rtmpStream.attachCamera(device)
            try await rtmpStream.attachAudio(AVCaptureDevice.default(for: .audio))
        } catch {
            await MainActor.run {
                errorMessage = "Erro ao acessar camera: \(error.localizedDescription)"
                connectionState = .error
            }
        }
    }

    // MARK: - Publishing

    func startPublishing(rtmpUrl: String, streamKey: String) {
        guard !isStreaming else { return }

        errorMessage = nil
        connectionState = .connecting
        retryCount = 0

        let fullUrl: String
        if rtmpUrl.hasSuffix("/") {
            fullUrl = "\(rtmpUrl.dropLast())/\(streamKey)"
        } else {
            fullUrl = "\(rtmpUrl)/\(streamKey)"
        }

        guard let url = URL(string: fullUrl),
              let scheme = url.scheme,
              let host = url.host else {
            connectionState = .error
            errorMessage = "URL RTMP invalida: \(fullUrl)"
            return
        }

        let port = url.port ?? (scheme == "rtmps" ? 443 : 1935)
        let baseUrl = "\(scheme)://\(host):\(port)"

        let pathComponents = url.pathComponents.filter { $0 != "/" }
        let appName = pathComponents.count > 1
            ? pathComponents.dropLast().joined(separator: "/")
            : pathComponents.first ?? "live"
        let streamName = pathComponents.last ?? streamKey

        Task {
            do {
                try await rtmpConnection.connect(baseUrl + "/" + appName)
                await MainActor.run {
                    connectionState = .connected
                }

                try await rtmpStream.publish(streamName)
                await MainActor.run {
                    isStreaming = true
                    connectionState = .publishing
                    startDurationTimer()
                }
            } catch {
                await MainActor.run {
                    connectionState = .error
                    errorMessage = "Falha ao conectar: \(error.localizedDescription)"
                    handleConnectionFailure()
                }
            }
        }
    }

    func stopPublishing() {
        guard isStreaming || connectionState != .idle else { return }

        Task {
            try? await rtmpStream.close()
            try? await rtmpConnection.close()

            await MainActor.run {
                isStreaming = false
                connectionState = .idle
                stopDurationTimer()
                streamDuration = 0
                retryCount = 0
            }
        }
    }

    // MARK: - Camera Controls

    func switchCamera() {
        isFrontCamera.toggle()

        Task {
            let position: AVCaptureDevice.Position = isFrontCamera ? .front : .back
            let device = CameraSession.captureDevice(position: position)

            do {
                try await rtmpStream.attachCamera(device)
            } catch {
                await MainActor.run {
                    errorMessage = "Erro ao trocar camera: \(error.localizedDescription)"
                }
            }

            if isFrontCamera && isTorchOn {
                await MainActor.run {
                    isTorchOn = false
                }
            }
        }
    }

    func toggleTorch() {
        guard !isFrontCamera else { return }

        let newState = !isTorchOn
        let device = CameraSession.captureDevice(position: .back)

        guard let device = device, device.hasTorch else { return }

        do {
            try device.lockForConfiguration()
            device.torchMode = newState ? .on : .off
            device.unlockForConfiguration()
            isTorchOn = newState
        } catch {
            errorMessage = "Erro ao controlar flash: \(error.localizedDescription)"
        }
    }

    // MARK: - Duration Timer

    private func startDurationTimer() {
        streamStartTime = Date()
        streamDuration = 0

        durationTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self, let startTime = self.streamStartTime else { return }
            Task { @MainActor in
                self.streamDuration = Date().timeIntervalSince(startTime)
            }
        }
    }

    private func stopDurationTimer() {
        durationTimer?.invalidate()
        durationTimer = nil
        streamStartTime = nil
    }

    // MARK: - Connection Handlers

    private func setupConnectionHandlers() {
        // Observar estado da conexao via KVO ou notificacoes do HaishinKit
        // O HaishinKit emite eventos de conexao via delegate pattern
    }

    private func handleConnectionFailure() {
        guard retryCount < maxRetries else {
            errorMessage = "Falha apos \(maxRetries) tentativas. Verifique a conexao."
            return
        }

        retryCount += 1
        let delay = Double(retryCount) * 2.0

        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.connectionState = .connecting
        }
    }

    // MARK: - Formatted Duration

    var formattedDuration: String {
        let hours = Int(streamDuration) / 3600
        let minutes = (Int(streamDuration) % 3600) / 60
        let seconds = Int(streamDuration) % 60

        if hours > 0 {
            return String(format: "%02d:%02d:%02d", hours, minutes, seconds)
        }
        return String(format: "%02d:%02d", minutes, seconds)
    }

    var formattedBitrate: String {
        let mbps = Double(currentBitrate) / 1_000_000.0
        return String(format: "%.1f Mbps", mbps)
    }
}
