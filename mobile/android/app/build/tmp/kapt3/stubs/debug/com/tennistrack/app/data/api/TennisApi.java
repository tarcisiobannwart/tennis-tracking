package com.tennistrack.app.data.api;

import com.tennistrack.app.data.model.CreateStreamRequest;
import com.tennistrack.app.data.model.LoginRequest;
import com.tennistrack.app.data.model.LoginResponse;
import com.tennistrack.app.data.model.MatchResponse;
import com.tennistrack.app.data.model.StreamListResponse;
import com.tennistrack.app.data.model.StreamResponse;
import retrofit2.Response;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.Header;
import retrofit2.http.POST;
import retrofit2.http.Path;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000H\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\bf\u0018\u00002\u00020\u0001J(\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u00062\b\b\u0001\u0010\u0007\u001a\u00020\bH\u00a7@\u00a2\u0006\u0002\u0010\tJ(\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u000b0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u00062\b\b\u0001\u0010\f\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\rJ$\u0010\u000e\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00100\u000f0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u001e\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\u00130\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u001e\u0010\u0014\u001a\b\u0012\u0004\u0012\u00020\u00150\u00032\b\b\u0001\u0010\u0007\u001a\u00020\u0016H\u00a7@\u00a2\u0006\u0002\u0010\u0017\u00a8\u0006\u0018"}, d2 = {"Lcom/tennistrack/app/data/api/TennisApi;", "", "createStream", "Lretrofit2/Response;", "Lcom/tennistrack/app/data/model/StreamResponse;", "token", "", "request", "Lcom/tennistrack/app/data/model/CreateStreamRequest;", "(Ljava/lang/String;Lcom/tennistrack/app/data/model/CreateStreamRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "deleteStream", "", "streamId", "(Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getMatches", "", "Lcom/tennistrack/app/data/model/MatchResponse;", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getStreams", "Lcom/tennistrack/app/data/model/StreamListResponse;", "login", "Lcom/tennistrack/app/data/model/LoginResponse;", "Lcom/tennistrack/app/data/model/LoginRequest;", "(Lcom/tennistrack/app/data/model/LoginRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public abstract interface TennisApi {
    
    @retrofit2.http.POST(value = "api/auth/login")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object login(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.data.model.LoginRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.tennistrack.app.data.model.LoginResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/streams")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getStreams(@retrofit2.http.Header(value = "Authorization")
    @org.jetbrains.annotations.NotNull()
    java.lang.String token, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.tennistrack.app.data.model.StreamListResponse>> $completion);
    
    @retrofit2.http.POST(value = "api/streams")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object createStream(@retrofit2.http.Header(value = "Authorization")
    @org.jetbrains.annotations.NotNull()
    java.lang.String token, @retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.data.model.CreateStreamRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.tennistrack.app.data.model.StreamResponse>> $completion);
    
    @retrofit2.http.DELETE(value = "api/streams/{id}")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object deleteStream(@retrofit2.http.Header(value = "Authorization")
    @org.jetbrains.annotations.NotNull()
    java.lang.String token, @retrofit2.http.Path(value = "id")
    @org.jetbrains.annotations.NotNull()
    java.lang.String streamId, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<kotlin.Unit>> $completion);
    
    @retrofit2.http.GET(value = "api/matches")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getMatches(@retrofit2.http.Header(value = "Authorization")
    @org.jetbrains.annotations.NotNull()
    java.lang.String token, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<java.util.List<com.tennistrack.app.data.model.MatchResponse>>> $completion);
}