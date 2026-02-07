package com.tennistrack.app.data.repository;

import com.tennistrack.app.data.api.TennisApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava"
})
public final class StreamRepository_Factory implements Factory<StreamRepository> {
  private final Provider<TennisApi> apiProvider;

  private final Provider<AuthRepository> authRepositoryProvider;

  public StreamRepository_Factory(Provider<TennisApi> apiProvider,
      Provider<AuthRepository> authRepositoryProvider) {
    this.apiProvider = apiProvider;
    this.authRepositoryProvider = authRepositoryProvider;
  }

  @Override
  public StreamRepository get() {
    return newInstance(apiProvider.get(), authRepositoryProvider.get());
  }

  public static StreamRepository_Factory create(Provider<TennisApi> apiProvider,
      Provider<AuthRepository> authRepositoryProvider) {
    return new StreamRepository_Factory(apiProvider, authRepositoryProvider);
  }

  public static StreamRepository newInstance(TennisApi api, AuthRepository authRepository) {
    return new StreamRepository(api, authRepository);
  }
}
