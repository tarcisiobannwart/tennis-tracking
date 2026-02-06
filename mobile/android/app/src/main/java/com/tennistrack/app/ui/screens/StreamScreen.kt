package com.tennistrack.app.ui.screens

import android.app.Activity
import android.content.pm.ActivityInfo
import android.view.SurfaceView
import android.view.View
import android.view.WindowManager
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Snackbar
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.hilt.navigation.compose.hiltViewModel
import com.tennistrack.app.streaming.CameraManager
import com.tennistrack.app.streaming.RtmpStreamer
import com.tennistrack.app.ui.components.CameraPreview
import com.tennistrack.app.ui.components.ConnectionState
import com.tennistrack.app.ui.components.ConnectionStatusBadge
import com.tennistrack.app.ui.components.StreamControls
import com.tennistrack.app.ui.theme.DarkSurfaceVariant
import com.tennistrack.app.ui.theme.ErrorRed
import com.tennistrack.app.ui.theme.TextSecondary
import com.tennistrack.app.ui.viewmodels.StreamViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun StreamScreen(
    onBack: () -> Unit,
    viewModel: StreamViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val activity = context as? Activity
    val uiState by viewModel.uiState.collectAsState()
    val scope = rememberCoroutineScope()
    var showControls by remember { mutableStateOf(true) }
    val streamer = remember { RtmpStreamer() }

    // Force landscape and immersive mode
    DisposableEffect(Unit) {
        val originalOrientation = activity?.requestedOrientation
        activity?.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE

        activity?.window?.let { window ->
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            WindowCompat.setDecorFitsSystemWindows(window, false)
            val controller = WindowInsetsControllerCompat(window, window.decorView)
            controller.hide(WindowInsetsCompat.Type.systemBars())
            controller.systemBarsBehavior =
                WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }

        onDispose {
            activity?.requestedOrientation =
                originalOrientation ?: ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
            activity?.window?.let { window ->
                window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                WindowCompat.setDecorFitsSystemWindows(window, true)
                val controller = WindowInsetsControllerCompat(window, window.decorView)
                controller.show(WindowInsetsCompat.Type.systemBars())
            }
            streamer.release()
        }
    }

    // Setup streamer callbacks
    LaunchedEffect(streamer) {
        streamer.onConnectionSuccess = {
            viewModel.onConnectionSuccess()
        }
        streamer.onConnectionFailed = { reason ->
            viewModel.onConnectionFailed(reason)
        }
        streamer.onDisconnected = {
            viewModel.onDisconnected()
        }
        streamer.onNewBitrateCallback = { bitrate ->
            viewModel.onBitrateUpdate(bitrate)
        }
    }

    // Auto-hide controls after 5 seconds when streaming
    LaunchedEffect(showControls, uiState.isStreaming) {
        if (showControls && uiState.isStreaming) {
            delay(5000)
            showControls = false
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null
            ) {
                showControls = !showControls
            }
    ) {
        // Camera preview
        CameraPreview(
            modifier = Modifier.fillMaxSize(),
            streamer = streamer,
            onSurfaceReady = { surfaceView ->
                streamer.startPreview(uiState.currentResolution)
            }
        )

        // Overlay controls
        AnimatedVisibility(
            visible = showControls,
            enter = fadeIn(),
            exit = fadeOut()
        ) {
            Box(modifier = Modifier.fillMaxSize()) {
                // Top gradient overlay
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(100.dp)
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(
                                    Color.Black.copy(alpha = 0.7f),
                                    Color.Transparent
                                )
                            )
                        )
                        .align(Alignment.TopCenter)
                )

                // Top bar: back button, connection status, camera label, bitrate, timer
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp)
                        .align(Alignment.TopCenter),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Left section: back + status
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        IconButton(onClick = {
                            if (uiState.isStreaming) {
                                streamer.stopStream()
                                viewModel.onStreamStopped()
                            }
                            onBack()
                        }) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = "Voltar",
                                tint = Color.White,
                                modifier = Modifier.size(24.dp)
                            )
                        }

                        ConnectionStatusBadge(state = uiState.connectionState)

                        Spacer(modifier = Modifier.width(12.dp))

                        // Camera label
                        Row(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(DarkSurfaceVariant.copy(alpha = 0.7f))
                                .padding(horizontal = 10.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.Videocam,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = uiState.cameraLabel,
                                color = Color.White,
                                fontSize = 12.sp
                            )
                        }
                    }

                    // Right section: bitrate + timer
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        if (uiState.isStreaming) {
                            // Bitrate
                            Row(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(DarkSurfaceVariant.copy(alpha = 0.7f))
                                    .padding(horizontal = 10.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Speed,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = viewModel.formatBitrate(),
                                    color = Color.White,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }

                            // Duration timer
                            Row(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(Color.Red.copy(alpha = 0.7f))
                                    .padding(horizontal = 10.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Timer,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = viewModel.formatDuration(),
                                    color = Color.White,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }

                // Bottom gradient overlay
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(140.dp)
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(
                                    Color.Transparent,
                                    Color.Black.copy(alpha = 0.7f)
                                )
                            )
                        )
                        .align(Alignment.BottomCenter)
                )

                // Bottom controls
                StreamControls(
                    isStreaming = uiState.isStreaming,
                    isFlashOn = uiState.isFlashOn,
                    currentResolution = uiState.currentResolution.label,
                    onRecordClick = {
                        if (uiState.isStreaming) {
                            streamer.stopStream()
                            viewModel.onStreamStopped()
                        } else {
                            scope.launch {
                                viewModel.onStreamStarted()
                                val result = viewModel.createStream()
                                val rtmpUrl = uiState.streamResponse?.rtmpUrl
                                if (rtmpUrl != null) {
                                    streamer.startStream(rtmpUrl)
                                }
                            }
                        }
                    },
                    onSwitchCamera = {
                        streamer.switchCamera()
                    },
                    onToggleFlash = {
                        val isOn = streamer.toggleFlash()
                        viewModel.onFlashToggled(isOn)
                    },
                    onResolutionSelected = { label ->
                        val preset = CameraManager.getPresetByLabel(label)
                        streamer.setResolution(preset)
                        streamer.startPreview(preset)
                        viewModel.onResolutionChanged(label)
                    },
                    modifier = Modifier.align(Alignment.BottomCenter)
                )
            }
        }

        // Error snackbar
        AnimatedVisibility(
            visible = uiState.errorMessage != null,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(16.dp)
        ) {
            Snackbar(
                containerColor = ErrorRed,
                contentColor = Color.White,
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(text = uiState.errorMessage ?: "")
            }

            LaunchedEffect(uiState.errorMessage) {
                if (uiState.errorMessage != null) {
                    delay(4000)
                    viewModel.clearError()
                }
            }
        }
    }
}
