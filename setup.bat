@echo off
setlocal
cd /d %~dp0
py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install msedge
where ffmpeg >nul 2>nul || echo Please install FFmpeg and add it to PATH.
where ollama >nul 2>nul && ollama pull llama3:8b
echo Checking for ADB...
where adb >nul 2>nul && echo ADB found. || echo WARNING: ADB not found. Download Android Platform Tools from developer.android.com and add to PATH.

echo.
echo COPE Companion App:
echo   1. Build the companion_android app in Android Studio
echo   2. Install on your Android phone
echo   3. Open the app and enter this PC's local IP address
echo   4. Set companion_app_enabled: true in config.yaml
echo   5. Restart COPE
echo.
python -c "from core.memory import MemoryStore; MemoryStore(); print('Database ready')"
mkdir data\activity_log 2>nul
mkdir assets\sounds assets\icons assets\tts_voice 2>nul
echo JARVIS setup complete. Run: .venv\Scripts\python main.py
