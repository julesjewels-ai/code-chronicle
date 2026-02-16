from unittest.mock import MagicMock
from src.services.llm import OpenAILLMService, MockLLMService
from src.models import Commit
from openai import OpenAIError

def test_mock_llm_service():
    service = MockLLMService()
    commit = Commit(hash_id="123", message="feat: add something")
    analysis = service.analyze_commit(commit)
    assert "LLM Analysis:" in analysis
    assert "feat: add something" in analysis

def test_openai_llm_service_success(mocker):
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()

    mock_message.content = "Analysis result."
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_completion

    # Patch OpenAI constructor to return our mock client
    mocker.patch("src.services.llm.OpenAI", return_value=mock_client)

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc", message="fix: bug")

    result = service.analyze_commit(commit)

    assert result == "Analysis result."
    mock_client.chat.completions.create.assert_called_once()

def test_openai_llm_service_failure(mocker):
    # Mock OpenAI client raising error
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

    mocker.patch("src.services.llm.OpenAI", return_value=mock_client)

    service = OpenAILLMService(api_key="test-key")
    commit = Commit(hash_id="abc", message="fix: bug")

    result = service.analyze_commit(commit)

    assert "Error analyzing commit: API Error" in result
