from ..interfaces import LLMProvider
from ..models import Commit

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: Commit {commit.hash_id} by {commit.author} on {commit.date}: '{commit.message}'\nDetails: {commit.body[:50]}..."
