import pytest  # type: ignore
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def git_service() -> LocalGitService:
    """Fixture to provide a LocalGitService instance."""
    return LocalGitService("/tmp/repo")

@pytest.fixture
def mock_popen(mocker: MagicMock) -> MagicMock:
    """Fixture to mock subprocess.Popen."""
    return mocker.patch("subprocess.Popen")

@pytest.mark.parametrize("stdout_lines, expected_commits", [
    # Standard case: Valid hash and message
    (
        ["abcdef|Initial commit\n", "123456|Second commit\n"],
        [
            Commit(hash_id="abcdef", message="Initial commit"),
            Commit(hash_id="123456", message="Second commit")
        ]
    ),
    # Empty output: No commits
    ([], []),
    # Malformed lines: Missing delimiter (should be skipped)
    (["invalid line\n", "another invalid\n"], []),
    # Mixed valid and invalid lines
    (
        ["abcdef|Valid\n", "invalid\n", "123456|Another valid\n"],
        [
            Commit(hash_id="abcdef", message="Valid"),
            Commit(hash_id="123456", message="Another valid")
        ]
    ),
    # Empty message: Valid hash but empty message part
    (["abcdef|\n"], [Commit(hash_id="abcdef", message="")]),
    # Trailing newline handling
    (["abcdef|Line with newline\n"], [Commit(hash_id="abcdef", message="Line with newline")])
])
def test_get_commit_history_success(
    git_service: LocalGitService,
    mock_popen: MagicMock,
    stdout_lines: list[str],
    expected_commits: list[Commit]
) -> None:
    """Test get_commit_history with various output scenarios."""
    # Setup mock process
    process_mock = MagicMock()
    process_mock.stdout = iter(stdout_lines)
    process_mock.wait.return_value = 0
    process_mock.__enter__.return_value = process_mock
    mock_popen.return_value = process_mock

    # Execute
    limit = 10
    commits = list(git_service.get_commit_history(limit))

    # Assert
    assert commits == expected_commits

    # Verify subprocess call
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    # Verify command structure
    assert args[0][:5] == ["git", "-C", "/tmp/repo", "log", "-n"]
    assert args[0][5] == str(limit)
    assert args[0][6] == "--pretty=tformat:%h|%s"
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["text"] is True

def test_get_commit_history_process_error(git_service: LocalGitService, mock_popen: MagicMock) -> None:
    """Test get_commit_history raises CalledProcessError on non-zero exit code."""
    # Setup mock process to fail
    process_mock = MagicMock()
    process_mock.stdout = iter([])
    process_mock.wait.return_value = 1
    process_mock.returncode = 1
    process_mock.__enter__.return_value = process_mock
    mock_popen.return_value = process_mock

    # Execute and Assert
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        list(git_service.get_commit_history(5))

    assert exc_info.value.returncode == 1

def test_get_commit_history_os_error(git_service: LocalGitService, mock_popen: MagicMock) -> None:
    """Test get_commit_history raises OSError (e.g. git not found)."""
    # Simulate an OSError
    mock_popen.side_effect = OSError("git not found")

    with pytest.raises(OSError, match="git not found"):
        list(git_service.get_commit_history(5))

def test_initialization() -> None:
    """Test LocalGitService initialization."""
    service = LocalGitService("/custom/path")
    assert service.repo_path == "/custom/path"
