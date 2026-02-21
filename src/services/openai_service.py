from openai import OpenAI
from ..interfaces import LLMProvider
from ..models import Commit

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        prompt = f"Analyze this commit message: '{commit.message}'"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer. Analyze the following commit message and describe its impact on the codebase."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content or ""
