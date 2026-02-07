package com.tennistrack.app.ui.components;

import androidx.compose.animation.core.RepeatMode;
import androidx.compose.foundation.layout.Arrangement;
import androidx.compose.runtime.Composable;
import androidx.compose.ui.Alignment;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.text.font.FontWeight;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0007\b\u0086\u0081\u0002\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005j\u0002\b\u0006j\u0002\b\u0007\u00a8\u0006\b"}, d2 = {"Lcom/tennistrack/app/ui/components/ConnectionState;", "", "(Ljava/lang/String;I)V", "IDLE", "CONNECTING", "LIVE", "DISCONNECTED", "ERROR", "app_debug"})
public enum ConnectionState {
    /*public static final*/ IDLE /* = new IDLE() */,
    /*public static final*/ CONNECTING /* = new CONNECTING() */,
    /*public static final*/ LIVE /* = new LIVE() */,
    /*public static final*/ DISCONNECTED /* = new DISCONNECTED() */,
    /*public static final*/ ERROR /* = new ERROR() */;
    
    ConnectionState() {
    }
    
    @org.jetbrains.annotations.NotNull()
    public static kotlin.enums.EnumEntries<com.tennistrack.app.ui.components.ConnectionState> getEntries() {
        return null;
    }
}