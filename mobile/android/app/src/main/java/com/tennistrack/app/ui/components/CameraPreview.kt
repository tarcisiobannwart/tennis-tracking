package com.tennistrack.app.ui.components

import android.view.SurfaceHolder
import android.view.SurfaceView
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import com.tennistrack.app.streaming.RtmpStreamer

@Composable
fun CameraPreview(
    modifier: Modifier = Modifier,
    streamer: RtmpStreamer,
    onSurfaceReady: (SurfaceView) -> Unit
) {
    val context = LocalContext.current
    val surfaceView = remember { SurfaceView(context) }

    DisposableEffect(surfaceView) {
        val callback = object : SurfaceHolder.Callback {
            override fun surfaceCreated(holder: SurfaceHolder) {
                streamer.initCamera(surfaceView)
                onSurfaceReady(surfaceView)
            }

            override fun surfaceChanged(
                holder: SurfaceHolder,
                format: Int,
                width: Int,
                height: Int
            ) {
                // Reconfiguracao se necessario
            }

            override fun surfaceDestroyed(holder: SurfaceHolder) {
                streamer.stopStream()
                streamer.stopPreview()
            }
        }

        surfaceView.holder.addCallback(callback)

        onDispose {
            surfaceView.holder.removeCallback(callback)
            streamer.release()
        }
    }

    AndroidView(
        factory = { surfaceView },
        modifier = modifier
    )
}
