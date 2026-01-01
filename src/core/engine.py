from typing import List
from ..interfaces import GitProvider, LLMProvider
from ..models import NarrativeChunk

class ChronicleGenerator:
    def __init__(self, git_provider: GitProvider, llm_provider: LLMProvider):
        self.git_provider = git_provider
        self.llm_provider = llm_provider

    def generate(self, limit: int = 5) -> str:
        commits = self.git_provider.get_commit_history(limit)
        narrative_chunks = []

        for commit in commits:
            analysis = self.llm_provider.analyze_commit(commit)
            chunk = NarrativeChunk(commit=commit, analysis=analysis)
            narrative_chunks.append(chunk)

        return self._format_narrative(narrative_chunks)

    def _format_narrative(self, chunks: List[NarrativeChunk]) -> str:
        formatted_parts = []
        for chunk in chunks:
            formatted_parts.append(
                f"Commit {chunk.commit.hash_id}: {chunk.commit.message}\n  -> {chunk.analysis}"
            )
        return "\n\n".join(formatted_parts)
