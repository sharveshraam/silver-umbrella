"""Git automation skill."""
from git import Repo
class GitAuto:
    """Stage and commit local project changes without pushing."""
    def commit_all(self, repo_path: str, message: str):
        """Stage all changes and commit with a provided message."""; repo=Repo(repo_path); repo.git.add(A=True); return repo.index.commit(message)
