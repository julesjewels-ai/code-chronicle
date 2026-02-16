import pytest
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def git_service() -> LocalGitService:
    return LocalGitService("/tmp/repo")

@pytest.mark.parametrize("limit, stdout_lines, return_code, expected_result", [
    (
        2,
        ["h1|m1\n", "h2|m2\n"],
        0,
        [Commit(hash_id="h1", message="m1"), Commit(hash_id="h2", message="m2")]
    ),
    (
        5,
        [],
        0,
        []
    ),
    (
        3,
        ["h1|m1\n", "invalid_line\n", "h3|m3\n"],
        0,
        [Commit(hash_id="h1", message="m1"), Commit(hash_id="h3", message="m3")]
    ),
    (
        2,
        [],
        1,
        subprocess.CalledProcessError
    )
])
def test_get_commit_history(
    git_service: LocalGitService,
    mocker,
    limit: int,
    stdout_lines: list[str],
    return_code: int,
    expected_result: list[Commit] | type[Exception]
) -> None:
    # Arrange
    mock_popen = mocker.patch("subprocess.Popen")
    process_mock = MagicMock()
    # Mock context manager behavior
    process_mock.__enter__.return_value = process_mock
    process_mock.__exit__.return_value = None

    # Mock stdout iterator
    process_mock.stdout = iter(stdout_lines)

    # Mock return code behavior
    process_mock.wait.return_value = return_code
    process_mock.returncode = return_code

    mock_popen.return_value = process_mock

    # Act & Assert
    if isinstance(expected_result, type) and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            list(git_service.get_commit_history(limit))
    else:
        commits = list(git_service.get_commit_history(limit))
        assert commits == expected_result

        # Verify subprocess call arguments
        args, kwargs = mock_popen.call_args
        expected_cmd = ["git", "-C", "/tmp/repo", "log", "-n", str(limit), "--pretty=tformat:%h|%s"]
        assert args[0] == expected_cmd
        assert kwargs.get("stdout") == subprocess.PIPE
        assert kwargs.get("text") is True
