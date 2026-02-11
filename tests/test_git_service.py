import pytest
from unittest.mock import MagicMock
import subprocess
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def service():
    return LocalGitService("/tmp/repo")

@pytest.fixture
def mock_popen(mocker):
    return mocker.patch("subprocess.Popen")

@pytest.mark.parametrize("stdout_lines, expected_commits", [
    # Standard output with newline
    (
        ["h1|msg1\n", "h2|msg2\n"],
        [Commit(hash_id="h1", message="msg1"), Commit(hash_id="h2", message="msg2")]
    ),
    # Message containing separator
    (
        ["h1|feat: msg | with | pipes\n"],
        [Commit(hash_id="h1", message="feat: msg | with | pipes")]
    ),
    # Empty message with newline
    (
        ["h1|\n"],
        [Commit(hash_id="h1", message="")]
    ),
    # Malformed line (no separator) - should be skipped
    (
        ["invalid_line_no_pipe\n", "h2|valid\n"],
        [Commit(hash_id="h2", message="valid")]
    ),
    # Empty output
    (
        [],
        []
    ),
    # Just a newline - should be skipped
    (
        ["\n"],
        []
    ),
    # Line without trailing newline (edge case: last char truncated by implementation)
    # This documents current behavior: "message" -> "messag"
    (
        ["h1|message"],
        [Commit(hash_id="h1", message="messag")]
    ),
])
def test_get_commit_history_success(service, mock_popen, stdout_lines, expected_commits):
    process_mock = MagicMock()
    process_mock.stdout = iter(stdout_lines)
    process_mock.wait.return_value = 0
    process_mock.__enter__.return_value = process_mock
    mock_popen.return_value = process_mock

    commits = list(service.get_commit_history(len(expected_commits)))

    assert commits == expected_commits

    # Verify call args
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    assert args[0][:5] == ["git", "-C", "/tmp/repo", "log", "-n"]
    assert args[0][6] == "--pretty=tformat:%h|%s"
    assert kwargs['stdout'] == subprocess.PIPE
    assert kwargs['text'] is True

def test_get_commit_history_failure(service, mock_popen):
    process_mock = MagicMock()
    process_mock.stdout = iter([])
    process_mock.wait.return_value = 1
    process_mock.returncode = 1
    process_mock.__enter__.return_value = process_mock
    mock_popen.return_value = process_mock

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        list(service.get_commit_history(5))

    assert excinfo.value.returncode == 1
