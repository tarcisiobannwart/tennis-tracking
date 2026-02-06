package com.tennistrack.app.streaming

import android.util.Log
import android.view.SurfaceView
import com.pedro.common.ConnectChecker
import com.pedro.encoder.input.video.CameraHelper
import com.pedro.library.rtmp.RtmpCamera2

class RtmpStreamer : ConnectChecker {

    companion object {
        private const val TAG = "RtmpStreamer"
    }

    private var rtmpCamera: RtmpCamera2? = null
    private var currentResolution: ResolutionPreset = CameraManager.RESOLUTION_720P
    private var _isStreaming = false

    var onConnectionStarted: (() -> Unit)? = null
    var onConnectionSuccess: (() -> Unit)? = null
    var onConnectionFailed: ((reason: String) -> Unit)? = null
    var onDisconnected: (() -> Unit)? = null
    var onNewBitrateCallback: ((bitrate: Long) -> Unit)? = null

    fun initCamera(surfaceView: SurfaceView) {
        rtmpCamera = RtmpCamera2(surfaceView, this)
    }

    fun startPreview(resolution: ResolutionPreset = currentResolution) {
        currentResolution = resolution
        rtmpCamera?.let { camera ->
            if (!camera.isOnPreview) {
                camera.startPreview(
                    CameraHelper.Facing.BACK,
                    resolution.width,
                    resolution.height
                )
            }
        }
    }

    fun stopPreview() {
        rtmpCamera?.let { camera ->
            if (camera.isOnPreview) {
                camera.stopPreview()
            }
        }
    }

    fun startStream(rtmpUrl: String) {
        rtmpCamera?.let { camera ->
            if (!camera.isStreaming) {
                if (camera.prepareAudio(
                        currentResolution.audioBitrate,
                        44100,
                        true
                    ) && camera.prepareVideo(
                        currentResolution.width,
                        currentResolution.height,
                        currentResolution.fps,
                        currentResolution.videoBitrate,
                        0
                    )
                ) {
                    camera.startStream(rtmpUrl)
                    onConnectionStarted?.invoke()
                    Log.d(TAG, "Stream iniciado para: $rtmpUrl")
                } else {
                    onConnectionFailed?.invoke("Falha ao preparar audio/video")
                    Log.e(TAG, "Falha ao preparar audio/video")
                }
            }
        } ?: run {
            onConnectionFailed?.invoke("Camera nao inicializada")
        }
    }

    fun stopStream() {
        rtmpCamera?.let { camera ->
            if (camera.isStreaming) {
                camera.stopStream()
            }
        }
        _isStreaming = false
    }

    fun switchCamera() {
        try {
            rtmpCamera?.switchCamera()
        } catch (e: Exception) {
            Log.e(TAG, "Erro ao trocar camera: ${e.message}")
        }
    }

    fun toggleFlash(): Boolean {
        rtmpCamera?.let { camera ->
            if (camera.isLanternEnabled) {
                camera.disableLantern()
                return false
            } else {
                try {
                    camera.enableLantern()
                    return true
                } catch (e: Exception) {
                    Log.e(TAG, "Flash nao disponivel: ${e.message}")
                    return false
                }
            }
        }
        return false
    }

    fun setResolution(preset: ResolutionPreset) {
        val wasStreaming = isStreaming()
        val wasOnPreview = rtmpCamera?.isOnPreview == true

        if (wasStreaming) {
            stopStream()
        }
        if (wasOnPreview) {
            stopPreview()
        }

        currentResolution = preset

        if (wasOnPreview) {
            startPreview(preset)
        }
    }

    fun isStreaming(): Boolean {
        return rtmpCamera?.isStreaming == true
    }

    fun isOnPreview(): Boolean {
        return rtmpCamera?.isOnPreview == true
    }

    fun getBitrate(): Int {
        return currentResolution.videoBitrate
    }

    fun getCurrentResolution(): ResolutionPreset {
        return currentResolution
    }

    fun release() {
        stopStream()
        stopPreview()
        rtmpCamera = null
    }

    // ConnectChecker callbacks

    override fun onConnectionStarted(url: String) {
        Log.d(TAG, "Conexao iniciada: $url")
    }

    override fun onConnectionSuccess() {
        _isStreaming = true
        Log.d(TAG, "Conexao RTMP estabelecida")
        onConnectionSuccess?.invoke()
    }

    override fun onConnectionFailed(reason: String) {
        _isStreaming = false
        Log.e(TAG, "Conexao RTMP falhou: $reason")
        onConnectionFailed?.invoke(reason)
    }

    override fun onNewBitrate(bitrate: Long) {
        onNewBitrateCallback?.invoke(bitrate)
    }

    override fun onDisconnect() {
        _isStreaming = false
        Log.d(TAG, "Desconectado do RTMP")
        onDisconnected?.invoke()
    }

    override fun onAuthError() {
        _isStreaming = false
        Log.e(TAG, "Erro de autenticacao RTMP")
        onConnectionFailed?.invoke("Erro de autenticacao RTMP")
    }

    override fun onAuthSuccess() {
        Log.d(TAG, "Autenticacao RTMP bem-sucedida")
    }
}
