package com.cope.companion

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.core.app.NotificationCompat
import kotlin.math.sqrt

class MicService : Service() {
    private val mainHandler = Handler(Looper.getMainLooper())
    private var clapThread: Thread? = null
    @Volatile
    private var running = false
    @Volatile
    private var listeningSpeech = false
    private var speech: SpeechRecognizer? = null
    private var lastClap = 0L

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> {
                stopSelf()
                return START_NOT_STICKY
            }
            ACTION_LISTEN -> startSpeechRecognition()
        }
        startForeground(NOTIF_ID, buildNotification())
        running = true
        startClapLoop()
        return START_STICKY
    }

    override fun onDestroy() {
        running = false
        clapThread = null
        mainHandler.post {
            speech?.destroy()
            speech = null
        }
        super.onDestroy()
    }

    private fun startClapLoop() {
        if (clapThread?.isAlive == true) return
        clapThread = Thread({
            val minBuf = AudioRecord.getMinBufferSize(
                RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )
            val recorder = try {
                AudioRecord(
                    MediaRecorder.AudioSource.MIC,
                    RATE,
                    AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT,
                    minBuf * 2
                )
            } catch (_: SecurityException) {
                return@Thread
            }
            if (recorder.state != AudioRecord.STATE_INITIALIZED) {
                recorder.release()
                return@Thread
            }
            val buf = ShortArray(512)
            recorder.startRecording()
            try {
                while (running) {
                    if (listeningSpeech || !voiceEnabled()) {
                        Thread.sleep(200)
                        continue
                    }
                    val n = recorder.read(buf, 0, buf.size)
                    if (n <= 0) continue
                    var sum = 0.0
                    for (i in 0 until n) {
                        val s = buf[i].toDouble()
                        sum += s * s
                    }
                    val rms = sqrt(sum / n)
                    if (rms > CLAP_THRESHOLD) {
                        val now = System.currentTimeMillis()
                        val dt = now - lastClap
                        if (dt in 200..800) {
                            lastClap = 0L
                            startSpeechRecognition()
                        } else {
                            lastClap = now
                        }
                    }
                }
            } finally {
                try {
                    recorder.stop()
                } catch (_: Exception) {
                }
                recorder.release()
            }
        }, "cope-clap").also { it.isDaemon = true; it.start() }
    }

    private fun startSpeechRecognition() {
        if (!voiceEnabled()) return
        mainHandler.post {
            if (listeningSpeech) return@post
            if (!SpeechRecognizer.isRecognitionAvailable(this)) return@post
            listeningSpeech = true
            val recognizer = speech ?: SpeechRecognizer.createSpeechRecognizer(this).also { speech = it }
            recognizer.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {}
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}
                override fun onError(error: Int) {
                    listeningSpeech = false
                }
                override fun onResults(results: Bundle?) {
                    val text = results
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        ?.trim()
                        .orEmpty()
                    if (text.isNotEmpty()) {
                        CopeBridge.instance?.sendVoiceCommand(text)
                    }
                    listeningSpeech = false
                }
                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            }
            recognizer.startListening(intent)
        }
    }

    private fun voiceEnabled(): Boolean {
        return getSharedPreferences("cope_companion", Context.MODE_PRIVATE)
            .getBoolean("voice_commands", false)
    }

    private fun buildNotification(): Notification {
        val nm = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            nm.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, getString(R.string.mic_channel), NotificationManager.IMPORTANCE_LOW)
            )
        }
        val launch = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.app_name))
            .setContentText(getString(R.string.mic_notification))
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(launch)
            .setOngoing(true)
            .build()
    }

    companion object {
        const val ACTION_LISTEN = "com.cope.companion.LISTEN"
        const val ACTION_STOP = "com.cope.companion.STOP"
        private const val CHANNEL_ID = "cope_mic"
        private const val NOTIF_ID = 9876
        private const val RATE = 8000
        private const val CLAP_THRESHOLD = 8000.0

        fun listenIntent(context: Context): Intent =
            Intent(context, MicService::class.java).setAction(ACTION_LISTEN)
    }
}
