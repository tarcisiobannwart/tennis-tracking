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

@dagger.hilt.android.AndroidEntryPoint()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000*\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0011\n\u0002\u0010\u000e\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0012\u0010\t\u001a\u00020\n2\b\u0010\u000b\u001a\u0004\u0018\u00010\fH\u0014J\b\u0010\r\u001a\u00020\nH\u0002R\u001a\u0010\u0003\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00060\u00050\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0016\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005X\u0082\u0004\u00a2\u0006\u0004\n\u0002\u0010\b\u00a8\u0006\u000e"}, d2 = {"Lcom/tennistrack/app/MainActivity;", "Landroidx/activity/ComponentActivity;", "()V", "permissionLauncher", "Landroidx/activity/result/ActivityResultLauncher;", "", "", "requiredPermissions", "[Ljava/lang/String;", "onCreate", "", "savedInstanceState", "Landroid/os/Bundle;", "requestPermissionsIfNeeded", "app_debug"})
public final class MainActivity extends androidx.activity.ComponentActivity {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String[] requiredPermissions = {"android.permission.CAMERA", "android.permission.RECORD_AUDIO"};
    @org.jetbrains.annotations.NotNull()
    private final androidx.activity.result.ActivityResultLauncher<java.lang.String[]> permissionLauncher = null;
    
    public MainActivity() {
        super();
    }
    
    @java.lang.Override()
    protected void onCreate(@org.jetbrains.annotations.Nullable()
    android.os.Bundle savedInstanceState) {
    }
    
    private final void requestPermissionsIfNeeded() {
    }
}