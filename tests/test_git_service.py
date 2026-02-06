import pytest
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def git_service() -> LocalGitService:
    return LocalGitService("/tmp/repo")

@pytest.fixture
def mock_popen(mocker):
    return mocker.patch("subprocess.Popen")

@pytest.mark.parametrize("stdout_lines, expected_commits", [
    # Happy path: multiple valid commits
    (
        ["abcdef|Commit 1\n", "123456|Commit 2\n"],
        [Commit(hash_id="abcdef", message="Commit 1"), Commit(hash_id="123456", message="Commit 2")]
    ),
    # Edge case: Empty output
    (
        [],
        []
    ),
    # Edge case: Invalid format (missing pipe) -> should be skipped
    (
        ["invalid_line\n", "abcdef|Valid\n"],
        [Commit(hash_id="abcdef", message="Valid")]
    ),
    # Edge case: Invalid format (empty message part but pipe exists) -> should be included (message is empty string)
    (
        ["abcdef|\n"],
        [Commit(hash_id="abcdef", message="")]
    ),
     # Edge case: Pipe at start -> empty hash
    (
        ["|Message\n"],
        [Commit(hash_id="", message="Message")]
    ),
])
def test_get_commit_history_parsing(
    git_service: LocalGitService,
    mock_popen: MagicMock,
    stdout_lines: list[str],
    expected_commits: list[Commit]
) -> None:
    # Arrange
    process_mock = MagicMock()
    process_mock.stdout = iter(stdout_lines)
    process_mock.wait.return_value = 0
    process_mock.__enter__.return_value = process_mock
    mock_popen.return_value = process_mock

    # Act
    commits = list(git_service.get_commit_history(5))

    # Assert
    assert commits == expected_commits

    # Verify Popen call
    args, kwargs = mock_popen.call_args
    assert args[0][:5] == ["git", "-C", "/tmp/repo", "log", "-n"]
    assert args[0][6] == "--pretty=tformat:%h|%s"
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["text"] is True

def test_get_commit_history_failure(
    git_service: LocalGitService,
    mock_popen: MagicMock
) -> None:
    # Arrange
    process_mock = MagicMock()
    process_mock.stdout = iter([])
    process_mock.wait.return_value = 1
    process_mock.returncode = 1
    process_mock.__enter__.return_value = process_mock
    mock_popen.return_value = process_mock

    # Act & Assert
    with pytest.raises(subprocess.CalledProcessError):
        list(git_service.get_commit_history(5))
