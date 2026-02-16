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
            f"Analyze the following commit message and generate a concise summary "
            f"explaining the change and its impact. Focus on the 'why' and 'what'.\n\n"
            f"Commit Hash: {commit.hash_id}\n"
            f"Message: {commit.message}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful software engineering assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            content = response.choices[0].message.content
            return content.strip() if content else "No analysis generated."
        except OpenAIError as e:
            return f"Error analyzing commit: {str(e)}"
