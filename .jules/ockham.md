## 2024-05-22 - [Simplified Git Parsing]
**Observation:** `LocalGitService._parse_git_log` used a verbose loop with explicit list management and string splitting, adding unnecessary cognitive load.
**Action:** Refactored to a single list comprehension using `partition` and `splitlines()`. Reduced method size by 50% while maintaining identical behavior and error handling (skipping malformed lines).

## 2026-01-17 - [Removed Dead Code]
**Observation:** `Commit` data model contained an unused `diff` field, suggesting a feature that was either removed or never implemented (YAGNI). `src/core/engine.py` had an unused `List` import.
**Action:** Removed the `diff` field and `Optional` import from `src/models.py`. Removed unused `List` import from `src/core/engine.py`. Reduced cognitive load by removing misleading code paths.

## 2026-02-10 - [Modernized Types and Error Handling]
**Observation:** `LocalGitService` used deprecated `typing.List` and swallowed exceptions with a `try/except` block that printed to stdout, creating hidden control flow and side effects.
**Action:** Replaced `List` with `list` (Python 3.9+). Removed `try/except` in `get_commit_history` to allow exceptions to propagate to the caller, simplifying the service and improving error visibility.

## 2026-02-10 - [Removed Dead Git Parsing Logic]
**Observation:** `LocalGitService._parse_git_log` was a dead static method, superseded by the streaming `_parse_commit_from_line` logic used in `get_commit_history`. Its existence caused confusion and required redundant tests.
**Action:** Removed `_parse_git_log` and its associated tests. Refactored tests to verify parsing edge cases via the public `get_commit_history` API using mocks, ensuring coverage while reducing code volume.
