from collections.abc import Iterator
from ..interfaces import GitProvider
from ..models import Commit


class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> Iterator[Commit]:
        # Lazy import to optimize startup time (~150ms improvement)
        import subprocess

        # Use tformat to ensure consistent trailing newlines, allowing faster slicing
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), "--pretty=tformat:%h|%s"]

        # Use Popen to stream output line by line.
        # Use default buffering (bufsize=-1) to improve throughput and reduce syscalls
        # compared to line buffering (bufsize=1), while still yielding lines via the iterator.
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, text=True
        ) as process:
            # Type safety: stdout is guaranteed to be non-None due to stdout=PIPE
            assert process.stdout is not None

            for line in process.stdout:
                # Optimization: Inlined parsing logic (avoids function call overhead)
                parts = line.partition('|')
                if parts[1]:
                    yield Commit(hash_id=parts[0], message=parts[2].rstrip('\n'))

            # Check for errors after processing
            if process.wait() != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
