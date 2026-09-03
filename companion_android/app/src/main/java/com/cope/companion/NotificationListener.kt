package com.cope.companion

import android.content.Context
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

class NotificationListener : NotificationListenerService() {

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        val extras = sbn?.notification?.extras ?: return
        val prefs = getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (!prefs.getBoolean(KEY_NOTIF, false)) return
        val bridge = CopeBridge.instance ?: return
        if (!bridge.isConnected()) return

        val pkg = sbn.packageName ?: return
        if (isSpam(pkg)) return
        val allow = prefs.getStringSet(KEY_ALLOW, emptySet()) ?: emptySet()
        if (allow.isNotEmpty() && pkg !in allow) return

        val app = pkg.substringAfterLast('.')
        val title = extras.getCharSequence("android.title")?.toString().orEmpty()
        val body = extras.getCharSequence("android.text")?.toString().orEmpty()
        if (title.isBlank() && body.isBlank()) return
        bridge.sendNotification(app, title, body)
    }

    private fun isSpam(pkg: String): Boolean {
        val blocked = setOf(
            "android",
            "com.android.systemui",
            "com.android.providers.downloads",
            "com.google.android.gms",
            "com.android.vending"
        )
        return pkg in blocked
    }

    companion object {
        const val PREFS = "cope_companion"
        const val KEY_NOTIF = "notification_mirror"
        const val KEY_ALLOW = "notif_allowlist"
    }
}
