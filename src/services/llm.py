from openai import OpenAI, OpenAIError
from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer. Analyze the following git commit message and explain its impact on the codebase in one concise sentence."},
                    {"role": "user", "content": commit.message}
                ]
            )
            return response.choices[0].message.content or "No analysis generated."
        except OpenAIError as e:
            return f"Error analyzing commit: {str(e)}"
