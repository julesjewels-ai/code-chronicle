import subprocess
from typing import List
from ..interfaces import GitProvider
from ..models import Commit

class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> List[Commit]:
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), "--pretty=format:%h|%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return self._parse_git_log(result.stdout)

    @staticmethod
    def _parse_git_log(output: str) -> List[Commit]:
        return [
            Commit(hash_id=parts[0], message=parts[2])
            for line in output.splitlines()
            if (parts := line.partition('|'))[1]
        ]
