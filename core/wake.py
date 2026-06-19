"""Low-CPU double-clap wake detection."""
import time
class DoubleClapDetector:
    """Detect two sharp microphone energy spikes within a timing window."""
    def __init__(self, sensitivity: float=.75, sloth_mode=None): self.threshold=int(5000+15000*sensitivity); self.last=0.0; self.sloth_mode=sloth_mode
    def _rms16(self, pcm: bytes) -> int:
        """Compute RMS for little-endian signed 16-bit mono PCM without audioop."""
        if not pcm: return 0
        total=0; count=0
        for i in range(0, len(pcm)-1, 2):
            sample=int.from_bytes(pcm[i:i+2], 'little', signed=True); total += sample*sample; count += 1
        return int((total/max(count,1)) ** 0.5)
    def is_clap(self, pcm: bytes) -> bool:
        """Return True when raw 16-bit mono PCM looks like a clap."""
        if self.sloth_mode and self.sloth_mode.is_active(): return False
        return self._rms16(pcm)>self.threshold
    def feed(self, pcm: bytes) -> bool:
        """Feed one audio frame and return True on confirmed double clap."""
        if self.sloth_mode and self.sloth_mode.is_active(): return False
        now=time.time()
        if self.is_clap(pcm):
            ok=.2 <= now-self.last <= .8; self.last=now; return ok
        return False
