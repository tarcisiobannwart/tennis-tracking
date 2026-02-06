package com.tennistrack.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material.icons.filled.HighQuality
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.tennistrack.app.streaming.CameraManager
import com.tennistrack.app.ui.theme.CourtGreen
import com.tennistrack.app.ui.theme.DarkBackground
import com.tennistrack.app.ui.theme.DarkSurface
import com.tennistrack.app.ui.theme.DarkSurfaceVariant
import com.tennistrack.app.ui.theme.ErrorRed
import com.tennistrack.app.ui.theme.TextSecondary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onBack: () -> Unit,
    onLogout: () -> Unit
) {
    var serverUrl by remember { mutableStateOf("rtmp://localhost:1935/live") }
    var selectedResolution by remember { mutableStateOf("720p") }
    var audioBitrate by remember { mutableStateOf("128") }
    var showServerDialog by remember { mutableStateOf(false) }
    var showLogoutDialog by remember { mutableStateOf(false) }

    Scaffold(
        containerColor = DarkBackground,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Configuracoes",
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Voltar",
                            tint = Color.White
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = DarkSurface
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
        ) {
            // Server section
            SettingsSection(title = "Servidor") {
                SettingsItem(
                    icon = Icons.Default.Cloud,
                    title = "URL do Servidor",
                    subtitle = serverUrl,
                    onClick = { showServerDialog = true }
                )
            }

            // Streaming section
            SettingsSection(title = "Transmissao") {
                SettingsItem(
                    icon = Icons.Default.HighQuality,
                    title = "Resolucao Padrao",
                    subtitle = selectedResolution,
                    onClick = { }
                )

                // Resolution options
                CameraManager.presets.forEach { preset ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { selectedResolution = preset.label }
                            .padding(horizontal = 56.dp, vertical = 10.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = preset.label,
                                color = if (preset.label == selectedResolution) CourtGreen else Color.White,
                                fontSize = 14.sp
                            )
                            Text(
                                text = "${preset.width}x${preset.height} @ ${preset.videoBitrate / 1_000_000}Mbps",
                                color = TextSecondary,
                                fontSize = 12.sp
                            )
                        }
                        if (preset.label == selectedResolution) {
                            Icon(
                                imageVector = Icons.Default.Check,
                                contentDescription = "Selecionado",
                                tint = CourtGreen,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                    }
                }

                Divider(color = DarkSurfaceVariant, modifier = Modifier.padding(horizontal = 16.dp))

                SettingsItem(
                    icon = Icons.Default.MusicNote,
                    title = "Bitrate de Audio",
                    subtitle = "${audioBitrate} Kbps",
                    onClick = {
                        audioBitrate = when (audioBitrate) {
                            "64" -> "128"
                            "128" -> "192"
                            "192" -> "256"
                            else -> "64"
                        }
                    }
                )
            }

            // About section
            SettingsSection(title = "Sobre") {
                SettingsItem(
                    icon = Icons.Default.Info,
                    title = "TennisTrack Camera",
                    subtitle = "Versao 1.0.0",
                    onClick = { }
                )
            }

            // Logout
            SettingsSection(title = "Conta") {
                SettingsItem(
                    icon = Icons.Default.Logout,
                    title = "Sair",
                    subtitle = "Encerrar sessao",
                    titleColor = ErrorRed,
                    onClick = { showLogoutDialog = true }
                )
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }

    // Server URL dialog
    if (showServerDialog) {
        var tempUrl by remember { mutableStateOf(serverUrl) }
        AlertDialog(
            onDismissRequest = { showServerDialog = false },
            containerColor = DarkSurface,
            title = {
                Text("URL do Servidor RTMP", color = Color.White)
            },
            text = {
                OutlinedTextField(
                    value = tempUrl,
                    onValueChange = { tempUrl = it },
                    label = { Text("URL RTMP") },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = CourtGreen,
                        unfocusedBorderColor = TextSecondary.copy(alpha = 0.5f),
                        focusedLabelColor = CourtGreen,
                        cursorColor = CourtGreen
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        serverUrl = tempUrl
                        showServerDialog = false
                    }
                ) {
                    Text("Salvar", color = CourtGreen)
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showServerDialog = false }
                ) {
                    Text("Cancelar", color = TextSecondary)
                }
            }
        )
    }

    // Logout confirmation dialog
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            containerColor = DarkSurface,
            title = {
                Text("Sair da Conta", color = Color.White)
            },
            text = {
                Text(
                    "Deseja realmente encerrar sua sessao?",
                    color = TextSecondary
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showLogoutDialog = false
                        onLogout()
                    }
                ) {
                    Text("Sair", color = ErrorRed)
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showLogoutDialog = false }
                ) {
                    Text("Cancelar", color = TextSecondary)
                }
            }
        )
    }
}

@Composable
private fun SettingsSection(
    title: String,
    content: @Composable () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = title.uppercase(),
            color = CourtGreen,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 1.sp,
            modifier = Modifier.padding(start = 16.dp, top = 24.dp, bottom = 8.dp)
        )

        content()
    }
}

@Composable
private fun SettingsItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    titleColor: Color = Color.White,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = TextSecondary,
            modifier = Modifier.size(24.dp)
        )

        Spacer(modifier = Modifier.width(16.dp))

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                color = titleColor,
                fontSize = 16.sp
            )
            Text(
                text = subtitle,
                color = TextSecondary,
                fontSize = 13.sp
            )
        }
    }
}
