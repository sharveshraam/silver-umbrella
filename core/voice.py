"""Lazy offline speech-to-text, text-to-speech, and microphone wake loop."""
from __future__ import annotations
import importlib.util
import threading
import time

class VoiceEngine:
    """Voice facade with pyttsx3 fallback and lazy Whisper loading."""
    def __init__(self, settings, stealth_mode=None, sloth_mode=None):
        self.settings=settings; self._tts=None; self._stt=None; self.muted=False; self.stealth_mode=stealth_mode; self.sloth_mode=sloth_mode
    def _load_tts(self):
        """Load TTS engine on first speech."""
        if self._tts is None:
            import pyttsx3; self._tts=pyttsx3.init(); self._tts.setProperty('rate', self.settings.get('voice_speed',160)); self._tts.setProperty('volume', self.settings.get('voice_volume',0.9))
    def speak(self, text: str) -> None:
        """Speak text unless muted, stealth, or sleeping."""
        if self.muted: return
        if self.stealth_mode and not self.stealth_mode.should_speak(): return
        if self.sloth_mode and self.sloth_mode.is_active(): return
        self._load_tts(); self._tts.say(text); self._tts.runAndWait()
    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe an audio file with faster-whisper loaded lazily."""
        if self.sloth_mode and self.sloth_mode.is_active(): return ''
        if self._stt is None:
            from faster_whisper import WhisperModel; self._stt=WhisperModel('tiny', device='cpu', compute_type='int8')
        segments,_=self._stt.transcribe(audio_path); return ' '.join(s.text for s in segments)

class MicListener:
    """Continuous low-CPU mic loop that feeds PCM to DoubleClapDetector."""
    CHUNK = 512
    RATE = 8000
    CHANNELS = 1
    FORMAT = None

    def __init__(self, detector, on_wake_callback, sloth_mode=None):
        self.detector = detector
        self.on_wake = on_wake_callback
        self.sloth_mode = sloth_mode
        self._stop = threading.Event()
        self._thread = None
        self.last_error: str | None = None

    def start(self):
        """Start the background mic thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="jarvis-mic", daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the mic thread to stop."""
        self._stop.set()

    def _loop(self):
        """Read 8 kHz mono PCM from PyAudio and feed the wake detector."""
        if not importlib.util.find_spec("pyaudio"):
            self.last_error = "PyAudio is not installed; wake microphone loop is disabled."
            return
        import pyaudio
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16, channels=self.CHANNELS, rate=self.RATE,
            input=True, frames_per_buffer=self.CHUNK
        )
        try:
            while not self._stop.is_set():
                if self.sloth_mode and self.sloth_mode.is_active():
                    time.sleep(0.5); continue
                pcm = stream.read(self.CHUNK, exception_on_overflow=False)
                if self.detector.feed(pcm):
                    self.on_wake()
        finally:
            stream.stop_stream(); stream.close(); pa.terminate()
