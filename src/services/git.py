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
            # Optimize: Stream stdout to avoid loading full output into memory.
            # Reduces memory footprint for large commit histories.
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, encoding='utf-8') as process:
                if process.stdout is None:
                    return []
                commits = self._parse_git_log(process.stdout)
                # Ensure process completes and check return code
                if process.wait() != 0:
                    raise subprocess.CalledProcessError(process.returncode, cmd)
                return commits
        except subprocess.CalledProcessError as e:
            # Handle error appropriately, maybe log or re-raise custom exception
            print(f"Error fetching git log: {e}")
            return []
        except Exception as e:
            print(f"Error executing git: {e}")
            return []

    @staticmethod
    def _parse_git_log(lines: Iterable[str]) -> List[Commit]:
        # Accepts any iterable of strings (list, file object, generator)
        # Handle string input for backward compatibility and tests
        if isinstance(lines, str):
            lines = lines.splitlines()

        return [
            Commit(hash_id=parts[0], message=parts[2])
            for line in lines
            if (parts := line.strip().partition('|'))[1]
        ]
