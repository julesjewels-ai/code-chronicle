import pytest
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def git_service() -> LocalGitService:
    return LocalGitService("/tmp/repo")

@pytest.mark.parametrize("stdout_lines, expected_commits", [
    (
        ["h1|msg1\n", "h2|msg2\n"],
        [Commit("h1", "msg1"), Commit("h2", "msg2")]
    ),
    (
        ["h1|msg1|part2\n"],
        [Commit("h1", "msg1|part2")]
    ),
    (
        [],
        []
    ),
    (
        ["invalid_line\n", "h3|msg3\n"],
        [Commit("h3", "msg3")]  # The invalid line is skipped
    ),
])
def test_get_commit_history_success(
    git_service: LocalGitService,
    mocker,
    stdout_lines: list[str],
    expected_commits: list[Commit]
) -> None:
    # Mock subprocess.Popen
    mock_popen = mocker.patch('subprocess.Popen')
    mock_process = MagicMock()
    # Configure the mock to return an iterator for stdout
    mock_process.stdout = iter(stdout_lines)
    mock_process.wait.return_value = 0
    # Configure context manager behavior
    mock_process.__enter__.return_value = mock_process
    mock_popen.return_value = mock_process

    # Execute
    commits = list(git_service.get_commit_history(2))

    # Assert
    assert commits == expected_commits

    # Verify call args
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    # Verify command structure
    expected_cmd = ["git", "-C", "/tmp/repo", "log", "-n", "2", "--pretty=tformat:%h|%s"]
    assert args[0] == expected_cmd
    assert kwargs['stdout'] == subprocess.PIPE
    assert kwargs['text'] is True

def test_get_commit_history_failure(git_service: LocalGitService, mocker) -> None:
    # Mock subprocess.Popen to simulate failure (non-zero exit code)
    mock_popen = mocker.patch('subprocess.Popen')
    mock_process = MagicMock()
    mock_process.stdout = iter([])
    mock_process.wait.return_value = 1
    mock_process.returncode = 1
    mock_process.__enter__.return_value = mock_process
    mock_popen.return_value = mock_process

    # Execute and expect CalledProcessError
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        list(git_service.get_commit_history(2))

    assert excinfo.value.returncode == 1

def test_get_commit_history_os_error(git_service: LocalGitService, mocker) -> None:
    # Mock subprocess.Popen to raise OSError (e.g. git not found)
    mocker.patch('subprocess.Popen', side_effect=OSError("git not found"))

    with pytest.raises(OSError, match="git not found"):
        list(git_service.get_commit_history(2))
