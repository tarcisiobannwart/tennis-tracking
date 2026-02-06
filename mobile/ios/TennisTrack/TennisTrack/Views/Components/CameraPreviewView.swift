import SwiftUI
import HaishinKit

/// UIViewRepresentable que encapsula a MTHKView do HaishinKit
/// para exibir o preview da camera no SwiftUI.
struct CameraPreviewView: UIViewRepresentable {
    let stream: RTMPStream

    func makeUIView(context: Context) -> MTHKView {
        let view = MTHKView(frame: .zero)
        view.videoGravity = .resizeAspectFill
        view.backgroundColor = .black
        view.translatesAutoresizingMaskIntoConstraints = false

        Task { @MainActor in
            await view.attachStream(stream)
        }

        return view
    }

    func updateUIView(_ uiView: MTHKView, context: Context) {
        // O stream ja esta vinculado na criacao.
        // Atualizacoes de stream sao gerenciadas pelo RTMPPublisher.
    }

    static func dismantleUIView(_ uiView: MTHKView, coordinator: ()) {
        Task { @MainActor in
            await uiView.attachStream(nil)
        }
    }
}

/// Preview wrapper para usar quando nao ha HaishinKit disponivel (simulador)
struct CameraPreviewPlaceholder: View {
    var body: some View {
        ZStack {
            Color.black

            VStack(spacing: 16) {
                Image(systemName: "video.slash")
                    .font(.system(size: 48))
                    .foregroundColor(.textMuted)

                Text("Preview indisponivel")
                    .font(.bodyMedium)
                    .foregroundColor(.textSecondary)

                Text("Use um dispositivo fisico para preview da camera")
                    .font(.labelSmall)
                    .foregroundColor(.textMuted)
                    .multilineTextAlignment(.center)
            }
        }
    }
}

#Preview {
    CameraPreviewPlaceholder()
}
