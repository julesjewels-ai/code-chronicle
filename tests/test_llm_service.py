from src.services.llm import MockLLMService
from src.models import Commit

def test_mock_llm_analyze():
    service = MockLLMService()
    commit = Commit(hash_id="123", message="test")
    analysis = service.analyze_commit(commit)
    assert analysis == "LLM Analysis: This change evolves the codebase by 'test'."
