from collections.abc import Iterator
from ..interfaces import GitProvider
from ..models import Commit


class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> Iterator[Commit]:
        # Lazy import to optimize startup time (~150ms improvement)
        import subprocess

        # Separator for commit boundaries
        separator = "COMMIT_START|"

        # Use tformat with separator to easily identify commits.
        # Include -p to get the diff.
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), f"--pretty=tformat:{separator}%h|%s", "-p"]

        # Use Popen to stream output line by line.
        # Use default buffering (bufsize=-1) to improve throughput and reduce syscalls
        # compared to line buffering (bufsize=1), while still yielding lines via the iterator.
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, text=True
        ) as process:
            # Type safety: stdout is guaranteed to be non-None due to stdout=PIPE
            assert process.stdout is not None

            current_commit: Commit | None = None
            diff_lines: list[str] = []

            for line in process.stdout:
                if line.startswith(separator):
                    # If we have a previous commit pending, yield it
                    if current_commit:
                        current_commit.diff = "".join(diff_lines).strip()
                        yield current_commit

                    # Start new commit
                    # Parse line: "COMMIT_START|hash|message"
                    # Remove separator first
                    content = line[len(separator):]
                    parts = content.partition('|')
                    if parts[1]:
                        # parts[0] is hash, parts[2] is message (with newline)
                        current_commit = Commit(hash_id=parts[0], message=parts[2][:-1])
                        diff_lines = []
                else:
                    if current_commit:
                        diff_lines.append(line)

            # Yield the last commit
            if current_commit:
                current_commit.diff = "".join(diff_lines).strip()
                yield current_commit

            # Check for errors after processing
            if process.wait() != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
