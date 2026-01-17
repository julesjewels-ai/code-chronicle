import subprocess
from typing import List, Iterable
from ..interfaces import GitProvider
from ..models import Commit

class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> List[Commit]:
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), "--pretty=format:%h|%s"]
        try:
            # Use Popen to stream output instead of loading everything into memory
            # This improves performance for large histories and reduces memory usage
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8') as proc:
                commits = self._parse_git_stream(proc.stdout)

                # Check for errors after consuming stdout
                _, stderr = proc.communicate()

                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(proc.returncode, cmd, output=None, stderr=stderr)

                return commits
        except subprocess.CalledProcessError as e:
            # Handle error appropriately, maybe log or re-raise custom exception
            print(f"Error fetching git log: {e}")
            return []

    @staticmethod
    def _parse_git_stream(stream: Iterable[str]) -> List[Commit]:
        return [
            Commit(hash_id=parts[0], message=parts[2].rstrip('\n'))
            for line in stream
            if (parts := line.partition('|'))[1]
        ]

    @staticmethod
    def _parse_git_log(output: str) -> List[Commit]:
        return LocalGitService._parse_git_stream(output.splitlines())
