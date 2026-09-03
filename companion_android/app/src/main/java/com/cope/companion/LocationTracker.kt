package com.cope.companion

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.os.Looper
import androidx.core.content.ContextCompat
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority

class LocationTracker(
    context: Context,
    private val bridge: CopeBridge
) {
    private val appContext = context.applicationContext
    private val client = LocationServices.getFusedLocationProviderClient(appContext)
    @Volatile
    var enabled: Boolean = false

    private val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            if (!enabled || !bridge.isConnected()) return
            val loc = result.lastLocation ?: return
            bridge.sendLocation(loc.latitude, loc.longitude)
        }
    }

    @SuppressLint("MissingPermission")
    fun start() {
        if (!hasPermission()) return
        val request = LocationRequest.Builder(Priority.PRIORITY_BALANCED_POWER_ACCURACY, 5 * 60 * 1000L)
            .setMinUpdateIntervalMillis(5 * 60 * 1000L)
            .setMinUpdateDistanceMeters(50f)
            .build()
        client.requestLocationUpdates(request, callback, Looper.getMainLooper())
        client.lastLocation.addOnSuccessListener { loc ->
            if (enabled && loc != null && bridge.isConnected()) {
                bridge.sendLocation(loc.latitude, loc.longitude)
            }
        }
    }

    fun stop() {
        client.removeLocationUpdates(callback)
    }

    private fun hasPermission(): Boolean {
        val fine = ContextCompat.checkSelfPermission(appContext, Manifest.permission.ACCESS_FINE_LOCATION)
        val coarse = ContextCompat.checkSelfPermission(appContext, Manifest.permission.ACCESS_COARSE_LOCATION)
        return fine == PackageManager.PERMISSION_GRANTED || coarse == PackageManager.PERMISSION_GRANTED
    }
}
