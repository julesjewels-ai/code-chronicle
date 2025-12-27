import subprocess
from typing import List, Dict

class GitManager:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commits(self, limit: int) -> List[Dict[str, str]]:
        """Retrieves a list of commits with their hashes and messages."""
        cmd = ["git", "-C", self.repo_path, "log", f"-n {limit}", "--pretty=format:%h|%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            hash_id, msg = line.split('|', 1)
            commits.append({"hash": hash_id, "message": msg})
        return commits

    def get_diff(self, commit_hash: str) -> str:
        """Retrieves the diff for a given commit hash."""
        cmd = ["git", "-C", self.repo_path, "show", commit_hash, "--pretty=format:"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
