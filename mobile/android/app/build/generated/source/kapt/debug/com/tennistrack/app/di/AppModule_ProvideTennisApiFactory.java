package com.tennistrack.app.di;

import com.tennistrack.app.data.api.TennisApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import retrofit2.Retrofit;

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
public final class AppModule_ProvideTennisApiFactory implements Factory<TennisApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideTennisApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public TennisApi get() {
    return provideTennisApi(retrofitProvider.get());
  }

  public static AppModule_ProvideTennisApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideTennisApiFactory(retrofitProvider);
  }

  public static TennisApi provideTennisApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideTennisApi(retrofit));
  }
}
