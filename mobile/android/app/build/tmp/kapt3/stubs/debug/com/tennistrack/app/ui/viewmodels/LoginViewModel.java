package com.tennistrack.app.ui.viewmodels;

import androidx.lifecycle.ViewModel;
import com.tennistrack.app.data.repository.AuthRepository;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.SharingStarted;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00008\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0010\u0002\n\u0002\b\u0004\n\u0002\u0010\u000e\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u000f\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0006\u0010\u000e\u001a\u00020\u000fJ\u0006\u0010\u0010\u001a\u00020\u000fJ\u0006\u0010\u0011\u001a\u00020\u000fJ\u000e\u0010\u0012\u001a\u00020\u000f2\u0006\u0010\u0013\u001a\u00020\u0014J\u000e\u0010\u0015\u001a\u00020\u000f2\u0006\u0010\u0013\u001a\u00020\u0014R\u0014\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010\b\u001a\b\u0012\u0004\u0012\u00020\n0\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\b\u0010\u000bR\u0017\u0010\f\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000b\u00a8\u0006\u0016"}, d2 = {"Lcom/tennistrack/app/ui/viewmodels/LoginViewModel;", "Landroidx/lifecycle/ViewModel;", "authRepository", "Lcom/tennistrack/app/data/repository/AuthRepository;", "(Lcom/tennistrack/app/data/repository/AuthRepository;)V", "_uiState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/tennistrack/app/ui/viewmodels/LoginUiState;", "isLoggedIn", "Lkotlinx/coroutines/flow/StateFlow;", "", "()Lkotlinx/coroutines/flow/StateFlow;", "uiState", "getUiState", "clearError", "", "login", "logout", "onPasswordChanged", "value", "", "onUsernameChanged", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel()
public final class LoginViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull()
    private final com.tennistrack.app.data.repository.AuthRepository authRepository = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.tennistrack.app.ui.viewmodels.LoginUiState> _uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.tennistrack.app.ui.viewmodels.LoginUiState> uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> isLoggedIn = null;
    
    @javax.inject.Inject()
    public LoginViewModel(@org.jetbrains.annotations.NotNull()
    com.tennistrack.app.data.repository.AuthRepository authRepository) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.tennistrack.app.ui.viewmodels.LoginUiState> getUiState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> isLoggedIn() {
        return null;
    }
    
    public final void onUsernameChanged(@org.jetbrains.annotations.NotNull()
    java.lang.String value) {
    }
    
    public final void onPasswordChanged(@org.jetbrains.annotations.NotNull()
    java.lang.String value) {
    }
    
    public final void login() {
    }
    
    public final void logout() {
    }
    
    public final void clearError() {
    }
}