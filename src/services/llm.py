import json
import urllib.request
import urllib.error
from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze_commit(self, commit: Commit) -> str:
        prompt = f"Analyze this git commit message: '{commit.message}'. Explain the architectural impact and reasoning in 2 sentences."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert software architect."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            return f"Error calling OpenAI API: HTTP {e.code} - {e.reason}"
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
