import pytest  # type: ignore
from unittest.mock import MagicMock
from src.services.llm import OpenAILLMService, MockLLMService
from src.models import Commit
from openai import OpenAIError

@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("src.services.llm.OpenAI")

def test_mock_llm_service():
    service = MockLLMService()
    commit = Commit(hash_id="abc", message="fix bug")
    result = service.analyze_commit(commit)
    assert "LLM Analysis" in result
    assert "fix bug" in result

def test_openai_llm_service_init(mock_openai):
    service = OpenAILLMService(api_key="test_key", model="gpt-4-test")
    mock_openai.assert_called_once_with(api_key="test_key")
    assert service.model == "gpt-4-test"

def test_openai_llm_service_analyze_success(mock_openai):
    # Setup mock response
    mock_client = mock_openai.return_value
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "Analysis result."
    mock_client.chat.completions.create.return_value = mock_completion

    service = OpenAILLMService(api_key="key")
    commit = Commit(hash_id="abc", message="feat: add feature")

    result = service.analyze_commit(commit)

    assert result == "Analysis result."
    mock_client.chat.completions.create.assert_called_once()

    # Check if correct arguments were passed
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs['model'] == "gpt-4o"
    assert call_args.kwargs['messages'][1]['content'] == "feat: add feature"

def test_openai_llm_service_analyze_api_error(mock_openai):
    mock_client = mock_openai.return_value
    # Use OpenAIError constructor if possible, or just mock the exception raising
    mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

    service = OpenAILLMService(api_key="key")
    commit = Commit(hash_id="abc", message="msg")

    result = service.analyze_commit(commit)

    assert "Error analyzing commit: API Error" in result
