import pytest
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService

@pytest.fixture
def service():
    return LocalGitService("/tmp/repo")

@pytest.mark.parametrize("stdout_content, expected_hashes, expected_messages, should_raise, expected_exception, return_code", [
    # Happy path: normal commits
    (
        "abc1234|Initial commit\ndef5678|Second commit\n",
        ["abc1234", "def5678"],
        ["Initial commit", "Second commit"],
        False, None, 0
    ),
    # Edge case: No commits (empty output)
    (
        "",
        [],
        [],
        False, None, 0
    ),
    # Edge case: Malformed line (missing separator) -> should be skipped
    (
        "invalid_line_no_separator\nabc1234|Valid commit\n",
        ["abc1234"],
        ["Valid commit"],
        False, None, 0
    ),
    # Edge case: Empty message (separator present, empty part after)
    (
        "abc1234|\n",
        ["abc1234"],
        [""], # "|\n" -> parts[2] is "\n", [:-1] is ""
        False, None, 0
    ),
    # Edge case: Special characters in message
    (
        "abc1234|Fix: Issue #123 with special chars! @#$%^&*\n",
        ["abc1234"],
        ["Fix: Issue #123 with special chars! @#$%^&*"],
        False, None, 0
    ),
    # Edge case: Missing trailing newline (optimization truncation side-effect)
    # The code uses [:-1] which blindly removes the last character.
    (
        "abc1234|Truncated message",
        ["abc1234"],
        ["Truncated messag"],
        False, None, 0
    ),
    # Failure case: git returns non-zero exit code
    (
        "",
        [],
        [],
        True, subprocess.CalledProcessError, 1
    ),
])
def test_get_commit_history(
    service, mocker, stdout_content, expected_hashes, expected_messages, should_raise, expected_exception, return_code
):
    # Mock subprocess.Popen
    process_mock = MagicMock()
    # Popen context manager setup
    process_mock.__enter__.return_value = process_mock
    process_mock.__exit__.return_value = None

    # Simulate stdout as an iterator of lines
    def line_generator(content):
        if not content:
            return
        lines = content.splitlines(keepends=True)
        # Handle the case where the last line doesn't have a newline but splitlines might not show it if not careful
        # splitlines(keepends=True) keeps the newline if present.
        # "abc".splitlines(keepends=True) -> ["abc"]
        for line in lines:
            yield line

    process_mock.stdout = line_generator(stdout_content)
    process_mock.wait.return_value = return_code
    process_mock.returncode = return_code

    # Patch subprocess.Popen
    # We patch it where it is used. Since it's imported inside the function,
    # we patch the subprocess module itself which is globally cached.
    mock_popen = mocker.patch("subprocess.Popen", return_value=process_mock)

    if should_raise:
        with pytest.raises(expected_exception):
            list(service.get_commit_history(5))
    else:
        commits = list(service.get_commit_history(5))
        assert len(commits) == len(expected_hashes)
        for i, commit in enumerate(commits):
            assert commit.hash_id == expected_hashes[i]
            assert commit.message == expected_messages[i]

    # Verify Popen arguments
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    assert args[0][:5] == ["git", "-C", "/tmp/repo", "log", "-n"]
    assert args[0][6] == "--pretty=tformat:%h|%s"
    assert kwargs["stdout"] == subprocess.PIPE
    assert kwargs["text"] is True

def test_get_commit_history_file_not_found(service, mocker):
    # Test FileNotFoundError (git not installed or other OS error)
    mocker.patch("subprocess.Popen", side_effect=FileNotFoundError)
    with pytest.raises(FileNotFoundError):
        list(service.get_commit_history(5))
