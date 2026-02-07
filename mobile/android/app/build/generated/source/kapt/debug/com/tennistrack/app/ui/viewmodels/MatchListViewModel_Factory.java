package com.tennistrack.app.ui.viewmodels;

import com.tennistrack.app.data.repository.StreamRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
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
public final class MatchListViewModel_Factory implements Factory<MatchListViewModel> {
  private final Provider<StreamRepository> streamRepositoryProvider;

  public MatchListViewModel_Factory(Provider<StreamRepository> streamRepositoryProvider) {
    this.streamRepositoryProvider = streamRepositoryProvider;
  }

  @Override
  public MatchListViewModel get() {
    return newInstance(streamRepositoryProvider.get());
  }

  public static MatchListViewModel_Factory create(
      Provider<StreamRepository> streamRepositoryProvider) {
    return new MatchListViewModel_Factory(streamRepositoryProvider);
  }

  public static MatchListViewModel newInstance(StreamRepository streamRepository) {
    return new MatchListViewModel(streamRepository);
  }
}
