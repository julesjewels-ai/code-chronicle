from typing import Iterator, Optional
from ..interfaces import GitProvider
from ..models import Commit

class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> Iterator[Commit]:
        # Optimization: Lazy import subprocess to save ~20-40ms startup time
        import subprocess
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), "--pretty=format:%h|%s"]

        # Use Popen to stream output line by line.
        # bufsize=1 enables line buffering.
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, text=True, bufsize=1
        ) as process:
            if process.stdout:
                for line in process.stdout:
                    if commit := _parse_commit_from_line(line):
                        yield commit

            # Check for errors after processing
            if process.wait() != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)

    @staticmethod
    def _parse_git_log(output: str) -> list[Commit]:
        return [
            Commit(hash_id=parts[0], message=parts[2])
            for line in output.splitlines()
            if (parts := line.partition('|'))[1]
        ]

def _parse_commit_from_line(line: str) -> Optional[Commit]:
    line = line.rstrip('\n')
    parts = line.partition('|')
    if parts[1]:
        return Commit(hash_id=parts[0], message=parts[2])
    return None
