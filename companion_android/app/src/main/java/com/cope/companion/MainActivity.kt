package com.cope.companion

import android.Manifest
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.button.MaterialButton
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {
    private lateinit var prefs: SharedPreferences
    private lateinit var statusLabel: TextView
    private lateinit var messageLog: TextView
    private lateinit var ipInput: TextInputEditText
    private lateinit var portInput: TextInputEditText
    private lateinit var connectButton: MaterialButton
    private lateinit var speakButton: MaterialButton
    private lateinit var sendFileButton: MaterialButton
    private lateinit var voiceToggle: SwitchMaterial
    private lateinit var notificationToggle: SwitchMaterial
    private lateinit var clipboardToggle: SwitchMaterial
    private lateinit var locationToggle: SwitchMaterial

    private var bridge: CopeBridge? = null
    private var clipboardSync: ClipboardSync? = null
    private var locationTracker: LocationTracker? = null

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { }

    private val filePicker = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        if (uri == null) return@registerForActivityResult
        val name = uri.lastPathSegment?.substringAfterLast('/') ?: "phone_file"
        val bytes = contentResolver.openInputStream(uri)?.use { it.readBytes() } ?: return@registerForActivityResult
        bridge?.sendFile(name, bytes)
        appendLog("Sending file $name (${bytes.size} bytes)")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        prefs = getSharedPreferences("cope_companion", MODE_PRIVATE)

        statusLabel = findViewById(R.id.statusLabel)
        messageLog = findViewById(R.id.messageLog)
        ipInput = findViewById(R.id.ipInput)
        portInput = findViewById(R.id.portInput)
        connectButton = findViewById(R.id.connectButton)
        speakButton = findViewById(R.id.speakButton)
        sendFileButton = findViewById(R.id.sendFileButton)
        voiceToggle = findViewById(R.id.voiceToggle)
        notificationToggle = findViewById(R.id.notificationToggle)
        clipboardToggle = findViewById(R.id.clipboardToggle)
        locationToggle = findViewById(R.id.locationToggle)

        ipInput.setText(prefs.getString(KEY_IP, ""))
        portInput.setText(prefs.getString(KEY_PORT, "9876"))
        voiceToggle.isChecked = prefs.getBoolean(KEY_VOICE, false)
        notificationToggle.isChecked = prefs.getBoolean(KEY_NOTIF, false)
        clipboardToggle.isChecked = prefs.getBoolean(KEY_CLIP, false)
        locationToggle.isChecked = prefs.getBoolean(KEY_LOC, false)

        connectButton.setOnClickListener { toggleConnection() }
        speakButton.setOnClickListener {
            startService(MicService.listenIntent(this))
        }
        sendFileButton.setOnClickListener { filePicker.launch("*/*") }

        voiceToggle.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean(KEY_VOICE, checked).apply()
            if (checked) {
                ensureMicPermission()
                if (bridge?.isConnected() == true) startMicService()
            } else {
                stopService(Intent(this, MicService::class.java))
            }
        }
        notificationToggle.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean(KEY_NOTIF, checked).apply()
            if (checked) ensureNotificationAccess()
        }
        clipboardToggle.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean(KEY_CLIP, checked).apply()
            clipboardSync?.enabled = checked
            if (checked) clipboardSync?.start()
        }
        locationToggle.setOnCheckedChangeListener { _, checked ->
            prefs.edit().putBoolean(KEY_LOC, checked).apply()
            if (checked) {
                ensureLocationPermission()
                locationTracker?.enabled = true
                locationTracker?.start()
            } else {
                locationTracker?.enabled = false
                locationTracker?.stop()
            }
        }

        requestStartupPermissions()
    }

    private fun toggleConnection() {
        val existing = bridge
        if (existing?.isConnected() == true) {
            existing.disconnect()
            stopService(Intent(this, MicService::class.java))
            clipboardSync?.stop()
            locationTracker?.stop()
            setConnectedUi(false)
            return
        }
        val ip = ipInput.text?.toString()?.trim().orEmpty()
        val port = portInput.text?.toString()?.toIntOrNull() ?: 9876
        if (ip.isEmpty()) {
            statusLabel.text = "Enter this PC's local IP address."
            return
        }
        prefs.edit().putString(KEY_IP, ip).putString(KEY_PORT, port.toString()).apply()
        val created = CopeBridge(
            onStatus = { msg -> runOnUiThread { onBridgeStatus(msg) } },
            onMessage = { msg -> runOnUiThread { appendLog(msg) } },
            onClipboard = { content ->
                runOnUiThread { clipboardSync?.writeFromPc(content) }
            }
        )
        bridge = created
        clipboardSync = ClipboardSync(this, created).also {
            it.enabled = clipboardToggle.isChecked
            it.start()
        }
        locationTracker = LocationTracker(this, created).also {
            it.enabled = locationToggle.isChecked
            if (locationToggle.isChecked) it.start()
        }
        created.connect(ip, port)
        connectButton.text = getString(R.string.disconnect)
    }

    private fun onBridgeStatus(msg: String) {
        statusLabel.text = msg
        appendLog(msg)
        val connected = msg.startsWith("Connected")
        val disconnected = msg.startsWith("Disconnected") || msg.startsWith("Connection failed")
        if (connected) {
            setConnectedUi(true)
            if (voiceToggle.isChecked) startMicService()
        } else if (disconnected) {
            setConnectedUi(false)
        }
    }

    private fun setConnectedUi(connected: Boolean) {
        connectButton.text = getString(if (connected) R.string.disconnect else R.string.connect)
        speakButton.isEnabled = connected && voiceToggle.isChecked
        sendFileButton.isEnabled = connected
    }

    private fun startMicService() {
        val intent = Intent(this, MicService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    private fun appendLog(msg: String) {
        val previous = messageLog.text?.toString().orEmpty()
        val next = (msg + "\n" + previous).take(2000)
        messageLog.text = next
    }

    private fun requestStartupPermissions() {
        val needed = mutableListOf<String>()
        if (voiceToggle.isChecked) needed += Manifest.permission.RECORD_AUDIO
        if (locationToggle.isChecked) {
            needed += Manifest.permission.ACCESS_FINE_LOCATION
            needed += Manifest.permission.ACCESS_COARSE_LOCATION
        }
        if (Build.VERSION.SDK_INT >= 33) needed += Manifest.permission.POST_NOTIFICATIONS
        val missing = needed.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) permissionLauncher.launch(missing.toTypedArray())
    }

    private fun ensureMicPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED
        ) {
            permissionLauncher.launch(arrayOf(Manifest.permission.RECORD_AUDIO))
        }
    }

    private fun ensureLocationPermission() {
        permissionLauncher.launch(
            arrayOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
        )
    }

    private fun ensureNotificationAccess() {
        val enabled = Settings.Secure.getString(contentResolver, "enabled_notification_listeners") ?: ""
        if (!enabled.contains(packageName)) {
            startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
        }
    }

    override fun onDestroy() {
        clipboardSync?.stop()
        locationTracker?.stop()
        super.onDestroy()
    }

    companion object {
        private const val KEY_IP = "pc_ip"
        private const val KEY_PORT = "pc_port"
        private const val KEY_VOICE = "voice_commands"
        private const val KEY_NOTIF = "notification_mirror"
        private const val KEY_CLIP = "clipboard_sync"
        private const val KEY_LOC = "location_sharing"
    }
}
