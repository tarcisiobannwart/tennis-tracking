package com.tennistrack.app.data.model

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    @SerializedName("username") val username: String,
    @SerializedName("password") val password: String
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    @SerializedName("user_id") val userId: String?,
    @SerializedName("username") val username: String?
)

data class StreamResponse(
    @SerializedName("id") val id: String,
    @SerializedName("stream_key") val streamKey: String,
    @SerializedName("rtmp_url") val rtmpUrl: String,
    @SerializedName("hls_url") val hlsUrl: String?,
    @SerializedName("status") val status: String,
    @SerializedName("match_id") val matchId: String?,
    @SerializedName("camera_label") val cameraLabel: String?,
    @SerializedName("created_at") val createdAt: String?
)

data class StreamListResponse(
    @SerializedName("streams") val streams: List<StreamResponse>,
    @SerializedName("total") val total: Int
)

data class CreateStreamRequest(
    @SerializedName("match_id") val matchId: String?,
    @SerializedName("camera_label") val cameraLabel: String,
    @SerializedName("device_info") val deviceInfo: DeviceInfo
)

data class DeviceInfo(
    @SerializedName("model") val model: String,
    @SerializedName("os_version") val osVersion: String,
    @SerializedName("app_version") val appVersion: String,
    @SerializedName("resolution") val resolution: String
)

data class MatchResponse(
    @SerializedName("id") val id: String,
    @SerializedName("player1_name") val player1Name: String,
    @SerializedName("player2_name") val player2Name: String,
    @SerializedName("score") val score: String?,
    @SerializedName("surface") val surface: String?,
    @SerializedName("tournament") val tournament: String?,
    @SerializedName("date") val date: String?,
    @SerializedName("status") val status: String,
    @SerializedName("streams_count") val streamsCount: Int?
)
