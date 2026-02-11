from openai import OpenAI, OpenAIError
from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        # OpenAI client will automatically look for OPENAI_API_KEY env var if api_key is None
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        prompt = f"Analyze the following commit message and explain how it evolves the codebase:\n\nMessage: {commit.message}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer explaining code changes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            content = response.choices[0].message.content
            return content.strip() if content else "No analysis generated."
        except OpenAIError as e:
            return f"Error generating analysis: {str(e)}"
