## 2024-05-22 - [Simplified Git Parsing]
**Observation:** `LocalGitService._parse_git_log` used a verbose loop with explicit list management and string splitting, adding unnecessary cognitive load.
**Action:** Refactored to a single list comprehension using `partition` and `splitlines()`. Reduced method size by 50% while maintaining identical behavior and error handling (skipping malformed lines).

## 2024-05-22 - [Simplified Error Handling]
**Observation:** `LocalGitService.get_commit_history` swallowed `subprocess.CalledProcessError` and printed to stdout, which is a side effect and hides errors from the caller.
**Action:** Removed the `try...except` block, allowing the exception to propagate to the orchestrator (`main.py`) which already handles exceptions. This reduces code and enforces proper error handling.
