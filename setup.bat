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
python -c "from core.memory import MemoryStore; MemoryStore(); print('Database ready')"
mkdir data\activity_log 2>nul
mkdir assets\sounds assets\icons assets\tts_voice 2>nul
echo JARVIS setup complete. Run: .venv\Scripts\python main.py
