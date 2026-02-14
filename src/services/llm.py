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
        prompt = (
            f"Analyze the following commit message and describe its impact on the codebase.\n\n"
            f"Commit Hash: {commit.hash_id}\n"
            f"Message: {commit.message}\n\n"
            f"Provide a concise summary suitable for a release note or changelog."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a skilled software engineer and technical writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            if not response.choices:
                return "Error: No analysis returned."
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except OpenAIError as e:
            return f"Error analyzing commit: {e}"
