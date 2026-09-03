# JARVIS — Local Desktop AI Companion

JARVIS is a local-first Windows desktop assistant built with Python 3.11+, PyQt6, SQLite, lazy-loaded voice services, and optional local/cloud AI providers. It is designed for personal use, offline resilience, and potato-laptop performance.

## Features

- Frameless Iron Man-inspired HUD with an animated arc reactor, chat log, status bar, and orb-ready UI.
- Local memory and Second Brain backed by SQLite WAL and FTS5.
- Local-first LLM integration through Ollama (`llama3:8b` by default), with safe fallback messaging.
- Lazy TTS/STT loading: pyttsx3 fallback and Faster-Whisper tiny model support.
- Double-clap wake detection logic using low-cost PCM energy spikes.
- Modular skills for files, browser research, messaging drafts, image editing, thumbnails, video, reminders, system control, focus, privacy, intruder alert, Git automation, YouTube workflows, and viral hook scoring.
- Phone integration via USB (ADB) or Wi-Fi (COPE Companion App).
- Every potentially irreversible action is designed to be confirmed before execution by the brain/router layer.
- Feature toggles live in `config.yaml` so modules can be disabled independently.

## Setup on Windows

1. Install Python 3.11+.
2. Install Ollama and FFmpeg if you want local LLM/video features.
3. Run:

```bat
setup.bat
```

4. Launch:

```bat
.venv\Scripts\python main.py
```

## Phone Integration

### USB (ADB)
1. Enable Developer Options on your Android phone
2. Enable USB Debugging
3. Connect phone via USB cable
4. Set `adb_enabled: true` in config.yaml
5. COPE will show `[ADB: CONNECTED]` in the top bar

Commands: "Pull photos from phone", "Take phone screenshot",
"Get phone battery level", "Launch [app] on phone"

### Wi-Fi (COPE Companion App)
1. Build `companion_android/` in Android Studio and install on phone
2. Connect phone and PC to the same Wi-Fi network
3. Find your PC's local IP (run `ipconfig` in terminal)
4. Enter that IP in the companion app and tap Connect
5. Set `companion_app_enabled: true` in config.yaml and restart COPE

Features: voice commands from phone, notification mirror,
clipboard sync, location sharing, file transfer

## Configuration

Edit `config.yaml` to change user name, wake mode, LLM model, API keys, folders, briefing time, focus sites, and feature flags.

## Privacy and Safety

- JARVIS stores memory locally in `data/jarvis.db`.
- Intruder alert is disabled by default and must be enabled in config.
- Sending messages, deleting files, uploading videos, Git commits/pushes, shutdown/restart, and lock actions should be confirmed by the user before execution.
- API keys are optional and blank by default.

## Project Layout

```text
core/       Brain, settings, voice, wake, memory, scheduler, pattern learning
skills/     One module per assistant skill
ui/         PyQt6 HUD, orb, styles, animations
workflows/  YAML scheduled workflow definitions
data/       SQLite database and daily activity logs
assets/     Sounds, icons, and optional TTS voice assets
```

## Development Notes

- Keep heavy services lazy-loaded.
- Avoid blocking the UI thread; schedule workflows in background jobs/threads.
- Prefer local/offline behavior and explicit confirmation for destructive actions.

## Phase 2 Modes

### Stealth Mode

Stealth Mode switches JARVIS into silent text-only operation. TTS is suppressed, the microphone/STT path can remain active, and the sidebar chat displays timestamped responses. Toggle it with the HUD Stealth button, the configured `stealth_hotkey`, or the phrase `JARVIS, stealth mode`.

### Companion Pet

The floating pet is a lightweight transparent `QWidget` rendered with `QPainter`. It supports idle, listening, thinking, working, happy, alert, sleeping, stealth, focused, and reading states, plus short speech bubbles for quick nudges.

### Teaching Mode

Teaching Mode turns errors into layered explanations: what happened, why it happened, deeper context, how to fix it now, how to avoid it next time, and a prompt to go deeper. Known concepts are stored locally so JARVIS can avoid repeating full lessons unnecessarily.

### Self-Learning

Self-learning is idle-triggered only. When the user has been inactive long enough, JARVIS can fetch configured RSS sources in a daemon thread, summarize items, store them in the Second Brain, and stop immediately when activity returns or Sloth Mode activates.

### Location Adaptive Mode

On startup, JARVIS can detect coarse location, timezone, network latency, and battery state. It uses this context to recommend local/offline mode, reduced video quality, performance mode, or workflow pausing.

### Sloth Mode

Sloth Mode is full DND/deep sleep. Wake detection, speech, learning, reminders, workflows, sounds, and animations are expected to pause until the user manually wakes JARVIS through the orb, wake hotkey, or optional configured auto-wake.
