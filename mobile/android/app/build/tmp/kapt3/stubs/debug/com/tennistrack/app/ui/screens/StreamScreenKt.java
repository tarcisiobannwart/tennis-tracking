package com.tennistrack.app.ui.screens;

import android.app.Activity;
import android.content.pm.ActivityInfo;
import android.view.SurfaceView;
import android.view.View;
import android.view.WindowManager;
import androidx.compose.foundation.layout.Arrangement;
import androidx.compose.material.icons.Icons;
import androidx.compose.runtime.Composable;
import androidx.compose.ui.Alignment;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.graphics.Brush;
import androidx.compose.ui.text.font.FontWeight;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.tennistrack.app.streaming.CameraManager;
import com.tennistrack.app.streaming.RtmpStreamer;
import com.tennistrack.app.ui.components.ConnectionState;
import com.tennistrack.app.ui.viewmodels.StreamViewModel;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000\u0014\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\u001a \u0010\u0000\u001a\u00020\u00012\f\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00010\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u0005H\u0007\u00a8\u0006\u0006"}, d2 = {"StreamScreen", "", "onBack", "Lkotlin/Function0;", "viewModel", "Lcom/tennistrack/app/ui/viewmodels/StreamViewModel;", "app_debug"})
public final class StreamScreenKt {
    
    @androidx.compose.runtime.Composable()
    public static final void StreamScreen(@org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onBack, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.ui.viewmodels.StreamViewModel viewModel) {
    }
}