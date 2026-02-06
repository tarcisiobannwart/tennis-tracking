package com.tennistrack.app.data.repository

import android.os.Build
import com.tennistrack.app.data.api.TennisApi
import com.tennistrack.app.data.model.CreateStreamRequest
import com.tennistrack.app.data.model.DeviceInfo
import com.tennistrack.app.data.model.MatchResponse
import com.tennistrack.app.data.model.StreamResponse
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class StreamRepository @Inject constructor(
    private val api: TennisApi,
    private val authRepository: AuthRepository
) {
    suspend fun getStreams(): Result<List<StreamResponse>> {
        return try {
            val token = authRepository.getAuthHeader()
                ?: return Result.failure(Exception("Nao autenticado"))
            val response = api.getStreams(token)
            if (response.isSuccessful) {
                Result.success(response.body()?.streams ?: emptyList())
            } else {
                Result.failure(Exception("Erro ao buscar streams: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Erro de conexao: ${e.message}"))
        }
    }

    suspend fun createStream(
        matchId: String?,
        cameraLabel: String,
        resolution: String
    ): Result<StreamResponse> {
        return try {
            val token = authRepository.getAuthHeader()
                ?: return Result.failure(Exception("Nao autenticado"))

            val deviceInfo = DeviceInfo(
                model = "${Build.MANUFACTURER} ${Build.MODEL}",
                osVersion = "Android ${Build.VERSION.RELEASE}",
                appVersion = "1.0.0",
                resolution = resolution
            )

            val request = CreateStreamRequest(
                matchId = matchId,
                cameraLabel = cameraLabel,
                deviceInfo = deviceInfo
            )

            val response = api.createStream(token, request)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Erro ao criar stream: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Erro de conexao: ${e.message}"))
        }
    }

    suspend fun deleteStream(streamId: String): Result<Unit> {
        return try {
            val token = authRepository.getAuthHeader()
                ?: return Result.failure(Exception("Nao autenticado"))
            val response = api.deleteStream(token, streamId)
            if (response.isSuccessful) {
                Result.success(Unit)
            } else {
                Result.failure(Exception("Erro ao encerrar stream: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Erro de conexao: ${e.message}"))
        }
    }

    suspend fun getMatches(): Result<List<MatchResponse>> {
        return try {
            val token = authRepository.getAuthHeader()
                ?: return Result.failure(Exception("Nao autenticado"))
            val response = api.getMatches(token)
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("Erro ao buscar partidas: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Erro de conexao: ${e.message}"))
        }
    }
}
