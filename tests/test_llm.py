import json
from unittest.mock import MagicMock, patch
from src.services.llm import MockLLMService, OpenAILLMService
from src.models import Commit
from urllib.error import HTTPError

def test_mock_llm_service():
    service = MockLLMService()
    commit = Commit(hash_id="abc", message="feat: add thing")
    result = service.analyze_commit(commit)
    assert result == "LLM Analysis: This change evolves the codebase by 'feat: add thing'."

@patch("urllib.request.urlopen")
def test_openai_llm_service_success(mock_urlopen):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "choices": [
            {
                "message": {
                    "content": "Analysis result."
                }
            }
        ]
    }).encode("utf-8")
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    mock_urlopen.return_value = mock_response

    service = OpenAILLMService(api_key="fake-key")
    commit = Commit(hash_id="abc", message="feat: add thing")

    result = service.analyze_commit(commit)

    assert result == "Analysis result."

    # Verify request
    mock_urlopen.assert_called_once()
    args, _ = mock_urlopen.call_args
    req = args[0]
    assert req.full_url == "https://api.openai.com/v1/chat/completions"
    assert req.headers["Authorization"] == "Bearer fake-key"
    assert req.method == "POST"

    # Verify payload
    data = json.loads(req.data)
    assert data["model"] == "gpt-4o-mini"
    assert "messages" in data

@patch("urllib.request.urlopen")
def test_openai_llm_service_http_error(mock_urlopen):
    # Setup mock error
    mock_urlopen.side_effect = HTTPError(
        url="http://api.openai.com",
        code=401,
        msg="Unauthorized",
        hdrs={},
        fp=None
    )

    service = OpenAILLMService(api_key="fake-key")
    commit = Commit(hash_id="abc", message="feat: add thing")

    result = service.analyze_commit(commit)

    assert "Error calling OpenAI API: HTTP 401 - Unauthorized" in result

@patch("urllib.request.urlopen")
def test_openai_llm_service_generic_error(mock_urlopen):
    mock_urlopen.side_effect = Exception("Network down")

    service = OpenAILLMService(api_key="fake-key")
    commit = Commit(hash_id="abc", message="feat: add thing")

    result = service.analyze_commit(commit)

    assert "Error calling OpenAI API: Network down" in result
