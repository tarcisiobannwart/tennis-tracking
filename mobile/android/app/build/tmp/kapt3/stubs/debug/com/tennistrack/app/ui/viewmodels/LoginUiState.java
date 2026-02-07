package com.tennistrack.app.ui.viewmodels;

import androidx.lifecycle.ViewModel;
import com.tennistrack.app.data.repository.AuthRepository;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.SharingStarted;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\"\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0012\n\u0002\u0010\b\n\u0002\b\u0002\b\u0086\b\u0018\u00002\u00020\u0001B9\u0012\b\b\u0002\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0004\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0005\u001a\u00020\u0006\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003\u0012\b\b\u0002\u0010\b\u001a\u00020\u0006\u00a2\u0006\u0002\u0010\tJ\t\u0010\u0010\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0011\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0012\u001a\u00020\u0006H\u00c6\u0003J\u000b\u0010\u0013\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\t\u0010\u0014\u001a\u00020\u0006H\u00c6\u0003J=\u0010\u0015\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00032\b\b\u0002\u0010\u0005\u001a\u00020\u00062\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u00032\b\b\u0002\u0010\b\u001a\u00020\u0006H\u00c6\u0001J\u0013\u0010\u0016\u001a\u00020\u00062\b\u0010\u0017\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u0018\u001a\u00020\u0019H\u00d6\u0001J\t\u0010\u001a\u001a\u00020\u0003H\u00d6\u0001R\u0013\u0010\u0007\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u000bR\u0011\u0010\u0005\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0005\u0010\fR\u0011\u0010\b\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\fR\u0011\u0010\u0004\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000bR\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u000b\u00a8\u0006\u001b"}, d2 = {"Lcom/tennistrack/app/ui/viewmodels/LoginUiState;", "", "username", "", "password", "isLoading", "", "errorMessage", "loginSuccess", "(Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Z)V", "getErrorMessage", "()Ljava/lang/String;", "()Z", "getLoginSuccess", "getPassword", "getUsername", "component1", "component2", "component3", "component4", "component5", "copy", "equals", "other", "hashCode", "", "toString", "app_debug"})
public final class LoginUiState {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String username = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String password = null;
    private final boolean isLoading = false;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String errorMessage = null;
    private final boolean loginSuccess = false;
    
    public LoginUiState(@org.jetbrains.annotations.NotNull()
    java.lang.String username, @org.jetbrains.annotations.NotNull()
    java.lang.String password, boolean isLoading, @org.jetbrains.annotations.Nullable()
    java.lang.String errorMessage, boolean loginSuccess) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getUsername() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getPassword() {
        return null;
    }
    
    public final boolean isLoading() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getErrorMessage() {
        return null;
    }
    
    public final boolean getLoginSuccess() {
        return false;
    }
    
    public LoginUiState() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component1() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component2() {
        return null;
    }
    
    public final boolean component3() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component4() {
        return null;
    }
    
    public final boolean component5() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.tennistrack.app.ui.viewmodels.LoginUiState copy(@org.jetbrains.annotations.NotNull()
    java.lang.String username, @org.jetbrains.annotations.NotNull()
    java.lang.String password, boolean isLoading, @org.jetbrains.annotations.Nullable()
    java.lang.String errorMessage, boolean loginSuccess) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}