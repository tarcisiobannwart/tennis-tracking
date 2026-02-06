package com.tennistrack.app.data.api

import com.tennistrack.app.data.model.CreateStreamRequest
import com.tennistrack.app.data.model.LoginRequest
import com.tennistrack.app.data.model.LoginResponse
import com.tennistrack.app.data.model.MatchResponse
import com.tennistrack.app.data.model.StreamListResponse
import com.tennistrack.app.data.model.StreamResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.Path

interface TennisApi {

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @GET("api/streams")
    suspend fun getStreams(
        @Header("Authorization") token: String
    ): Response<StreamListResponse>

    @POST("api/streams")
    suspend fun createStream(
        @Header("Authorization") token: String,
        @Body request: CreateStreamRequest
    ): Response<StreamResponse>

    @DELETE("api/streams/{id}")
    suspend fun deleteStream(
        @Header("Authorization") token: String,
        @Path("id") streamId: String
    ): Response<Unit>

    @GET("api/matches")
    suspend fun getMatches(
        @Header("Authorization") token: String
    ): Response<List<MatchResponse>>
}
