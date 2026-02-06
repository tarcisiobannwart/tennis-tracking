# Retrofit
-keepattributes Signature
-keepattributes Exceptions
-keepattributes *Annotation*

-keep class com.tennistrack.app.data.model.** { *; }

-dontwarn javax.annotation.**

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# Gson
-keepattributes SerializedName
-keep class com.google.gson.** { *; }

# RootEncoder
-keep class com.pedro.** { *; }
-dontwarn com.pedro.**

# Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
