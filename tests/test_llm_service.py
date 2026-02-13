import pytest  # type: ignore
from unittest.mock import MagicMock, patch
from src.services.llm import OpenAILLMService
from src.models import Commit

@pytest.fixture
def mock_openai():
    with patch("src.services.llm.openai.OpenAI") as mock:
        yield mock

def test_openai_service_init(mock_openai):
    service = OpenAILLMService(api_key="test-key", model="test-model")
    mock_openai.assert_called_once_with(api_key="test-key")
    assert service.model == "test-model"

def test_openai_analyze_commit_success(mock_openai):
    # Setup mock
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis result"
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="feat: add login")

    result = service.analyze_commit(commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-4o"  # Default model
    # Message at index 0 is system, index 1 is user prompt
    assert "feat: add login" in call_args.kwargs["messages"][1]["content"]

def test_openai_analyze_commit_custom_model(mock_openai):
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis"
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="k", model="gpt-3.5-turbo")
    commit = Commit(hash_id="123", message="msg")

    service.analyze_commit(commit)

    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-3.5-turbo"

def test_openai_analyze_commit_error(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    service = OpenAILLMService(api_key="k")
    commit = Commit(hash_id="123", message="msg")

    # Depending on implementation, it might raise or return error string.
    # Plan said "Handle exceptions and return an error string".
    # So we assert it returns a string containing error info.
    result = service.analyze_commit(commit)

    assert "Error" in result or "unavailable" in result
