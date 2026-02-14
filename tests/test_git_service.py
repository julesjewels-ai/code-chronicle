import subprocess
import pytest
from src.services.git import LocalGitService

@pytest.fixture
def service():
    return LocalGitService("/tmp/repo")

@pytest.fixture
def mock_popen(mocker):
    # Mock subprocess.Popen context manager
    process_mock = mocker.MagicMock()
    process_mock.__enter__.return_value = process_mock
    process_mock.__exit__.return_value = None
    return mocker.patch("subprocess.Popen", return_value=process_mock)

@pytest.mark.parametrize("stdout_lines, expected_commits", [
    (
        ["h1|m1\n", "h2|m2\n"],
        [("h1", "m1"), ("h2", "m2")]
    ),
    (
        ["h3|m3\n", "h4|m4"], # Truncated output
        [("h3", "m3"), ("h4", "m4")]
    ),
    (
        ["invalid_line\n", "h5|m5\n"], # Malformed output
        [("h5", "m5")]
    ),
    (
        [], # Empty output
        []
    )
], ids=["standard", "truncated", "malformed", "empty"])
def test_get_commit_history_parsing(service, mock_popen, stdout_lines, expected_commits):
    process_mock = mock_popen.return_value.__enter__.return_value
    process_mock.stdout = iter(stdout_lines)
    process_mock.wait.return_value = 0

    commits = list(service.get_commit_history(2))

    assert len(commits) == len(expected_commits)
    for commit, (expected_hash, expected_msg) in zip(commits, expected_commits):
        assert commit.hash_id == expected_hash
        assert commit.message == expected_msg

def test_get_commit_history_failure(service, mock_popen):
    process_mock = mock_popen.return_value.__enter__.return_value
    process_mock.stdout = iter([])
    process_mock.wait.return_value = 1
    process_mock.returncode = 1

    with pytest.raises(subprocess.CalledProcessError):
        list(service.get_commit_history(2))
