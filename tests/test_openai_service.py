import pytest
from unittest.mock import MagicMock
from src.services.openai_service import OpenAILLMService
from src.models import Commit

@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("src.services.openai_service.OpenAI")

def test_init(mock_openai):
    service = OpenAILLMService("test_key")
    mock_openai.assert_called_once_with(api_key="test_key")
    assert service.client == mock_openai.return_value
    assert service.model == "gpt-4o"

def test_analyze_commit(mock_openai):
    service = OpenAILLMService("test_key")
    mock_client = mock_openai.return_value

    # Mock response structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Analysis result"))]
    mock_client.chat.completions.create.return_value = mock_response

    commit = Commit(hash_id="123", message="Initial commit")
    result = service.analyze_commit(commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer. Analyze the following commit message and describe its impact on the codebase."},
            {"role": "user", "content": "Analyze this commit message: 'Initial commit'"}
        ]
    )

def test_analyze_commit_empty_response(mock_openai):
    service = OpenAILLMService("test_key")
    mock_client = mock_openai.return_value

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None))]
    mock_client.chat.completions.create.return_value = mock_response

    commit = Commit(hash_id="123", message="Initial commit")
    result = service.analyze_commit(commit)

    assert result == ""
