package com.tennistrack.app.ui.viewmodels;

import androidx.lifecycle.SavedStateHandle;
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
public final class StreamViewModel_Factory implements Factory<StreamViewModel> {
  private final Provider<StreamRepository> streamRepositoryProvider;

  private final Provider<SavedStateHandle> savedStateHandleProvider;

  public StreamViewModel_Factory(Provider<StreamRepository> streamRepositoryProvider,
      Provider<SavedStateHandle> savedStateHandleProvider) {
    this.streamRepositoryProvider = streamRepositoryProvider;
    this.savedStateHandleProvider = savedStateHandleProvider;
  }

  @Override
  public StreamViewModel get() {
    return newInstance(streamRepositoryProvider.get(), savedStateHandleProvider.get());
  }

  public static StreamViewModel_Factory create(Provider<StreamRepository> streamRepositoryProvider,
      Provider<SavedStateHandle> savedStateHandleProvider) {
    return new StreamViewModel_Factory(streamRepositoryProvider, savedStateHandleProvider);
  }

  public static StreamViewModel newInstance(StreamRepository streamRepository,
      SavedStateHandle savedStateHandle) {
    return new StreamViewModel(streamRepository, savedStateHandle);
  }
}
