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

## 2026-03-01 - [Modernized Type Hints]
**Observation:** `src/services/git.py` and `src/interfaces.py` relied on legacy `typing` imports (`Iterator`, `Optional`), adding unnecessary import overhead and verbosity.
**Action:** Replaced `typing.Iterator` with `collections.abc.Iterator` and `Optional[T]` with `T | None` (Python 3.10+). Removed unused `typing` imports to simplify dependency footprint and align with modern Python standards.

## 2026-03-05 - [Flattened Git Service Logic]
**Observation:** `LocalGitService.get_commit_history` contained unnecessary nesting (level 4) due to a redundant `if process.stdout:` check, increasing cognitive load.
**Action:** Removed the redundant check and added an `assert` for type safety. Flattened the loop structure to improve readability while maintaining strict type compliance.

## 2026-03-XX - [Refactor Git Parsing & Linting Payment]
**Observation:** `_parse_commit_from_line` used magic indices (`parts[1]`) reducing readability. Codebase had accumulated multiple PEP 8 violations (blank lines, line lengths).
**Action:** Refactored to use tuple unpacking (`hash_id, sep, message`) for clarity. Paid down linting debt across the entire codebase to meet standards.
