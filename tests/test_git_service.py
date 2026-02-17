import pytest  # type: ignore
import subprocess
from unittest.mock import MagicMock
from src.services.git import LocalGitService
from src.models import Commit

@pytest.fixture
def git_service() -> LocalGitService:
    return LocalGitService("/tmp/repo")

@pytest.mark.parametrize("stdout_lines, return_code, expected_commits, expected_exception", [
    (
        ["h1|m1\n", "h2|m2\n"],
        0,
        [Commit(hash_id="h1", message="m1"), Commit(hash_id="h2", message="m2")],
        None
    ),
    (
        [],
        0,
        [],
        None
    ),
    (
        ["malformed line\n", "h3|m3\n"],
        0,
        [Commit(hash_id="h3", message="m3")],
        None
    ),
    (
        [],
        1,
        None,
        subprocess.CalledProcessError
    )
])
def test_get_commit_history(
    mocker,
    git_service: LocalGitService,
    stdout_lines: list[str],
    return_code: int,
    expected_commits: list[Commit] | None,
    expected_exception: type[Exception] | None
) -> None:
    # Arrange
    mock_process = MagicMock()
    mock_process.stdout = iter(stdout_lines)
    mock_process.wait.return_value = return_code
    mock_process.returncode = return_code
    mock_process.__enter__.return_value = mock_process

    mock_popen = mocker.patch('subprocess.Popen', return_value=mock_process)

    # Act & Assert
    if expected_exception:
        with pytest.raises(expected_exception):
            list(git_service.get_commit_history(5))
    else:
        commits = list(git_service.get_commit_history(5))
        assert commits == expected_commits

        # Verify Popen called correctly
        args, kwargs = mock_popen.call_args
        assert args[0][:5] == ["git", "-C", "/tmp/repo", "log", "-n"]
        assert args[0][6] == "--pretty=tformat:%h|%s"
        assert kwargs['stdout'] == subprocess.PIPE
        assert kwargs['text'] is True
