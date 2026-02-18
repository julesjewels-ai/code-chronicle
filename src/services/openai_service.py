from ..interfaces import LLMProvider
from ..models import Commit
from openai import OpenAI

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        prompt = (
            f"Analyze this git commit and explain its impact on the codebase in one sentence. "
            f"Commit message: '{commit.message}'."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes git commits."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
            return "Error: No content returned."
        except Exception as e:
            return f"Error analyzing commit: {e}"
