## 2024-05-22 - [Simplified Git Parsing]
**Observation:** `LocalGitService._parse_git_log` used a verbose loop with explicit list management and string splitting, adding unnecessary cognitive load.
**Action:** Refactored to a single list comprehension using `partition` and `splitlines()`. Reduced method size by 50% while maintaining identical behavior and error handling (skipping malformed lines).

## 2026-01-17 - [Removed Dead Code]
**Observation:** `Commit` data model contained an unused `diff` field, suggesting a feature that was either removed or never implemented (YAGNI). `src/core/engine.py` had an unused `List` import.
**Action:** Removed the `diff` field and `Optional` import from `src/models.py`. Removed unused `List` import from `src/core/engine.py`. Reduced cognitive load by removing misleading code paths.

## 2026-02-10 - [Modernized Types and Error Handling]
**Observation:** `LocalGitService` used deprecated `typing.List` and swallowed exceptions with a `try/except` block that printed to stdout, creating hidden control flow and side effects.
**Action:** Replaced `List` with `list` (Python 3.9+). Removed `try/except` in `get_commit_history` to allow exceptions to propagate to the caller, simplifying the service and improving error visibility.

## 2026-01-25 - [Removed Dead Code in Git Service]
**Observation:** `LocalGitService._parse_git_log` was a dead method, a remnant of a previous implementation before streaming was introduced. Tests were verifying this dead code instead of the actual `_parse_commit_from_line` logic used in production.
**Action:** Removed `_parse_git_log`. Refactored tests to directly verify `_parse_commit_from_line`, ensuring the test suite covers the live code path and reducing cognitive load.
