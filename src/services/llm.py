import openai
from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        try:
            prompt = f"Analyze this git commit and explain its architectural impact in one sentence:\n\nMessage: {commit.message}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software architect analyzing code changes."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            return content if content else "Analysis empty."
        except Exception as e:
            return f"Analysis unavailable: {str(e)}"
