package com.cope.companion

import android.util.Base64
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.Socket

class CopeBridge(
    private val onStatus: (String) -> Unit,
    private val onMessage: (String) -> Unit,
    private val onClipboard: (String) -> Unit = {}
) {
    private var socket: Socket? = null
    private var writer: PrintWriter? = null
    private var reader: BufferedReader? = null
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var pingJob: Job? = null

    @Volatile
    var lastError: String? = null
        private set

    fun connect(host: String, port: Int) {
        scope.launch {
            try {
                disconnectInternal()
                socket = Socket(host, port)
                writer = PrintWriter(socket!!.getOutputStream(), true)
                reader = BufferedReader(InputStreamReader(socket!!.getInputStream()))
                instance = this@CopeBridge
                onStatus("Connected to COPE at $host:$port")
                startPingLoop()
                receiveLoop()
            } catch (e: Exception) {
                lastError = e.message
                onStatus("Connection failed: ${e.message}")
            }
        }
    }

    fun disconnect() {
        scope.launch {
            disconnectInternal()
            onStatus("Disconnected.")
        }
    }

    private fun disconnectInternal() {
        pingJob?.cancel()
        pingJob = null
        try {
            socket?.close()
        } catch (_: Exception) {
        }
        socket = null
        writer = null
        reader = null
        if (instance === this) {
            instance = null
        }
    }

    fun isConnected() = socket?.isConnected == true && socket?.isClosed == false

    fun send(payload: JSONObject) {
        scope.launch {
            try {
                synchronized(this@CopeBridge) {
                    writer?.println(payload.toString())
                }
            } catch (_: Exception) {
            }
        }
    }

    fun sendVoiceCommand(text: String) {
        send(JSONObject().apply {
            put("type", "voice_command")
            put("text", text)
        })
    }

    fun sendNotification(app: String, title: String, body: String) {
        send(JSONObject().apply {
            put("type", "notification")
            put("app", app)
            put("title", title)
            put("body", body)
        })
    }

    fun sendClipboard(content: String) {
        send(JSONObject().apply {
            put("type", "clipboard")
            put("content", content)
        })
    }

    fun sendLocation(lat: Double, lon: Double) {
        send(JSONObject().apply {
            put("type", "location")
            put("lat", lat)
            put("lon", lon)
        })
    }

    fun sendFile(filename: String, bytes: ByteArray) {
        send(JSONObject().apply {
            put("type", "file")
            put("filename", filename)
            put("data", Base64.encodeToString(bytes, Base64.NO_WRAP))
        })
    }

    private fun startPingLoop() {
        pingJob = scope.launch {
            while (isConnected()) {
                send(JSONObject().put("type", "ping"))
                delay(10_000)
            }
        }
    }

    private suspend fun receiveLoop() {
        while (isConnected()) {
            try {
                val line = reader?.readLine() ?: break
                val payload = JSONObject(line)
                when (payload.optString("type")) {
                    "pong" -> { /* keep-alive confirmed */ }
                    "notification" -> onMessage("${payload.optString("title")}: ${payload.optString("body")}")
                    "clipboard" -> {
                        val content = payload.optString("content")
                        if (content.isNotEmpty()) {
                            onClipboard(content)
                        }
                    }
                }
            } catch (_: Exception) {
                break
            }
        }
        onStatus("Disconnected.")
    }

    companion object {
        @Volatile
        var instance: CopeBridge? = null
            private set
    }
}
