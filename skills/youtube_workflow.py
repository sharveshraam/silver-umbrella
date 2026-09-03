"""YouTube Shorts scheduled workflow."""
class YouTubeWorkflow:
    """Pipeline planner for fetch, cut, caption, thumbnail, score, upload."""
    def __init__(self, settings=None, brain=None):
        self.settings = settings
        self.brain = brain
    def plan(self): """Return pipeline steps without executing uploads."""; return ['fetch_trends','download','transcribe','cut_vertical','caption','thumbnail','score_hook','confirm_upload','log']
    def run_pipeline(self, topic: str = "") -> str:
        """Plan (and optionally start) the YouTube Shorts pipeline using Settings or a dict."""
        cfg = self.settings.load() if hasattr(self.settings, 'load') else (self.settings or {})
        if not isinstance(cfg, dict):
            cfg = {}
        folder = cfg.get("default_video_folder", "data/videos")
        channel = cfg.get("youtube_channel_id", "")
        steps = self.plan()
        label = topic or "trends"
        dest = f"{folder} (channel {channel})" if channel else str(folder)
        return f"YouTube pipeline for '{label}' → {dest}: " + " → ".join(steps)
