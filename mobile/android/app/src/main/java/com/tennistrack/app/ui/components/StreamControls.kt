package com.tennistrack.app.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cameraswitch
import androidx.compose.material.icons.filled.FlashOff
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.tennistrack.app.streaming.CameraManager
import com.tennistrack.app.ui.theme.DarkSurfaceVariant
import com.tennistrack.app.ui.theme.LiveRed
import com.tennistrack.app.ui.theme.TextSecondary

@Composable
fun StreamControls(
    isStreaming: Boolean,
    isFlashOn: Boolean,
    currentResolution: String,
    onRecordClick: () -> Unit,
    onSwitchCamera: () -> Unit,
    onToggleFlash: () -> Unit,
    onResolutionSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var showQualityDropdown by remember { mutableStateOf(false) }

    val infiniteTransition = rememberInfiniteTransition(label = "recordPulse")
    val recordScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isStreaming) 1.15f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(600),
            repeatMode = RepeatMode.Reverse
        ),
        label = "recordScale"
    )

    val recordColor by animateColorAsState(
        targetValue = if (isStreaming) LiveRed else Color.White,
        label = "recordColor"
    )

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 24.dp, vertical = 16.dp),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Flash toggle
        ControlButton(
            onClick = onToggleFlash,
            icon = {
                Icon(
                    imageVector = if (isFlashOn) Icons.Default.FlashOn else Icons.Default.FlashOff,
                    contentDescription = "Flash",
                    tint = if (isFlashOn) Color.Yellow else Color.White,
                    modifier = Modifier.size(28.dp)
                )
            },
            label = "Flash"
        )

        // Camera switch
        ControlButton(
            onClick = onSwitchCamera,
            icon = {
                Icon(
                    imageVector = Icons.Default.Cameraswitch,
                    contentDescription = "Trocar Camera",
                    tint = Color.White,
                    modifier = Modifier.size(28.dp)
                )
            },
            label = "Trocar"
        )

        // Record button (center, larger)
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(72.dp)
                    .scale(if (isStreaming) recordScale else 1f)
                    .clip(CircleShape)
                    .border(3.dp, Color.White, CircleShape)
                    .background(
                        if (isStreaming) LiveRed.copy(alpha = 0.2f)
                        else Color.Transparent
                    )
                    .clickable { onRecordClick() },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = if (isStreaming) Icons.Default.Stop else Icons.Default.FiberManualRecord,
                    contentDescription = if (isStreaming) "Parar" else "Gravar",
                    tint = recordColor,
                    modifier = Modifier.size(if (isStreaming) 36.dp else 48.dp)
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = if (isStreaming) "PARAR" else "INICIAR",
                color = if (isStreaming) LiveRed else Color.White,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // Quality selector
        Box {
            ControlButton(
                onClick = { showQualityDropdown = true },
                icon = {
                    Text(
                        text = currentResolution,
                        color = Color.White,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                },
                label = "Qualidade"
            )

            DropdownMenu(
                expanded = showQualityDropdown,
                onDismissRequest = { showQualityDropdown = false },
                modifier = Modifier.background(DarkSurfaceVariant)
            ) {
                CameraManager.presets.forEach { preset ->
                    DropdownMenuItem(
                        text = {
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = preset.label,
                                    color = if (preset.label == currentResolution) Color.White else TextSecondary,
                                    fontWeight = if (preset.label == currentResolution) FontWeight.Bold else FontWeight.Normal
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "${preset.width}x${preset.height}",
                                    color = TextSecondary,
                                    fontSize = 12.sp
                                )
                            }
                        },
                        onClick = {
                            onResolutionSelected(preset.label)
                            showQualityDropdown = false
                        }
                    )
                }
            }
        }

        // Placeholder for symmetry
        Box(modifier = Modifier.size(56.dp))
    }
}

@Composable
private fun ControlButton(
    onClick: () -> Unit,
    icon: @Composable () -> Unit,
    label: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        IconButton(
            onClick = onClick,
            modifier = Modifier
                .size(56.dp)
                .clip(CircleShape)
                .background(Color.Black.copy(alpha = 0.4f))
        ) {
            icon()
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            color = Color.White.copy(alpha = 0.7f),
            fontSize = 10.sp
        )
    }
}
