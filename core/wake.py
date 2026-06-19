"""Low-CPU double-clap wake detection."""
import audioop, time
class DoubleClapDetector:
    """Detect two sharp microphone energy spikes within a timing window."""
    def __init__(self, sensitivity: float=.75): self.threshold=int(5000+15000*sensitivity); self.last=0.0
    def is_clap(self, pcm: bytes) -> bool:
        """Return True when raw 16-bit mono PCM looks like a clap."""; return audioop.rms(pcm,2)>self.threshold
    def feed(self, pcm: bytes) -> bool:
        """Feed one audio frame and return True on confirmed double clap."""
        now=time.time()
        if self.is_clap(pcm):
            ok=.2 <= now-self.last <= .8; self.last=now; return ok
        return False
