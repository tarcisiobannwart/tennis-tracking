package com.tennistrack.app.data.repository;

import androidx.datastore.core.DataStore;
import androidx.datastore.preferences.core.Preferences;
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
public final class AuthRepository_Factory implements Factory<AuthRepository> {
  private final Provider<TennisApi> apiProvider;

  private final Provider<DataStore<Preferences>> dataStoreProvider;

  public AuthRepository_Factory(Provider<TennisApi> apiProvider,
      Provider<DataStore<Preferences>> dataStoreProvider) {
    this.apiProvider = apiProvider;
    this.dataStoreProvider = dataStoreProvider;
  }

  @Override
  public AuthRepository get() {
    return newInstance(apiProvider.get(), dataStoreProvider.get());
  }

  public static AuthRepository_Factory create(Provider<TennisApi> apiProvider,
      Provider<DataStore<Preferences>> dataStoreProvider) {
    return new AuthRepository_Factory(apiProvider, dataStoreProvider);
  }

  public static AuthRepository newInstance(TennisApi api, DataStore<Preferences> dataStore) {
    return new AuthRepository(api, dataStore);
  }
}
