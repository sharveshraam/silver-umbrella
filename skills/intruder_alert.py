"""Opt-in webcam intruder alert."""
class IntruderAlert:
    """Disabled-by-default face check placeholder using OpenCV when enabled."""
    def enabled(self, settings): """Return configured opt-in status."""; return bool(settings.get('intruder_alert_enabled', False))
