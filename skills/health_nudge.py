"""Health nudge reminders."""
class HealthNudge:
    """Generate stretch and eye-strain reminders."""
    def message(self, minutes): """Return a health nudge for active screen time."""; return 'Look 20 feet away for 20 seconds, Sir.' if minutes>=60 else ''
