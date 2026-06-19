"""Privacy lockdown mode."""
class PrivacyMode:
    """Coordinates mic mute, clipboard clearing, window hiding, and lock."""
    def lockdown_plan(self): """Return actions to execute after confirmation."""; return ['mute_microphone','hide_windows','clear_clipboard','lock_screen']
