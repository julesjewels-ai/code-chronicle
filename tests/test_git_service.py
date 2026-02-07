import pytest
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

# Type alias for clarity
MockProcess = MagicMock

@pytest.fixture
def repo_path() -> str:
    """Fixture providing a dummy repo path."""
    return "/tmp/mock-repo"

@pytest.fixture
def git_service(repo_path: str) -> LocalGitService:
    """Fixture providing a LocalGitService instance."""
    return LocalGitService(repo_path)

@pytest.fixture
def mock_popen(mocker):
    """Fixture to mock subprocess.Popen."""
    return mocker.patch("subprocess.Popen")

def setup_mock_process(mock_popen: MagicMock, stdout_lines: list[str], return_code: int = 0) -> MagicMock:
    """Helper to configure the mock process behavior."""
    process_mock = MagicMock()
    # Popen is a context manager, so __enter__ returns the process instance
    process_mock.__enter__.return_value = process_mock
    process_mock.__exit__.return_value = None

    # stdout iteration
    process_mock.stdout = iter(stdout_lines)

    # wait() returns the exit code
    process_mock.wait.return_value = return_code
    process_mock.returncode = return_code

    mock_popen.return_value = process_mock
    return process_mock

@pytest.mark.parametrize(
    "stdout_lines, expected_commits, expected_count",
    [
        # Happy path: Standard commits
        (
            ["a1b2c3d|Initial commit\n", "e5f6g7h|Fix bug\n"],
            [Commit("a1b2c3d", "Initial commit"), Commit("e5f6g7h", "Fix bug")],
            2
        ),
        # Edge case: Empty output
        (
            [],
            [],
            0
        ),
        # Edge case: Malformed lines (missing pipe) should be skipped
        (
            ["valid|msg\n", "invalid-line\n", "another|valid\n"],
            [Commit("valid", "msg"), Commit("another", "valid")],
            2
        ),
        # Edge case: Empty message (hash|)
        (
            ["hash|\n"],
            [Commit("hash", "")],
            1
        ),
        # Edge case: Empty hash (|msg)
        (
            ["|msg\n"],
            [Commit("", "msg")],
            1
        ),
        # Edge case: Multiple pipes in message (should take first pipe as separator)
        (
            ["hash|msg|with|pipes\n"],
            [Commit("hash", "msg|with|pipes")],
            1
        ),
    ],
    ids=[
        "happy_path",
        "empty_output",
        "skip_malformed",
        "empty_message",
        "empty_hash",
        "multiple_pipes"
    ]
)
def test_get_commit_history_parsing(
    git_service: LocalGitService,
    mock_popen: MagicMock,
    stdout_lines: list[str],
    expected_commits: list[Commit],
    expected_count: int
):
    """Verify that commit history is parsed correctly from git log output."""
    # Arrange
    setup_mock_process(mock_popen, stdout_lines)

    # Act
    commits = list(git_service.get_commit_history(limit=5))

    # Assert
    assert len(commits) == expected_count
    assert commits == expected_commits

    # Verify subprocess call arguments
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    assert args[0] == ["git", "-C", git_service.repo_path, "log", "-n", "5", "--pretty=tformat:%h|%s"]
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["text"] is True

def test_get_commit_history_process_error(
    git_service: LocalGitService,
    mock_popen: MagicMock
):
    """Verify that CalledProcessError is raised when git returns non-zero exit code."""
    # Arrange
    setup_mock_process(mock_popen, [], return_code=1)

    # Act & Assert
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        list(git_service.get_commit_history(limit=5))

    assert exc_info.value.returncode == 1

def test_get_commit_history_command_args(
    git_service: LocalGitService,
    mock_popen: MagicMock
):
    """Verify that command arguments are constructed correctly based on input."""
    # Arrange
    setup_mock_process(mock_popen, [])
    limit = 10

    # Act
    list(git_service.get_commit_history(limit=limit))

    # Assert
    args, _ = mock_popen.call_args
    expected_cmd = ["git", "-C", git_service.repo_path, "log", "-n", str(limit), "--pretty=tformat:%h|%s"]
    assert args[0] == expected_cmd
