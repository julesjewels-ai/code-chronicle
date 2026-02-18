import pytest
from unittest.mock import MagicMock, patch
from src.services.openai_service import OpenAILLMService
from src.models import Commit

@pytest.fixture
def mock_openai():
    with patch('src.services.openai_service.OpenAI') as mock:
        yield mock

def test_analyze_commit_success(mock_openai):
    # Setup mock response
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Analysis result."
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="Fix bug")
    result = service.analyze_commit(commit)

    assert result == "Analysis result."
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs['model'] == "gpt-4o"
    assert "Fix bug" in kwargs['messages'][1]['content']

def test_analyze_commit_error(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="Fix bug")
    result = service.analyze_commit(commit)

    assert result == "Error analyzing commit: API Error"

def test_analyze_commit_no_content(mock_openai):
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = None
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc1234", message="Fix bug")
    result = service.analyze_commit(commit)

    assert result == "Error: No content returned."
