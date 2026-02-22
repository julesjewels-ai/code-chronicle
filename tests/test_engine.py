import pytest  # type: ignore
from src.core.engine import ChronicleGenerator
from src.models import Commit, AnalyzedCommit

@pytest.fixture
def mock_dependencies(mocker):
    mock_git = mocker.Mock()
    mock_llm = mocker.Mock()
    return mock_git, mock_llm

@pytest.mark.parametrize("limit, commit_count", [
    (1, 1),
    (5, 3), # limit 5, but 3 commits available
    (0, 0)
])
def test_generate(mock_dependencies, limit, commit_count):
    mock_git, mock_llm = mock_dependencies

    # Prepare dummy commits
    commits = [
        Commit(hash_id=f"h{i}", message=f"msg{i}")
        for i in range(commit_count)
    ]
    mock_git.get_commit_history.return_value = commits
    mock_llm.analyze_commit.side_effect = lambda c: f"analysis for {c.hash_id}"

    generator = ChronicleGenerator(mock_git, mock_llm)
    results = list(generator.generate(limit=limit))

    assert len(results) == commit_count
    for i, res in enumerate(results):
        assert isinstance(res, AnalyzedCommit)
        assert res.commit.hash_id == f"h{i}"
        assert res.analysis == f"analysis for h{i}"

    mock_git.get_commit_history.assert_called_with(limit)
    assert mock_llm.analyze_commit.call_count == commit_count
