import Foundation

struct StreamResponse: Codable, Identifiable {
    let id: String
    let streamKey: String
    let rtmpUrl: String
    let hlsUrl: String?
    let status: StreamStatus
    let matchId: String?
    let cameraLabel: String?
    let createdAt: String?
    let updatedAt: String?
    let deviceInfo: DeviceInfo?

    enum CodingKeys: String, CodingKey {
        case id
        case streamKey = "stream_key"
        case rtmpUrl = "rtmp_url"
        case hlsUrl = "hls_url"
        case status
        case matchId = "match_id"
        case cameraLabel = "camera_label"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case deviceInfo = "device_info"
    }
}

enum StreamStatus: String, Codable {
    case created
    case active
    case ended
    case error

    var displayName: String {
        switch self {
        case .created: return "Criado"
        case .active: return "Ao Vivo"
        case .ended: return "Encerrado"
        case .error: return "Erro"
        }
    }
}

struct StreamListResponse: Codable {
    let streams: [StreamResponse]
    let total: Int?
}

struct CreateStreamRequest: Codable {
    let matchId: String
    let cameraLabel: String
    let deviceInfo: DeviceInfo

    enum CodingKeys: String, CodingKey {
        case matchId = "match_id"
        case cameraLabel = "camera_label"
        case deviceInfo = "device_info"
    }
}

struct DeviceInfo: Codable {
    let deviceModel: String
    let osVersion: String
    let appVersion: String
    let resolution: String
    let bitrate: Int

    enum CodingKeys: String, CodingKey {
        case deviceModel = "device_model"
        case osVersion = "os_version"
        case appVersion = "app_version"
        case resolution
        case bitrate
    }

    static func current(resolution: VideoResolution) -> DeviceInfo {
        var systemInfo = utsname()
        uname(&systemInfo)
        let modelCode = withUnsafePointer(to: &systemInfo.machine) {
            $0.withMemoryRebound(to: CChar.self, capacity: 1) {
                String(validatingUTF8: $0) ?? "Unknown"
            }
        }

        let osVersion = ProcessInfo.processInfo.operatingSystemVersion
        let osString = "\(osVersion.majorVersion).\(osVersion.minorVersion).\(osVersion.patchVersion)"

        let appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"

        return DeviceInfo(
            deviceModel: modelCode,
            osVersion: "iOS \(osString)",
            appVersion: appVersion,
            resolution: "\(resolution.width)x\(resolution.height)",
            bitrate: resolution.bitrate
        )
    }
}

struct EndStreamRequest: Codable {
    let streamId: String

    enum CodingKeys: String, CodingKey {
        case streamId = "stream_id"
    }
}
