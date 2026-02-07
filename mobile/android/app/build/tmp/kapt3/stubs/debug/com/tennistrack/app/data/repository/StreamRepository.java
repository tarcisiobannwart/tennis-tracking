package com.tennistrack.app.data.repository;

import android.os.Build;
import com.tennistrack.app.data.api.TennisApi;
import com.tennistrack.app.data.model.CreateStreamRequest;
import com.tennistrack.app.data.model.DeviceInfo;
import com.tennistrack.app.data.model.MatchResponse;
import com.tennistrack.app.data.model.StreamResponse;
import javax.inject.Inject;
import javax.inject.Singleton;

@javax.inject.Singleton()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000>\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0005\n\u0002\u0010\u0002\n\u0002\b\u0004\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0005\b\u0007\u0018\u00002\u00020\u0001B\u0017\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J6\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\b2\b\u0010\n\u001a\u0004\u0018\u00010\u000b2\u0006\u0010\f\u001a\u00020\u000b2\u0006\u0010\r\u001a\u00020\u000bH\u0086@\u00f8\u0001\u0000\u00f8\u0001\u0001\u00a2\u0006\u0004\b\u000e\u0010\u000fJ$\u0010\u0010\u001a\b\u0012\u0004\u0012\u00020\u00110\b2\u0006\u0010\u0012\u001a\u00020\u000bH\u0086@\u00f8\u0001\u0000\u00f8\u0001\u0001\u00a2\u0006\u0004\b\u0013\u0010\u0014J\"\u0010\u0015\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00170\u00160\bH\u0086@\u00f8\u0001\u0000\u00f8\u0001\u0001\u00a2\u0006\u0004\b\u0018\u0010\u0019J\"\u0010\u001a\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\t0\u00160\bH\u0086@\u00f8\u0001\u0000\u00f8\u0001\u0001\u00a2\u0006\u0004\b\u001b\u0010\u0019R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u0082\u0002\u000b\n\u0002\b!\n\u0005\b\u00a1\u001e0\u0001\u00a8\u0006\u001c"}, d2 = {"Lcom/tennistrack/app/data/repository/StreamRepository;", "", "api", "Lcom/tennistrack/app/data/api/TennisApi;", "authRepository", "Lcom/tennistrack/app/data/repository/AuthRepository;", "(Lcom/tennistrack/app/data/api/TennisApi;Lcom/tennistrack/app/data/repository/AuthRepository;)V", "createStream", "Lkotlin/Result;", "Lcom/tennistrack/app/data/model/StreamResponse;", "matchId", "", "cameraLabel", "resolution", "createStream-BWLJW6A", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "deleteStream", "", "streamId", "deleteStream-gIAlu-s", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getMatches", "", "Lcom/tennistrack/app/data/model/MatchResponse;", "getMatches-IoAF18A", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getStreams", "getStreams-IoAF18A", "app_debug"})
public final class StreamRepository {
    @org.jetbrains.annotations.NotNull()
    private final com.tennistrack.app.data.api.TennisApi api = null;
    @org.jetbrains.annotations.NotNull()
    private final com.tennistrack.app.data.repository.AuthRepository authRepository = null;
    
    @javax.inject.Inject()
    public StreamRepository(@org.jetbrains.annotations.NotNull()
    com.tennistrack.app.data.api.TennisApi api, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.data.repository.AuthRepository authRepository) {
        super();
    }
}