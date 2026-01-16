from typing import List
from ..interfaces import GitProvider, LLMProvider

class ChronicleGenerator:
    def __init__(self, git_provider: GitProvider, llm_provider: LLMProvider):
        self.git_provider = git_provider
        self.llm_provider = llm_provider

    def generate(self, limit: int = 5) -> str:
        commits = self.git_provider.get_commit_history(limit)

        # Optimize: Use generator expression to avoid intermediate list allocation.
        # Performance Impact: Reduced memory usage by eliminating the list of formatted strings.
        return "\n\n".join(
            f"Commit {commit.hash_id}: {commit.message}\n  -> {self.llm_provider.analyze_commit(commit)}"
            for commit in commits
        )
