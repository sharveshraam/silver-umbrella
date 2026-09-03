"""APScheduler wrapper for reminders and workflows."""
from apscheduler.schedulers.background import BackgroundScheduler
class JarvisScheduler:
    """Background scheduler that keeps UI work non-blocking."""
    def __init__(self): self.scheduler=BackgroundScheduler()
    def start(self) -> None:
        """Start scheduling if not already running."""
        if not self.scheduler.running: self.scheduler.start()
    def add_once(self, run_date, func, *args, **kwargs):
        """Schedule a one-time task."""; return self.scheduler.add_job(func,'date',run_date=run_date,args=args,kwargs=kwargs)
