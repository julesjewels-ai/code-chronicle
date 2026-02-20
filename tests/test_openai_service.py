import pytest
from unittest.mock import MagicMock
from src.models import Commit
from src.services.openai_service import OpenAILLMService

@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("src.services.openai_service.OpenAI")

@pytest.fixture
def service(mock_openai):
    # We must set the env var or pass api_key
    return OpenAILLMService(api_key="test-key")

def test_init_raises_without_key(mocker):
    mocker.patch.dict("os.environ", {}, clear=True)
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        OpenAILLMService()

def test_init_with_env_key(mocker, mock_openai):
    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"})
    service = OpenAILLMService()
    assert service.api_key == "env-key"
    mock_openai.assert_called_once_with(api_key="env-key")

def test_analyze_commit_success(service, mock_openai):
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis result"
    mock_client.chat.completions.create.return_value = mock_response

    commit = Commit(hash_id="123", message="feat: test")
    result = service.analyze_commit(commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()

    # Check arguments
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs['model'] == "gpt-4o"
    assert kwargs['messages'][0]['role'] == "user"
    assert "feat: test" in kwargs['messages'][0]['content']

def test_analyze_commit_api_error(service, mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    commit = Commit(hash_id="123", message="feat: test")
    result = service.analyze_commit(commit)

    assert "Analysis failed: API Error" in result

def test_analyze_commit_empty_response(service, mock_openai):
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = ""
    mock_client.chat.completions.create.return_value = mock_response

    commit = Commit(hash_id="123", message="feat: test")
    result = service.analyze_commit(commit)

    assert result == "No analysis returned."
