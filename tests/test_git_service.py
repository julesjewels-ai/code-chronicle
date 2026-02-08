import pytest
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def git_service():
    return LocalGitService("/test/repo")

@pytest.mark.parametrize("stdout_lines, expected_commits", [
    # Normal case: single commit
    (["abc1234|Initial commit\n"], [Commit("abc1234", "Initial commit")]),
    # Normal case: multiple commits
    (
        ["abc1234|Initial commit\n", "def5678|Second commit\n"],
        [Commit("abc1234", "Initial commit"), Commit("def5678", "Second commit")]
    ),
    # Edge case: empty output
    ([], []),
    # Edge case: malformed line (missing |)
    (["invalid line\n"], []),
    # Edge case: mixed malformed and valid
    (["abc|msg\n", "invalid\n", "def|msg2\n"], [Commit("abc", "msg"), Commit("def", "msg2")]),
    # Edge case: empty message (trailing newline only)
    (["abc|\n"], [Commit("abc", "")]),
    # Edge case: no trailing newline (truncation behavior due to optimization)
    (["abc|message"], [Commit("abc", "messag")]),
])
def test_get_commit_history(git_service, mocker, stdout_lines, expected_commits):
    # Mock subprocess.Popen
    mock_process = MagicMock()
    mock_process.stdout = iter(stdout_lines)
    mock_process.wait.return_value = 0
    mock_process.__enter__.return_value = mock_process
    mock_process.returncode = 0

    # Since subprocess is imported locally in the method, we mock it in sys.modules
    # verify=True ensures we only mock existing attributes
    mock_popen = mocker.patch("subprocess.Popen", return_value=mock_process)

    # Act
    commits = list(git_service.get_commit_history(limit=5))

    # Assert
    assert commits == expected_commits

    # Verify Popen call
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    expected_cmd = ["git", "-C", "/test/repo", "log", "-n", "5", "--pretty=tformat:%h|%s"]
    assert args[0] == expected_cmd
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["text"] is True

def test_get_commit_history_subprocess_error(git_service, mocker):
    # Mock subprocess.Popen to fail
    mock_process = MagicMock()
    mock_process.stdout = iter([])
    mock_process.wait.return_value = 1
    mock_process.returncode = 1
    mock_process.__enter__.return_value = mock_process

    mocker.patch("subprocess.Popen", return_value=mock_process)

    # Act & Assert
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        list(git_service.get_commit_history(limit=5))

    assert exc_info.value.returncode == 1
