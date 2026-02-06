package com.tennistrack.app.streaming

data class ResolutionPreset(
    val label: String,
    val width: Int,
    val height: Int,
    val videoBitrate: Int,
    val audioBitrate: Int,
    val fps: Int
)

object CameraManager {

    val RESOLUTION_480P = ResolutionPreset(
        label = "480p",
        width = 854,
        height = 480,
        videoBitrate = 1_500_000,
        audioBitrate = 128_000,
        fps = 30
    )

    val RESOLUTION_720P = ResolutionPreset(
        label = "720p",
        width = 1280,
        height = 720,
        videoBitrate = 3_000_000,
        audioBitrate = 128_000,
        fps = 30
    )

    val RESOLUTION_1080P = ResolutionPreset(
        label = "1080p",
        width = 1920,
        height = 1080,
        videoBitrate = 5_000_000,
        audioBitrate = 192_000,
        fps = 30
    )

    val presets = listOf(RESOLUTION_480P, RESOLUTION_720P, RESOLUTION_1080P)

    fun getPresetByLabel(label: String): ResolutionPreset {
        return presets.find { it.label == label } ?: RESOLUTION_720P
    }

    fun getResolutionString(preset: ResolutionPreset): String {
        return "${preset.width}x${preset.height}"
    }
}
