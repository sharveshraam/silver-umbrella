"""Shared skill helpers."""
def require_confirm(action): """Return a standard confirmation payload."""; return {'requires_confirmation': True, 'action': action}
