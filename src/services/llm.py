from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        import openai  # type: ignore
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        prompt = f"""Analyze the following git commit and explain how it evolves the codebase.
Focus on the "why" and architectural impact.

Message: {commit.message}

Diff:
{commit.diff[:10000]}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect analyzing code evolution."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content or "No analysis generated."
        except Exception as e:
            return f"Error generating analysis: {str(e)}"
