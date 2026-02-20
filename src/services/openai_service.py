import os
from openai import OpenAI
from ..interfaces import LLMProvider
from ..models import Commit

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"

    def analyze_commit(self, commit: Commit) -> str:
        prompt = (
            "You are a senior software engineer. Analyze the following commit message "
            "and provide a concise summary of the changes and their impact.\n\n"
            f"Commit Hash: {commit.hash_id}\n"
            f"Message: {commit.message}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            return content if content else "No analysis returned."
        except Exception as e:
            # We catch generic exception to avoid crashing the whole generation process
            # for a single commit failure.
            return f"Analysis failed: {str(e)}"
