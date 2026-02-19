from openai import OpenAI
from ..interfaces import LLMProvider
from ..models import Commit

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o") -> None:
        """
        Initialize the OpenAI LLM service.

        :param api_key: The OpenAI API key. If not provided, it will be read from the environment.
        :param model: The OpenAI model to use. Defaults to "gpt-4o".
        """
        # OpenAI client automatically looks for OPENAI_API_KEY env var if api_key is None
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        """
        Analyze a commit using the OpenAI API.

        :param commit: The commit object to analyze.
        :return: A string containing the analysis of the commit.
        """
        prompt = (
            f"Analyze the following commit message and provide a concise summary of the changes.\n\n"
            f"Commit Hash: {commit.hash_id}\n"
            f"Message: {commit.message}\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer reviewing code changes. Provide a concise, insightful summary of the commit's intent and impact."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            content = response.choices[0].message.content
            return content.strip() if content else "No analysis generated."
        except Exception as e:
            return f"Error analyzing commit: {str(e)}"
