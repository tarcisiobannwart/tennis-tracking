package com.tennistrack.app.streaming;

import android.util.Log;
import android.view.SurfaceView;
import com.pedro.common.ConnectChecker;
import com.pedro.encoder.input.video.CameraHelper;
import com.pedro.library.rtmp.RtmpCamera2;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000V\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\b\u000b\n\u0002\u0010\t\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0014\u0018\u0000 =2\u00020\u0001:\u0001=B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0006\u0010%\u001a\u00020&J\u0006\u0010\'\u001a\u00020\u0006J\u000e\u0010(\u001a\u00020\r2\u0006\u0010)\u001a\u00020*J\u0006\u0010+\u001a\u00020\u0004J\u0006\u0010,\u001a\u00020\u0004J\b\u0010-\u001a\u00020\rH\u0016J\b\u0010.\u001a\u00020\rH\u0016J\u0010\u0010\u0007\u001a\u00020\r2\u0006\u0010\f\u001a\u00020\tH\u0016J\u0010\u0010\u0012\u001a\u00020\r2\u0006\u0010/\u001a\u00020\tH\u0016J\b\u0010\u0018\u001a\u00020\rH\u0016J\b\u00100\u001a\u00020\rH\u0016J\u0010\u00101\u001a\u00020\r2\u0006\u0010 \u001a\u00020\u001fH\u0016J\u0006\u00102\u001a\u00020\rJ\u000e\u00103\u001a\u00020\r2\u0006\u00104\u001a\u00020\u0006J\u0010\u00105\u001a\u00020\r2\b\b\u0002\u00106\u001a\u00020\u0006J\u000e\u00107\u001a\u00020\r2\u0006\u00108\u001a\u00020\tJ\u0006\u00109\u001a\u00020\rJ\u0006\u0010:\u001a\u00020\rJ\u0006\u0010;\u001a\u00020\rJ\u0006\u0010<\u001a\u00020\u0004R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082\u000e\u00a2\u0006\u0002\n\u0000R7\u0010\u0007\u001a\u001f\u0012\u0013\u0012\u00110\t\u00a2\u0006\f\b\n\u0012\b\b\u000b\u0012\u0004\b\b(\f\u0012\u0004\u0012\u00020\r\u0018\u00010\bX\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u000e\u0010\u000f\"\u0004\b\u0010\u0010\u0011R\"\u0010\u0012\u001a\n\u0012\u0004\u0012\u00020\r\u0018\u00010\u0013X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u0014\u0010\u0015\"\u0004\b\u0016\u0010\u0017R\"\u0010\u0018\u001a\n\u0012\u0004\u0012\u00020\r\u0018\u00010\u0013X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u0019\u0010\u0015\"\u0004\b\u001a\u0010\u0017R\"\u0010\u001b\u001a\n\u0012\u0004\u0012\u00020\r\u0018\u00010\u0013X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u001c\u0010\u0015\"\u0004\b\u001d\u0010\u0017R7\u0010\u001e\u001a\u001f\u0012\u0013\u0012\u00110\u001f\u00a2\u0006\f\b\n\u0012\b\b\u000b\u0012\u0004\b\b( \u0012\u0004\u0012\u00020\r\u0018\u00010\bX\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b!\u0010\u000f\"\u0004\b\"\u0010\u0011R\u0010\u0010#\u001a\u0004\u0018\u00010$X\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006>"}, d2 = {"Lcom/tennistrack/app/streaming/RtmpStreamer;", "Lcom/pedro/common/ConnectChecker;", "()V", "_isStreaming", "", "currentResolution", "Lcom/tennistrack/app/streaming/ResolutionPreset;", "onConnectionFailed", "Lkotlin/Function1;", "", "Lkotlin/ParameterName;", "name", "reason", "", "getOnConnectionFailed", "()Lkotlin/jvm/functions/Function1;", "setOnConnectionFailed", "(Lkotlin/jvm/functions/Function1;)V", "onConnectionStarted", "Lkotlin/Function0;", "getOnConnectionStarted", "()Lkotlin/jvm/functions/Function0;", "setOnConnectionStarted", "(Lkotlin/jvm/functions/Function0;)V", "onConnectionSuccess", "getOnConnectionSuccess", "setOnConnectionSuccess", "onDisconnected", "getOnDisconnected", "setOnDisconnected", "onNewBitrateCallback", "", "bitrate", "getOnNewBitrateCallback", "setOnNewBitrateCallback", "rtmpCamera", "Lcom/pedro/library/rtmp/RtmpCamera2;", "getBitrate", "", "getCurrentResolution", "initCamera", "surfaceView", "Landroid/view/SurfaceView;", "isOnPreview", "isStreaming", "onAuthError", "onAuthSuccess", "url", "onDisconnect", "onNewBitrate", "release", "setResolution", "preset", "startPreview", "resolution", "startStream", "rtmpUrl", "stopPreview", "stopStream", "switchCamera", "toggleFlash", "Companion", "app_debug"})
public final class RtmpStreamer implements com.pedro.common.ConnectChecker {
    @org.jetbrains.annotations.NotNull()
    private static final java.lang.String TAG = "RtmpStreamer";
    @org.jetbrains.annotations.Nullable()
    private com.pedro.library.rtmp.RtmpCamera2 rtmpCamera;
    @org.jetbrains.annotations.NotNull()
    private com.tennistrack.app.streaming.ResolutionPreset currentResolution;
    private boolean _isStreaming = false;
    @org.jetbrains.annotations.Nullable()
    private kotlin.jvm.functions.Function0<kotlin.Unit> onConnectionStarted;
    @org.jetbrains.annotations.Nullable()
    private kotlin.jvm.functions.Function0<kotlin.Unit> onConnectionSuccess;
    @org.jetbrains.annotations.Nullable()
    private kotlin.jvm.functions.Function1<? super java.lang.String, kotlin.Unit> onConnectionFailed;
    @org.jetbrains.annotations.Nullable()
    private kotlin.jvm.functions.Function0<kotlin.Unit> onDisconnected;
    @org.jetbrains.annotations.Nullable()
    private kotlin.jvm.functions.Function1<? super java.lang.Long, kotlin.Unit> onNewBitrateCallback;
    @org.jetbrains.annotations.NotNull()
    public static final com.tennistrack.app.streaming.RtmpStreamer.Companion Companion = null;
    
    public RtmpStreamer() {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final kotlin.jvm.functions.Function0<kotlin.Unit> getOnConnectionStarted() {
        return null;
    }
    
    public final void setOnConnectionStarted(@org.jetbrains.annotations.Nullable()
    kotlin.jvm.functions.Function0<kotlin.Unit> p0) {
    }
    
    @org.jetbrains.annotations.Nullable()
    public final kotlin.jvm.functions.Function0<kotlin.Unit> getOnConnectionSuccess() {
        return null;
    }
    
    public final void setOnConnectionSuccess(@org.jetbrains.annotations.Nullable()
    kotlin.jvm.functions.Function0<kotlin.Unit> p0) {
    }
    
    @org.jetbrains.annotations.Nullable()
    public final kotlin.jvm.functions.Function1<java.lang.String, kotlin.Unit> getOnConnectionFailed() {
        return null;
    }
    
    public final void setOnConnectionFailed(@org.jetbrains.annotations.Nullable()
    kotlin.jvm.functions.Function1<? super java.lang.String, kotlin.Unit> p0) {
    }
    
    @org.jetbrains.annotations.Nullable()
    public final kotlin.jvm.functions.Function0<kotlin.Unit> getOnDisconnected() {
        return null;
    }
    
    public final void setOnDisconnected(@org.jetbrains.annotations.Nullable()
    kotlin.jvm.functions.Function0<kotlin.Unit> p0) {
    }
    
    @org.jetbrains.annotations.Nullable()
    public final kotlin.jvm.functions.Function1<java.lang.Long, kotlin.Unit> getOnNewBitrateCallback() {
        return null;
    }
    
    public final void setOnNewBitrateCallback(@org.jetbrains.annotations.Nullable()
    kotlin.jvm.functions.Function1<? super java.lang.Long, kotlin.Unit> p0) {
    }
    
    public final void initCamera(@org.jetbrains.annotations.NotNull()
    android.view.SurfaceView surfaceView) {
    }
    
    public final void startPreview(@org.jetbrains.annotations.NotNull()
    com.tennistrack.app.streaming.ResolutionPreset resolution) {
    }
    
    public final void stopPreview() {
    }
    
    public final void startStream(@org.jetbrains.annotations.NotNull()
    java.lang.String rtmpUrl) {
    }
    
    public final void stopStream() {
    }
    
    public final void switchCamera() {
    }
    
    public final boolean toggleFlash() {
        return false;
    }
    
    public final void setResolution(@org.jetbrains.annotations.NotNull()
    com.tennistrack.app.streaming.ResolutionPreset preset) {
    }
    
    public final boolean isStreaming() {
        return false;
    }
    
    public final boolean isOnPreview() {
        return false;
    }
    
    public final int getBitrate() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.streaming.ResolutionPreset getCurrentResolution() {
        return null;
    }
    
    public final void release() {
    }
    
    @java.lang.Override()
    public void onConnectionStarted(@org.jetbrains.annotations.NotNull()
    java.lang.String url) {
    }
    
    @java.lang.Override()
    public void onConnectionSuccess() {
    }
    
    @java.lang.Override()
    public void onConnectionFailed(@org.jetbrains.annotations.NotNull()
    java.lang.String reason) {
    }
    
    @java.lang.Override()
    public void onNewBitrate(long bitrate) {
    }
    
    @java.lang.Override()
    public void onDisconnect() {
    }
    
    @java.lang.Override()
    public void onAuthError() {
    }
    
    @java.lang.Override()
    public void onAuthSuccess() {
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0012\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0005"}, d2 = {"Lcom/tennistrack/app/streaming/RtmpStreamer$Companion;", "", "()V", "TAG", "", "app_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
    }
}