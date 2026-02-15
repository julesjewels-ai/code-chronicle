import pytest  # type: ignore
from pytest_mock import MockerFixture  # type: ignore
from src.services.git import LocalGitService
from src.models import Commit
import subprocess

@pytest.fixture
def service() -> LocalGitService:
    return LocalGitService(repo_path=".")

@pytest.mark.parametrize("stdout_lines, returncode, expected_commits, expected_error", [
    # Standard success case
    (
        ["a1b2c3d|Initial commit\n", "e5f6g7h|Second commit\n"],
        0,
        [
            Commit(hash_id="a1b2c3d", message="Initial commit"),
            Commit(hash_id="e5f6g7h", message="Second commit")
        ],
        None
    ),
    # Empty output (no commits)
    (
        [],
        0,
        [],
        None
    ),
    # Malformed line (missing separator) - should be skipped
    (
        ["invalid_line_no_separator\n"],
        0,
        [],
        None
    ),
    # Truncated line (no newline at end) - current implementation slices last char
    # This documents the behavior: "Truncated message" -> "Truncated messag"
    (
        ["a1b2c3d|Truncated message"],
        0,
        [Commit(hash_id="a1b2c3d", message="Truncated messag")],
        None
    ),
    # Mixed valid and invalid
    (
        ["a1b2c3d|Valid\n", "badline\n", "e5f6g7h|Also Valid\n"],
        0,
        [
            Commit(hash_id="a1b2c3d", message="Valid"),
            Commit(hash_id="e5f6g7h", message="Also Valid")
        ],
        None
    ),
    # Subprocess error
    (
        [],
        1,
        [],
        subprocess.CalledProcessError
    )
])
def test_get_commit_history(
    service: LocalGitService,
    stdout_lines: list[str],
    returncode: int,
    expected_commits: list[Commit],
    expected_error: type[Exception] | None,
    mocker: MockerFixture
) -> None:
    # Mock subprocess.Popen
    mock_popen = mocker.patch("subprocess.Popen")
    mock_process = mock_popen.return_value

    # Configure context manager
    mock_process.__enter__.return_value = mock_process
    mock_process.__exit__.return_value = None

    # Configure stdout iterator
    mock_process.stdout = iter(stdout_lines)

    # Configure return code
    mock_process.wait.return_value = returncode
    mock_process.returncode = returncode

    if expected_error:
        with pytest.raises(expected_error):
            list(service.get_commit_history(limit=5))
    else:
        commits = list(service.get_commit_history(limit=5))
        assert commits == expected_commits
