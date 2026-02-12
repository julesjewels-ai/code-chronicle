from unittest.mock import MagicMock
from src.services.llm import MockLLMService, OpenAILLMService
from src.models import Commit

def test_mock_llm_service():
    service = MockLLMService()
    commit = Commit(hash_id="123", message="test message")
    analysis = service.analyze_commit(commit)
    assert "test message" in analysis

def test_openai_llm_service(mocker):
    # Mock OpenAI client
    mock_openai_class = mocker.patch("openai.OpenAI")
    mock_client = mock_openai_class.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis result"
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="test-key", model="gpt-4o")
    commit = Commit(hash_id="123", message="test message")

    analysis = service.analyze_commit(commit)

    assert analysis == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()
    assert mock_client.chat.completions.create.call_args[1]['model'] == "gpt-4o"

def test_openai_llm_service_error(mocker):
    # Mock OpenAI client to raise exception
    mock_openai_class = mocker.patch("openai.OpenAI")
    mock_client = mock_openai_class.return_value
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    service = OpenAILLMService(api_key="test-key", model="gpt-4o")
    commit = Commit(hash_id="123", message="test message")

    analysis = service.analyze_commit(commit)

    assert "Error analyzing commit: API Error" in analysis
