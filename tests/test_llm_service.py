import pytest
from unittest.mock import MagicMock, patch
from src.services.llm import OpenAILLMService, MockLLMService
from src.models import Commit
import openai

@pytest.fixture
def mock_commit():
    return Commit(hash_id="abcdef", message="Test commit")

def test_mock_llm_service(mock_commit):
    service = MockLLMService()
    analysis = service.analyze_commit(mock_commit)
    assert "LLM Analysis" in analysis
    assert "Test commit" in analysis

@patch("src.services.llm.openai.OpenAI")
def test_openai_llm_service_init(mock_openai):
    service = OpenAILLMService(api_key="test-key", model="gpt-4")
    assert service.model == "gpt-4"
    mock_openai.assert_called_once_with(api_key="test-key")

@patch("src.services.llm.openai.OpenAI")
def test_openai_llm_service_analyze_success(mock_openai_class, mock_commit):
    # Setup mock client and response
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Analysis result"))]
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key")
    result = service.analyze_commit(mock_commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()

    # Verify call args
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-3.5-turbo" # Default
    assert len(call_args.kwargs["messages"]) == 2
    assert "Test commit" in call_args.kwargs["messages"][1]["content"]

@patch("src.services.llm.openai.OpenAI")
def test_openai_llm_service_api_error(mock_openai_class, mock_commit):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # We need to construct an APIError properly
    err = openai.APIError("API Error Message", request=None, body=None)
    mock_client.chat.completions.create.side_effect = err

    service = OpenAILLMService(api_key="test-key")
    result = service.analyze_commit(mock_commit)

    assert "OpenAI API Error" in result
    assert "API Error Message" in result

@patch("src.services.llm.openai.OpenAI")
def test_openai_llm_service_generic_error(mock_openai_class, mock_commit):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_client.chat.completions.create.side_effect = Exception("Generic failure")

    service = OpenAILLMService(api_key="test-key")
    result = service.analyze_commit(mock_commit)

    assert "Error analyzing commit" in result
    assert "Generic failure" in result
