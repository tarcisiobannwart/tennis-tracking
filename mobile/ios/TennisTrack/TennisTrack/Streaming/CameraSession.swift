import AVFoundation

final class CameraSession {

    /// Retorna o AVCaptureDevice para a posicao de camera especificada
    static func captureDevice(position: AVCaptureDevice.Position) -> AVCaptureDevice? {
        // Tentar usar camera wide-angle primeiro (qualidade padrao)
        if let device = AVCaptureDevice.default(
            .builtInWideAngleCamera,
            for: .video,
            position: position
        ) {
            return device
        }

        // Fallback para qualquer camera disponivel na posicao
        let discoverySession = AVCaptureDevice.DiscoverySession(
            deviceTypes: [.builtInWideAngleCamera, .builtInDualCamera, .builtInTripleCamera],
            mediaType: .video,
            position: position
        )

        return discoverySession.devices.first
    }

    /// Retorna o dispositivo de audio padrao
    static func audioDevice() -> AVCaptureDevice? {
        AVCaptureDevice.default(for: .audio)
    }

    /// Configura a resolucao do dispositivo de captura
    static func configureResolution(
        _ device: AVCaptureDevice,
        resolution: VideoResolution
    ) throws {
        try device.lockForConfiguration()
        defer { device.unlockForConfiguration() }

        let preset = sessionPreset(for: resolution)

        // Configurar formato ativo que mais se aproxima da resolucao desejada
        let targetWidth = resolution.width
        let targetHeight = resolution.height

        let bestFormat = device.formats
            .filter { format in
                let dimensions = CMVideoFormatDescriptionGetDimensions(format.formatDescription)
                return dimensions.width >= Int32(targetWidth)
                    && dimensions.height >= Int32(targetHeight)
            }
            .sorted { a, b in
                let aDim = CMVideoFormatDescriptionGetDimensions(a.formatDescription)
                let bDim = CMVideoFormatDescriptionGetDimensions(b.formatDescription)
                return (aDim.width * aDim.height) < (bDim.width * bDim.height)
            }
            .first

        if let format = bestFormat {
            device.activeFormat = format

            // Configurar frame rate (30fps)
            let targetFrameRate = CMTimeMake(value: 1, timescale: 30)
            device.activeVideoMinFrameDuration = targetFrameRate
            device.activeVideoMaxFrameDuration = targetFrameRate
        }
    }

    /// Retorna o AVCaptureSession.Preset para a resolucao
    static func sessionPreset(for resolution: VideoResolution) -> AVCaptureSession.Preset {
        switch resolution {
        case .sd480:
            return .medium
        case .hd720:
            return .hd1280x720
        case .fullHD1080:
            return .hd1920x1080
        }
    }

    /// Verifica se a camera tem torch (flash)
    static func hasTorch(position: AVCaptureDevice.Position = .back) -> Bool {
        guard let device = captureDevice(position: position) else { return false }
        return device.hasTorch
    }

    /// Liga ou desliga o torch
    static func setTorch(enabled: Bool, position: AVCaptureDevice.Position = .back) throws {
        guard let device = captureDevice(position: position),
              device.hasTorch else {
            return
        }

        try device.lockForConfiguration()
        defer { device.unlockForConfiguration() }

        device.torchMode = enabled ? .on : .off
    }

    /// Verifica permissoes de camera e microfone
    static func checkPermissions() async -> (camera: Bool, microphone: Bool) {
        let cameraStatus = await withCheckedContinuation { continuation in
            switch AVCaptureDevice.authorizationStatus(for: .video) {
            case .authorized:
                continuation.resume(returning: true)
            case .notDetermined:
                AVCaptureDevice.requestAccess(for: .video) { granted in
                    continuation.resume(returning: granted)
                }
            default:
                continuation.resume(returning: false)
            }
        }

        let micStatus = await withCheckedContinuation { continuation in
            switch AVCaptureDevice.authorizationStatus(for: .audio) {
            case .authorized:
                continuation.resume(returning: true)
            case .notDetermined:
                AVCaptureDevice.requestAccess(for: .audio) { granted in
                    continuation.resume(returning: granted)
                }
            default:
                continuation.resume(returning: false)
            }
        }

        return (camera: cameraStatus, microphone: micStatus)
    }

    /// Lista todas as cameras disponiveis
    static func availableCameras() -> [AVCaptureDevice] {
        let discoverySession = AVCaptureDevice.DiscoverySession(
            deviceTypes: [
                .builtInWideAngleCamera,
                .builtInDualCamera,
                .builtInTripleCamera,
                .builtInUltraWideCamera,
                .builtInTelephotoCamera
            ],
            mediaType: .video,
            position: .unspecified
        )

        return discoverySession.devices
    }

    /// Configura auto focus e exposicao continua
    static func configureAutoSettings(_ device: AVCaptureDevice) throws {
        try device.lockForConfiguration()
        defer { device.unlockForConfiguration() }

        if device.isFocusModeSupported(.continuousAutoFocus) {
            device.focusMode = .continuousAutoFocus
        }

        if device.isExposureModeSupported(.continuousAutoExposure) {
            device.exposureMode = .continuousAutoExposure
        }

        if device.isWhiteBalanceModeSupported(.continuousAutoWhiteBalance) {
            device.whiteBalanceMode = .continuousAutoWhiteBalance
        }

        // Estabilizacao de video
        let connection = AVCaptureConnection(inputPort: AVCaptureInput.Port(), videoOrientation: .landscapeRight)
        if connection.isVideoStabilizationSupported {
            connection.preferredVideoStabilizationMode = .auto
        }
    }
}
