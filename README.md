# JARVIS — Local Desktop AI Companion

JARVIS is a local-first Windows desktop assistant built with Python 3.11+, PyQt6, SQLite, lazy-loaded voice services, and optional local/cloud AI providers. It is designed for personal use, offline resilience, and potato-laptop performance.

## Features

- Frameless Iron Man-inspired HUD with an animated arc reactor, chat log, status bar, and orb-ready UI.
- Local memory and Second Brain backed by SQLite WAL and FTS5.
- Local-first LLM integration through Ollama (`llama3:8b` by default), with safe fallback messaging.
- Lazy TTS/STT loading: pyttsx3 fallback and Faster-Whisper tiny model support.
- Double-clap wake detection logic using low-cost PCM energy spikes.
- Modular skills for files, browser research, messaging drafts, image editing, thumbnails, video, reminders, system control, focus, privacy, intruder alert, Git automation, YouTube workflows, and viral hook scoring.
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
