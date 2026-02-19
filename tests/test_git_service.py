import pytest  # type: ignore
from unittest.mock import MagicMock
from src.services.git import LocalGitService
import subprocess
from pytest_mock import MockerFixture  # type: ignore

@pytest.fixture
def local_git_service() -> LocalGitService:
    return LocalGitService("/tmp/repo")

@pytest.mark.parametrize("stdout_lines, return_code, expected_commits, expected_error", [
    # Standard case
    (
        ["h1|msg1\n", "h2|msg2\n"],
        0,
        [("h1", "msg1"), ("h2", "msg2")],
        None
    ),
    # Truncated/Malformed output (missing |)
    (
        ["h1|msg1\n", "invalid_line\n", "h3|msg3\n"],
        0,
        [("h1", "msg1"), ("h3", "msg3")],
        None
    ),
    # Empty output
    (
        [],
        0,
        [],
        None
    ),
    # Whitespace/Newline handling
    (
        ["h1|msg1 \n", "h2|msg2\n\n"],  # Note: logic slices [:-1], so trailing \n is removed.
        0,
        [("h1", "msg1 "), ("h2", "msg2\n")], # strict slicing check
        None
    ),
    # Unicode support
    (
        ["h1|café\n", "h2|emoji 🚀\n"],
        0,
        [("h1", "café"), ("h2", "emoji 🚀")],
        None
    ),
    # Error case
    (
        [],
        1,
        [],
        subprocess.CalledProcessError
    )
])
def test_get_commit_history(
    local_git_service: LocalGitService,
    mocker: MockerFixture,
    stdout_lines: list[str],
    return_code: int,
    expected_commits: list[tuple[str, str]],
    expected_error: type[Exception] | None
) -> None:
    # Arrange
    mock_process = MagicMock()
    mock_process.stdout = iter(stdout_lines)
    mock_process.wait.return_value = return_code
    mock_process.returncode = return_code
    mock_process.__enter__.return_value = mock_process

    # Patch subprocess.Popen globally since it's imported inside the method
    mock_popen = mocker.patch('subprocess.Popen', return_value=mock_process)

    # Act & Assert
    if expected_error:
        with pytest.raises(expected_error):
            list(local_git_service.get_commit_history(limit=5))
    else:
        commits = list(local_git_service.get_commit_history(limit=5))
        assert len(commits) == len(expected_commits)
        for commit, (expected_hash, expected_msg) in zip(commits, expected_commits):
            assert commit.hash_id == expected_hash
            assert commit.message == expected_msg

    # Verify Popen call arguments
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    # args[0] is the command list
    assert args[0][:5] == ["git", "-C", "/tmp/repo", "log", "-n"]
    assert args[0][6] == "--pretty=tformat:%h|%s"
    assert kwargs['stdout'] == subprocess.PIPE
    assert kwargs['text'] is True
