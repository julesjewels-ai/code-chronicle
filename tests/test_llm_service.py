import pytest  # type: ignore
from unittest.mock import MagicMock
from src.services.llm import OpenAILLMService, MockLLMService
from src.models import Commit

@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("src.services.llm.OpenAI")

def test_mock_llm_service():
    service = MockLLMService()
    commit = Commit(hash_id="abc", message="fix bug")
    assert "LLM Analysis" in service.analyze_commit(commit)

def test_openai_llm_service_init(mock_openai):
    service = OpenAILLMService(api_key="sk-test", model="gpt-4")
    mock_openai.assert_called_with(api_key="sk-test")
    assert service.model == "gpt-4"

def test_openai_llm_service_analyze(mock_openai):
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Analysis result"
    mock_client.chat.completions.create.return_value = mock_response

    service = OpenAILLMService(api_key="sk-test")
    commit = Commit(hash_id="abc", message="feature: add login")

    result = service.analyze_commit(commit)

    assert result == "Analysis result"
    mock_client.chat.completions.create.assert_called_once()

    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o"  # default
    assert "messages" in kwargs
    assert kwargs["messages"][1]["content"].endswith("feature: add login")

def test_openai_llm_service_error(mock_openai):
    from openai import OpenAIError
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

    service = OpenAILLMService(api_key="sk-test")
    commit = Commit(hash_id="abc", message="msg")

    result = service.analyze_commit(commit)

    assert "Error generating analysis" in result
    assert "API Error" in result
