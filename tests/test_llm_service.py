import pytest
from unittest.mock import MagicMock, patch
from src.services.llm import OpenAILLMService
from src.models import Commit

@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        yield mock

def test_analyze_commit(mock_openai):
    # Setup mock
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis result"
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="key", model="gpt-4o")
    commit = Commit(hash_id="h1", message="feat: add thing", diff="diff content")

    result = service.analyze_commit(commit)

    assert result == "Analysis result"

    # Verify call
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs['model'] == "gpt-4o"
    assert len(kwargs['messages']) == 2
    assert "diff content" in kwargs['messages'][1]['content']
