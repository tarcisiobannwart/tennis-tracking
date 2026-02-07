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

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000<\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\t\n\u0002\b\u001f\n\u0002\u0010\b\n\u0002\b\u0002\b\u0086\b\u0018\u00002\u00020\u0001Bo\u0012\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u0012\b\b\u0002\u0010\u0006\u001a\u00020\u0007\u0012\b\b\u0002\u0010\b\u001a\u00020\t\u0012\b\b\u0002\u0010\n\u001a\u00020\t\u0012\b\b\u0002\u0010\u000b\u001a\u00020\f\u0012\b\b\u0002\u0010\r\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u000e\u001a\u00020\u000f\u0012\b\b\u0002\u0010\u0010\u001a\u00020\u000f\u0012\n\b\u0002\u0010\u0011\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\u0002\u0010\u0012J\u000b\u0010!\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\u000b\u0010\"\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\u000b\u0010#\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003J\t\u0010$\u001a\u00020\u0007H\u00c6\u0003J\t\u0010%\u001a\u00020\tH\u00c6\u0003J\t\u0010&\u001a\u00020\tH\u00c6\u0003J\t\u0010\'\u001a\u00020\fH\u00c6\u0003J\t\u0010(\u001a\u00020\u0003H\u00c6\u0003J\t\u0010)\u001a\u00020\u000fH\u00c6\u0003J\t\u0010*\u001a\u00020\u000fH\u00c6\u0003Js\u0010+\u001a\u00020\u00002\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u00032\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u00052\b\b\u0002\u0010\u0006\u001a\u00020\u00072\b\b\u0002\u0010\b\u001a\u00020\t2\b\b\u0002\u0010\n\u001a\u00020\t2\b\b\u0002\u0010\u000b\u001a\u00020\f2\b\b\u0002\u0010\r\u001a\u00020\u00032\b\b\u0002\u0010\u000e\u001a\u00020\u000f2\b\b\u0002\u0010\u0010\u001a\u00020\u000f2\n\b\u0002\u0010\u0011\u001a\u0004\u0018\u00010\u0003H\u00c6\u0001J\u0013\u0010,\u001a\u00020\t2\b\u0010-\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010.\u001a\u00020/H\u00d6\u0001J\t\u00100\u001a\u00020\u0003H\u00d6\u0001R\u0011\u0010\r\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\u0014R\u0011\u0010\u0006\u001a\u00020\u0007\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0015\u0010\u0016R\u0011\u0010\u0010\u001a\u00020\u000f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0017\u0010\u0018R\u0011\u0010\u000b\u001a\u00020\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0019\u0010\u001aR\u0011\u0010\u000e\u001a\u00020\u000f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001b\u0010\u0018R\u0013\u0010\u0011\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001c\u0010\u0014R\u0011\u0010\n\u001a\u00020\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u001dR\u0011\u0010\b\u001a\u00020\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\b\u0010\u001dR\u0013\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001e\u0010\u0014R\u0013\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001f\u0010 \u00a8\u00061"}, d2 = {"Lcom/tennistrack/app/ui/viewmodels/StreamUiState;", "", "matchId", "", "streamResponse", "Lcom/tennistrack/app/data/model/StreamResponse;", "connectionState", "Lcom/tennistrack/app/ui/components/ConnectionState;", "isStreaming", "", "isFlashOn", "currentResolution", "Lcom/tennistrack/app/streaming/ResolutionPreset;", "cameraLabel", "durationSeconds", "", "currentBitrate", "errorMessage", "(Ljava/lang/String;Lcom/tennistrack/app/data/model/StreamResponse;Lcom/tennistrack/app/ui/components/ConnectionState;ZZLcom/tennistrack/app/streaming/ResolutionPreset;Ljava/lang/String;JJLjava/lang/String;)V", "getCameraLabel", "()Ljava/lang/String;", "getConnectionState", "()Lcom/tennistrack/app/ui/components/ConnectionState;", "getCurrentBitrate", "()J", "getCurrentResolution", "()Lcom/tennistrack/app/streaming/ResolutionPreset;", "getDurationSeconds", "getErrorMessage", "()Z", "getMatchId", "getStreamResponse", "()Lcom/tennistrack/app/data/model/StreamResponse;", "component1", "component10", "component2", "component3", "component4", "component5", "component6", "component7", "component8", "component9", "copy", "equals", "other", "hashCode", "", "toString", "app_debug"})
public final class StreamUiState {
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String matchId = null;
    @org.jetbrains.annotations.Nullable()
    private final com.tennistrack.app.data.model.StreamResponse streamResponse = null;
    @org.jetbrains.annotations.NotNull()
    private final com.tennistrack.app.ui.components.ConnectionState connectionState = null;
    private final boolean isStreaming = false;
    private final boolean isFlashOn = false;
    @org.jetbrains.annotations.NotNull()
    private final com.tennistrack.app.streaming.ResolutionPreset currentResolution = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String cameraLabel = null;
    private final long durationSeconds = 0L;
    private final long currentBitrate = 0L;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String errorMessage = null;
    
    public StreamUiState(@org.jetbrains.annotations.Nullable()
    java.lang.String matchId, @org.jetbrains.annotations.Nullable()
    com.tennistrack.app.data.model.StreamResponse streamResponse, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.ui.components.ConnectionState connectionState, boolean isStreaming, boolean isFlashOn, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.streaming.ResolutionPreset currentResolution, @org.jetbrains.annotations.NotNull()
    java.lang.String cameraLabel, long durationSeconds, long currentBitrate, @org.jetbrains.annotations.Nullable()
    java.lang.String errorMessage) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getMatchId() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.tennistrack.app.data.model.StreamResponse getStreamResponse() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.ui.components.ConnectionState getConnectionState() {
        return null;
    }
    
    public final boolean isStreaming() {
        return false;
    }
    
    public final boolean isFlashOn() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.streaming.ResolutionPreset getCurrentResolution() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getCameraLabel() {
        return null;
    }
    
    public final long getDurationSeconds() {
        return 0L;
    }
    
    public final long getCurrentBitrate() {
        return 0L;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getErrorMessage() {
        return null;
    }
    
    public StreamUiState() {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component1() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component10() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.tennistrack.app.data.model.StreamResponse component2() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.ui.components.ConnectionState component3() {
        return null;
    }
    
    public final boolean component4() {
        return false;
    }
    
    public final boolean component5() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.streaming.ResolutionPreset component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component7() {
        return null;
    }
    
    public final long component8() {
        return 0L;
    }
    
    public final long component9() {
        return 0L;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.ui.viewmodels.StreamUiState copy(@org.jetbrains.annotations.Nullable()
    java.lang.String matchId, @org.jetbrains.annotations.Nullable()
    com.tennistrack.app.data.model.StreamResponse streamResponse, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.ui.components.ConnectionState connectionState, boolean isStreaming, boolean isFlashOn, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.streaming.ResolutionPreset currentResolution, @org.jetbrains.annotations.NotNull()
    java.lang.String cameraLabel, long durationSeconds, long currentBitrate, @org.jetbrains.annotations.Nullable()
    java.lang.String errorMessage) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}