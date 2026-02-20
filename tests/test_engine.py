import pytest  # type: ignore
from unittest.mock import MagicMock
from src.core.engine import ChronicleGenerator
from src.models import Commit, AnalyzedCommit
from src.interfaces import GitProvider, LLMProvider
from pytest_mock import MockerFixture  # type: ignore

@pytest.fixture
def mock_git_provider(mocker: MockerFixture) -> MagicMock:
    return mocker.Mock(spec=GitProvider)

@pytest.fixture
def mock_llm_provider(mocker: MockerFixture) -> MagicMock:
    return mocker.Mock(spec=LLMProvider)

@pytest.fixture
def generator(mock_git_provider: MagicMock, mock_llm_provider: MagicMock) -> ChronicleGenerator:
    return ChronicleGenerator(mock_git_provider, mock_llm_provider)

@pytest.mark.parametrize("git_behavior, llm_behavior, expected_outcome", [
    # Happy Path: Single commit
    (
        [Commit("h1", "msg1")],
        ["analysis1"],
        [AnalyzedCommit(Commit("h1", "msg1"), "analysis1")]
    ),
    # Happy Path: Multiple commits
    (
        [Commit("h1", "msg1"), Commit("h2", "msg2")],
        ["analysis1", "analysis2"],
        [
            AnalyzedCommit(Commit("h1", "msg1"), "analysis1"),
            AnalyzedCommit(Commit("h2", "msg2"), "analysis2")
        ]
    ),
    # Empty History
    (
        [],
        [],
        []
    ),
    # Git Failure (Exception raised during history retrieval)
    (
        ValueError("Git Error"),
        None,
        ValueError
    ),
    # LLM Failure (Exception raised during analysis)
    (
        [Commit("h1", "msg1")],
        RuntimeError("LLM Error"),
        RuntimeError
    ),
])
def test_generate(
    generator: ChronicleGenerator,
    mock_git_provider: MagicMock,
    mock_llm_provider: MagicMock,
    git_behavior: list[Commit] | Exception,
    llm_behavior: list[str] | Exception | None,
    expected_outcome: list[AnalyzedCommit] | type[Exception]
) -> None:
    # Arrange
    if isinstance(git_behavior, Exception):
        mock_git_provider.get_commit_history.side_effect = git_behavior
    else:
        mock_git_provider.get_commit_history.return_value = iter(git_behavior)

    if isinstance(llm_behavior, Exception):
        mock_llm_provider.analyze_commit.side_effect = llm_behavior
    elif llm_behavior is not None:
        mock_llm_provider.analyze_commit.side_effect = llm_behavior

    # Act & Assert
    if isinstance(expected_outcome, type) and issubclass(expected_outcome, Exception):
        with pytest.raises(expected_outcome):
            # Convert generator to list to force execution
            list(generator.generate(limit=5))
    else:
        # Determine limit based on history length for consistent assertion
        limit_arg = len(expected_outcome) if expected_outcome else 5

        results = list(generator.generate(limit=limit_arg))
        assert results == expected_outcome

        # Verify calls
        mock_git_provider.get_commit_history.assert_called_once_with(limit_arg)
        if llm_behavior is not None:
             assert mock_llm_provider.analyze_commit.call_count == len(expected_outcome)
