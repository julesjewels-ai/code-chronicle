import openai
from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer analyzing git commits. Summarize the impact of this commit in one sentence."},
                    {"role": "user", "content": f"Commit Message: {commit.message}\nCommit Hash: {commit.hash_id}"}
                ]
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
            return "No analysis returned."
        except Exception as e:
            return f"Error analyzing commit: {e}"
