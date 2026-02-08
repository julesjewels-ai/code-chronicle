from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        # Lazy import to optimize startup time
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        prompt = f"""
Analyze the following git commit and explain its impact on the codebase.
Focus on the "why" and "how".

Commit Message: {commit.message}

Diff:
{commit.diff}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert software engineer performing a code review."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content or ""
