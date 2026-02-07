import json
import urllib.request
import urllib.error
from ..interfaces import LLMProvider
from ..models import Commit

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze_commit(self, commit: Commit) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        prompt = (
            f"Analyze the following git commit message and provide a brief summary of the changes "
            f"and their impact on the codebase. Keep it concise.\n\n"
            f"Commit Hash: {commit.hash_id}\n"
            f"Message: {commit.message}"
        )

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful software engineering assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.5,
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req) as response:
                # status is not always available on the response object directly in all versions,
                # but getcode() is standard.
                if response.getcode() == 200:
                    result = json.loads(response.read().decode("utf-8"))
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return f"Error: OpenAI API returned status code {response.getcode()}"

        except urllib.error.HTTPError as e:
            return f"Error: HTTP {e.code} - {e.reason}"
        except urllib.error.URLError as e:
            return f"Error: Failed to reach server - {e.reason}"
        except Exception as e:
            return f"Error: {str(e)}"

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."
