"""Lazy offline speech-to-text and text-to-speech."""
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
