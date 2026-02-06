package com.tennistrack.app.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.tennistrack.app.ui.theme.ConnectingBlue
import com.tennistrack.app.ui.theme.DisconnectedGray
import com.tennistrack.app.ui.theme.LiveRed

enum class ConnectionState {
    IDLE,
    CONNECTING,
    LIVE,
    DISCONNECTED,
    ERROR
}

@Composable
fun ConnectionStatusBadge(
    state: ConnectionState,
    modifier: Modifier = Modifier
) {
    val backgroundColor by animateColorAsState(
        targetValue = when (state) {
            ConnectionState.IDLE -> DisconnectedGray.copy(alpha = 0.7f)
            ConnectionState.CONNECTING -> ConnectingBlue.copy(alpha = 0.8f)
            ConnectionState.LIVE -> LiveRed.copy(alpha = 0.9f)
            ConnectionState.DISCONNECTED -> DisconnectedGray.copy(alpha = 0.7f)
            ConnectionState.ERROR -> Color.Red.copy(alpha = 0.8f)
        },
        label = "bgColor"
    )

    val statusText = when (state) {
        ConnectionState.IDLE -> "PRONTO"
        ConnectionState.CONNECTING -> "CONECTANDO..."
        ConnectionState.LIVE -> "AO VIVO"
        ConnectionState.DISCONNECTED -> "DESCONECTADO"
        ConnectionState.ERROR -> "ERRO"
    }

    val dotColor = when (state) {
        ConnectionState.LIVE -> LiveRed
        ConnectionState.CONNECTING -> ConnectingBlue
        else -> DisconnectedGray
    }

    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (state == ConnectionState.LIVE) 0.3f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(800),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(20.dp))
            .background(backgroundColor)
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .alpha(if (state == ConnectionState.LIVE) pulseAlpha else 1f)
                .clip(CircleShape)
                .background(
                    when (state) {
                        ConnectionState.LIVE -> Color.White
                        ConnectionState.CONNECTING -> Color.White
                        else -> Color.White.copy(alpha = 0.5f)
                    }
                )
        )

        Text(
            text = statusText,
            color = Color.White,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            style = MaterialTheme.typography.labelSmall
        )
    }
}
