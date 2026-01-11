import subprocess
from typing import List
from ..interfaces import GitProvider
from ..models import Commit

class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> List[Commit]:
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), "--pretty=format:%h|%s"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return self._parse_git_log(result.stdout)
        except subprocess.CalledProcessError as e:
            # Handle error appropriately, maybe log or re-raise custom exception
            print(f"Error fetching git log: {e}")
            return []

    def _parse_git_log(self, output: str) -> List[Commit]:
        commits = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                commits.append(Commit(hash_id=parts[0], message=parts[1]))
        return commits
