package com.tennistrack.app.ui.viewmodels;

import androidx.lifecycle.SavedStateHandle;
import androidx.lifecycle.ViewModel;
import com.tennistrack.app.data.model.StreamResponse;
import com.tennistrack.app.data.repository.StreamRepository;
import com.tennistrack.app.streaming.CameraManager;
import com.tennistrack.app.streaming.ResolutionPreset;
import com.tennistrack.app.ui.components.ConnectionState;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000N\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0010\t\n\u0002\b\u0007\n\u0002\u0010\u000b\n\u0002\b\b\b\u0007\u0018\u00002\u00020\u0001B\u0017\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J\u0006\u0010\u0010\u001a\u00020\u0011J\b\u0010\u0012\u001a\u0004\u0018\u00010\u0013J\u0006\u0010\u0014\u001a\u00020\u0013J\u0006\u0010\u0015\u001a\u00020\u0013J\u000e\u0010\u0016\u001a\u00020\u00112\u0006\u0010\u0017\u001a\u00020\u0018J\b\u0010\u0019\u001a\u00020\u0011H\u0014J\u000e\u0010\u001a\u001a\u00020\u00112\u0006\u0010\u001b\u001a\u00020\u0013J\u0006\u0010\u001c\u001a\u00020\u0011J\u0006\u0010\u001d\u001a\u00020\u0011J\u000e\u0010\u001e\u001a\u00020\u00112\u0006\u0010\u001f\u001a\u00020 J\u000e\u0010!\u001a\u00020\u00112\u0006\u0010\"\u001a\u00020\u0013J\u0006\u0010#\u001a\u00020\u0011J\u0006\u0010$\u001a\u00020\u0011J\u000e\u0010%\u001a\u00020\u00112\u0006\u0010\"\u001a\u00020\u0013J\b\u0010&\u001a\u00020\u0011H\u0002J\b\u0010\'\u001a\u00020\u0011H\u0002R\u0014\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\n\u001a\u0004\u0018\u00010\u000bX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0017\u0010\f\u001a\b\u0012\u0004\u0012\u00020\t0\r\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000f\u00a8\u0006("}, d2 = {"Lcom/tennistrack/app/ui/viewmodels/StreamViewModel;", "Landroidx/lifecycle/ViewModel;", "streamRepository", "Lcom/tennistrack/app/data/repository/StreamRepository;", "savedStateHandle", "Landroidx/lifecycle/SavedStateHandle;", "(Lcom/tennistrack/app/data/repository/StreamRepository;Landroidx/lifecycle/SavedStateHandle;)V", "_uiState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/tennistrack/app/ui/viewmodels/StreamUiState;", "timerJob", "Lkotlinx/coroutines/Job;", "uiState", "Lkotlinx/coroutines/flow/StateFlow;", "getUiState", "()Lkotlinx/coroutines/flow/StateFlow;", "clearError", "", "createStream", "", "formatBitrate", "formatDuration", "onBitrateUpdate", "bitrate", "", "onCleared", "onConnectionFailed", "reason", "onConnectionSuccess", "onDisconnected", "onFlashToggled", "isOn", "", "onResolutionChanged", "label", "onStreamStarted", "onStreamStopped", "setCameraLabel", "startTimer", "stopTimer", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel()
public final class StreamViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull()
    private final com.tennistrack.app.data.repository.StreamRepository streamRepository = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.tennistrack.app.ui.viewmodels.StreamUiState> _uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.tennistrack.app.ui.viewmodels.StreamUiState> uiState = null;
    @org.jetbrains.annotations.Nullable()
    private kotlinx.coroutines.Job timerJob;
    
    @javax.inject.Inject()
    public StreamViewModel(@org.jetbrains.annotations.NotNull()
    com.tennistrack.app.data.repository.StreamRepository streamRepository, @org.jetbrains.annotations.NotNull()
    androidx.lifecycle.SavedStateHandle savedStateHandle) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.tennistrack.app.ui.viewmodels.StreamUiState> getUiState() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String createStream() {
        return null;
    }
    
    public final void onStreamStarted() {
    }
    
    public final void onConnectionSuccess() {
    }
    
    public final void onConnectionFailed(@org.jetbrains.annotations.NotNull()
    java.lang.String reason) {
    }
    
    public final void onDisconnected() {
    }
    
    public final void onStreamStopped() {
    }
    
    public final void onBitrateUpdate(long bitrate) {
    }
    
    public final void onFlashToggled(boolean isOn) {
    }
    
    public final void onResolutionChanged(@org.jetbrains.annotations.NotNull()
    java.lang.String label) {
    }
    
    public final void setCameraLabel(@org.jetbrains.annotations.NotNull()
    java.lang.String label) {
    }
    
    public final void clearError() {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String formatDuration() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String formatBitrate() {
        return null;
    }
    
    private final void startTimer() {
    }
    
    private final void stopTimer() {
    }
    
    @java.lang.Override()
    protected void onCleared() {
    }
}