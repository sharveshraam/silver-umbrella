"""YouTube Shorts scheduled workflow."""
class YouTubeWorkflow:
    """Pipeline planner for fetch, cut, caption, thumbnail, score, upload."""
    def plan(self): """Return pipeline steps without executing uploads."""; return ['fetch_trends','download','transcribe','cut_vertical','caption','thumbnail','score_hook','confirm_upload','log']
