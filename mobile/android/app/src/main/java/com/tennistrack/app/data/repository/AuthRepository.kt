package com.tennistrack.app.data.repository

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import com.tennistrack.app.data.api.TennisApi
import com.tennistrack.app.data.model.LoginRequest
import com.tennistrack.app.data.model.LoginResponse
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val api: TennisApi,
    private val dataStore: DataStore<Preferences>
) {
    companion object {
        private val KEY_ACCESS_TOKEN = stringPreferencesKey("access_token")
        private val KEY_TOKEN_TYPE = stringPreferencesKey("token_type")
        private val KEY_USERNAME = stringPreferencesKey("username")
        private val KEY_USER_ID = stringPreferencesKey("user_id")
    }

    val isLoggedIn: Flow<Boolean> = dataStore.data.map { prefs ->
        prefs[KEY_ACCESS_TOKEN] != null
    }

    val username: Flow<String?> = dataStore.data.map { prefs ->
        prefs[KEY_USERNAME]
    }

    suspend fun login(username: String, password: String): Result<LoginResponse> {
        return try {
            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful) {
                val body = response.body()!!
                saveToken(body)
                Result.success(body)
            } else {
                val errorMsg = when (response.code()) {
                    401 -> "Credenciais invalidas"
                    422 -> "Dados de login invalidos"
                    else -> "Erro ao fazer login: ${response.code()}"
                }
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            Result.failure(Exception("Erro de conexao: ${e.message}"))
        }
    }

    suspend fun logout() {
        dataStore.edit { prefs ->
            prefs.remove(KEY_ACCESS_TOKEN)
            prefs.remove(KEY_TOKEN_TYPE)
            prefs.remove(KEY_USERNAME)
            prefs.remove(KEY_USER_ID)
        }
    }

    suspend fun getAuthHeader(): String? {
        val prefs = dataStore.data.first()
        val token = prefs[KEY_ACCESS_TOKEN] ?: return null
        val type = prefs[KEY_TOKEN_TYPE] ?: "Bearer"
        return "$type $token"
    }

    private suspend fun saveToken(loginResponse: LoginResponse) {
        dataStore.edit { prefs ->
            prefs[KEY_ACCESS_TOKEN] = loginResponse.accessToken
            prefs[KEY_TOKEN_TYPE] = loginResponse.tokenType
            loginResponse.username?.let { prefs[KEY_USERNAME] = it }
            loginResponse.userId?.let { prefs[KEY_USER_ID] = it }
        }
    }
}
