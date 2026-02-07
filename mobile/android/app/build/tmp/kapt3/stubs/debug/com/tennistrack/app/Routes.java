package com.tennistrack.app;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Bundle;
import androidx.activity.ComponentActivity;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.compose.runtime.Composable;
import androidx.compose.ui.Modifier;
import androidx.core.content.ContextCompat;
import androidx.navigation.NavType;
import com.tennistrack.app.ui.viewmodels.LoginViewModel;
import dagger.hilt.android.AndroidEntryPoint;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0007\b\u00c6\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0010\u0010\t\u001a\u00020\u00042\b\u0010\n\u001a\u0004\u0018\u00010\u0004R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\b\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u000b"}, d2 = {"Lcom/tennistrack/app/Routes;", "", "()V", "LOGIN", "", "MATCH_LIST", "SETTINGS", "STREAM", "STREAM_NO_MATCH", "stream", "matchId", "app_debug"})
public final class Routes {
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String LOGIN = "login";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String MATCH_LIST = "matchList";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String STREAM = "stream/{matchId}";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String STREAM_NO_MATCH = "stream/null";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String SETTINGS = "settings";
    @org.jetbrains.annotations.NotNull()
    public static final com.tennistrack.app.Routes INSTANCE = null;
    
    private Routes() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String stream(@org.jetbrains.annotations.Nullable()
    java.lang.String matchId) {
        return null;
    }
}