import pytest  # type: ignore
from unittest.mock import MagicMock, patch
from src.services.llm import OpenAILLMService
from src.models import Commit
import json
import urllib.error

@pytest.fixture
def llm_service():
    return OpenAILLMService(api_key="test_key")

@pytest.fixture
def sample_commit():
    return Commit(hash_id="abc1234", message="feat: add new feature")

def test_analyze_commit_success(llm_service, sample_commit):
    mock_response_content = {
        "choices": [
            {"message": {"content": "Summary of changes"}}
        ]
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = json.dumps(mock_response_content).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        analysis = llm_service.analyze_commit(sample_commit)

        assert analysis == "Summary of changes"

        # Verify request
        args, _ = mock_urlopen.call_args
        request = args[0]
        assert request.full_url == "https://api.openai.com/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test_key"
        # urllib.request stores headers with title case keys usually,
        # but let's check how we set them. We set "Content-Type".
        # However, checking specific header existence is enough or check exact casing if implementation preserves it.
        # urllib.request.Request headers are stored in .headers or .unredirected_hdrs
        assert request.headers["Authorization"] == "Bearer test_key"
        assert request.headers["Content-type"] == "application/json"

        data = json.loads(request.data)
        assert data["model"] == "gpt-4o-mini"
        assert "messages" in data

def test_analyze_commit_api_error(llm_service, sample_commit):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        analysis = llm_service.analyze_commit(sample_commit)

        assert "Error: OpenAI API returned status code 500" in analysis

def test_analyze_commit_http_error(llm_service, sample_commit):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://example.com",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None
        )

        analysis = llm_service.analyze_commit(sample_commit)

        assert "Error: HTTP 401 - Unauthorized" in analysis

def test_analyze_commit_url_error(llm_service, sample_commit):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError(reason="Connection refused")

        analysis = llm_service.analyze_commit(sample_commit)

        assert "Error: Failed to reach server - Connection refused" in analysis
