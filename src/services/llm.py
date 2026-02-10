from ..interfaces import LLMProvider
from ..models import Commit
import openai

class MockLLMService(LLMProvider):
    def analyze_commit(self, commit: Commit) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{commit.message}'."

class OpenAILLMService(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def analyze_commit(self, commit: Commit) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer analyzing git commits. Summarize the impact of this change concisely."},
                    {"role": "user", "content": f"Commit Message: {commit.message}\n\nAnalyze this commit."}
                ]
            )
            content = response.choices[0].message.content
            return content.strip() if content else "No analysis generated."
        except openai.APIError as e:
            return f"OpenAI API Error: {str(e)}"
        except openai.RateLimitError as e:
            return f"OpenAI Rate Limit Error: {str(e)}"
        except Exception as e:
            return f"Error analyzing commit: {str(e)}"
