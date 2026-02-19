import pytest
from unittest.mock import MagicMock
from src.services.openai_service import OpenAILLMService
from src.models import Commit

@pytest.fixture
def mock_openai(mocker):
    # Mock the OpenAI class imported in src.services.openai_service
    return mocker.patch('src.services.openai_service.OpenAI')

def test_initialization(mock_openai):
    service = OpenAILLMService(api_key="test-key")
    mock_openai.assert_called_once_with(api_key="test-key")
    assert service.client == mock_openai.return_value

def test_analyze_commit_success(mock_openai):
    # Setup mock response
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis result"
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="Fix bug")

    result = service.analyze_commit(commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs['model'] == "gpt-4o"
    assert "Fix bug" in kwargs['messages'][1]['content']

def test_analyze_commit_api_error(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="Fix bug")

    result = service.analyze_commit(commit)

    assert "Error analyzing commit: API Error" in result

def test_analyze_commit_empty_response(mock_openai):
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = ""
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="Fix bug")

    result = service.analyze_commit(commit)

    assert result == "No analysis generated."
