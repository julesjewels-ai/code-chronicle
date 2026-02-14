from unittest.mock import MagicMock, patch
from src.services.llm import OpenAILLMService, MockLLMService
from src.models import Commit
from openai import OpenAIError

def test_mock_llm_service():
    service = MockLLMService()
    commit = Commit(hash_id="123", message="feat: add something")
    result = service.analyze_commit(commit)
    assert "LLM Analysis:" in result
    assert "feat: add something" in result

@patch("src.services.llm.OpenAI")
def test_openai_llm_service_success(mock_openai):
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Analysis result"))]
    mock_client.chat.completions.create.return_value = mock_completion

    service = OpenAILLMService(api_key="sk-test", model="gpt-3.5-turbo")
    commit = Commit(hash_id="abc", message="fix: bug")

    result = service.analyze_commit(commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-3.5-turbo"
    assert len(kwargs["messages"]) == 2
    assert "fix: bug" in kwargs["messages"][1]["content"]

@patch("src.services.llm.OpenAI")
def test_openai_llm_service_error(mock_openai):
    # Setup mock to raise error
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

    service = OpenAILLMService(api_key="sk-test")
    commit = Commit(hash_id="abc", message="fix: bug")

    result = service.analyze_commit(commit)

    assert "Error analyzing commit: API Error" in result

@patch("src.services.llm.OpenAI")
def test_openai_llm_service_empty_response(mock_openai):
    # Setup mock to return empty content
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=None))]
    mock_client.chat.completions.create.return_value = mock_completion

    service = OpenAILLMService(api_key="sk-test")
    commit = Commit(hash_id="abc", message="fix: bug")

    result = service.analyze_commit(commit)

    assert result == ""

@patch("src.services.llm.OpenAI")
def test_openai_llm_service_no_choices(mock_openai):
    # Setup mock to return empty choices
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_completion = MagicMock()
    mock_completion.choices = []
    mock_client.chat.completions.create.return_value = mock_completion

    service = OpenAILLMService(api_key="sk-test")
    commit = Commit(hash_id="abc", message="fix: bug")

    result = service.analyze_commit(commit)

    assert result == "Error: No analysis returned."
