package com.cope.companion

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class ClipboardSync(
    context: Context,
    private val bridge: CopeBridge
) {
    private val appContext = context.applicationContext
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var job: Job? = null
    @Volatile
    private var lastSent: String? = null
    @Volatile
    var enabled: Boolean = false

    fun start() {
        if (job?.isActive == true) return
        job = scope.launch {
            val cm = appContext.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            while (isActive) {
                if (enabled && bridge.isConnected()) {
                    val text = cm.primaryClip
                        ?.takeIf { it.itemCount > 0 }
                        ?.getItemAt(0)
                        ?.coerceToText(appContext)
                        ?.toString()
                    if (!text.isNullOrEmpty() && text != lastSent) {
                        lastSent = text
                        bridge.sendClipboard(text)
                    }
                }
                delay(5_000)
            }
        }
    }

    fun stop() {
        job?.cancel()
        job = null
    }

    fun writeFromPc(content: String) {
        lastSent = content
        val cm = appContext.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText("COPE", content))
    }
}
