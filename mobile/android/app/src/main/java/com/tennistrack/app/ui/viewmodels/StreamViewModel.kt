package com.tennistrack.app.ui.viewmodels

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tennistrack.app.data.model.StreamResponse
import com.tennistrack.app.data.repository.StreamRepository
import com.tennistrack.app.streaming.CameraManager
import com.tennistrack.app.streaming.ResolutionPreset
import com.tennistrack.app.ui.components.ConnectionState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class StreamUiState(
    val matchId: String? = null,
    val streamResponse: StreamResponse? = null,
    val connectionState: ConnectionState = ConnectionState.IDLE,
    val isStreaming: Boolean = false,
    val isFlashOn: Boolean = false,
    val currentResolution: ResolutionPreset = CameraManager.RESOLUTION_720P,
    val cameraLabel: String = "Camera 1",
    val durationSeconds: Long = 0,
    val currentBitrate: Long = 0,
    val errorMessage: String? = null
)

@HiltViewModel
class StreamViewModel @Inject constructor(
    private val streamRepository: StreamRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow(StreamUiState())
    val uiState: StateFlow<StreamUiState> = _uiState.asStateFlow()

    private var timerJob: Job? = null

    init {
        val matchId = savedStateHandle.get<String>("matchId")
        if (matchId != null && matchId != "null") {
            _uiState.value = _uiState.value.copy(matchId = matchId)
        }
    }

    fun createStream(): String? {
        var rtmpUrl: String? = null
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                connectionState = ConnectionState.CONNECTING,
                errorMessage = null
            )

            val resolution = CameraManager.getResolutionString(_uiState.value.currentResolution)

            val result = streamRepository.createStream(
                matchId = _uiState.value.matchId,
                cameraLabel = _uiState.value.cameraLabel,
                resolution = resolution
            )

            result.fold(
                onSuccess = { stream ->
                    rtmpUrl = stream.rtmpUrl
                    _uiState.value = _uiState.value.copy(
                        streamResponse = stream
                    )
                },
                onFailure = { exception ->
                    _uiState.value = _uiState.value.copy(
                        connectionState = ConnectionState.ERROR,
                        errorMessage = exception.message
                    )
                }
            )
        }
        return rtmpUrl
    }

    fun onStreamStarted() {
        _uiState.value = _uiState.value.copy(
            connectionState = ConnectionState.CONNECTING,
            isStreaming = false
        )
    }

    fun onConnectionSuccess() {
        _uiState.value = _uiState.value.copy(
            connectionState = ConnectionState.LIVE,
            isStreaming = true,
            durationSeconds = 0
        )
        startTimer()
    }

    fun onConnectionFailed(reason: String) {
        stopTimer()
        _uiState.value = _uiState.value.copy(
            connectionState = ConnectionState.ERROR,
            isStreaming = false,
            errorMessage = "Falha na conexao: $reason"
        )
    }

    fun onDisconnected() {
        stopTimer()
        _uiState.value = _uiState.value.copy(
            connectionState = ConnectionState.DISCONNECTED,
            isStreaming = false
        )
    }

    fun onStreamStopped() {
        stopTimer()
        viewModelScope.launch {
            val streamId = _uiState.value.streamResponse?.id
            if (streamId != null) {
                streamRepository.deleteStream(streamId)
            }
            _uiState.value = _uiState.value.copy(
                connectionState = ConnectionState.IDLE,
                isStreaming = false,
                streamResponse = null,
                durationSeconds = 0,
                currentBitrate = 0
            )
        }
    }

    fun onBitrateUpdate(bitrate: Long) {
        _uiState.value = _uiState.value.copy(currentBitrate = bitrate)
    }

    fun onFlashToggled(isOn: Boolean) {
        _uiState.value = _uiState.value.copy(isFlashOn = isOn)
    }

    fun onResolutionChanged(label: String) {
        val preset = CameraManager.getPresetByLabel(label)
        _uiState.value = _uiState.value.copy(currentResolution = preset)
    }

    fun setCameraLabel(label: String) {
        _uiState.value = _uiState.value.copy(cameraLabel = label)
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    fun formatDuration(): String {
        val seconds = _uiState.value.durationSeconds
        val hours = seconds / 3600
        val minutes = (seconds % 3600) / 60
        val secs = seconds % 60
        return if (hours > 0) {
            String.format("%02d:%02d:%02d", hours, minutes, secs)
        } else {
            String.format("%02d:%02d", minutes, secs)
        }
    }

    fun formatBitrate(): String {
        val bitrate = _uiState.value.currentBitrate
        return when {
            bitrate >= 1_000_000 -> String.format("%.1f Mbps", bitrate / 1_000_000.0)
            bitrate >= 1_000 -> String.format("%.0f Kbps", bitrate / 1_000.0)
            else -> "$bitrate bps"
        }
    }

    private fun startTimer() {
        timerJob?.cancel()
        timerJob = viewModelScope.launch {
            while (true) {
                delay(1000)
                _uiState.value = _uiState.value.copy(
                    durationSeconds = _uiState.value.durationSeconds + 1
                )
            }
        }
    }

    private fun stopTimer() {
        timerJob?.cancel()
        timerJob = null
    }

    override fun onCleared() {
        super.onCleared()
        stopTimer()
    }
}
