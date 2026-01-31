from collections.abc import Iterator
from ..interfaces import GitProvider
from ..models import Commit


class LocalGitService(GitProvider):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_commit_history(self, limit: int) -> Iterator[Commit]:
        # Lazy import to optimize startup time
        import subprocess

        # Format: hash|author|date|subject|body(record_sep)
        # delimiters: \x1f (unit separator) for fields, \x1e (record separator) for commits
        # tformat adds a newline after each commit, so we will get ...%x1e\n
        fmt = "%h%x1f%an%x1f%ad%x1f%s%x1f%b%x1e"
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), f"--pretty=tformat:{fmt}"]

        # Use Popen to stream output
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, text=True, bufsize=-1
        ) as process:
            assert process.stdout is not None

            buffer = ""
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                buffer += chunk
                while '\x1e' in buffer:
                    record, _, buffer = buffer.partition('\x1e')
                    if commit := _parse_commit_record(record):
                        yield commit

            # Handle any remaining data
            if buffer and (commit := _parse_commit_record(buffer)):
                yield commit

            if process.wait() != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)


def _parse_commit_record(record: str) -> Commit | None:
    # Remove potential leading newline from tformat
    record = record.lstrip()
    if not record:
        return None

    parts = record.split('\x1f')
    # Expecting 5 parts: hash, author, date, subject, body
    # But body might be empty or contain fewer parts if git log output is weird?
    # git log format should guarantee parts if placeholders are there.
    # However, if body is empty, it's just empty string.

    if len(parts) >= 5:
        return Commit(
            hash_id=parts[0],
            author=parts[1],
            date=parts[2],
            message=parts[3],
            body=parts[4]
        )
    return None
