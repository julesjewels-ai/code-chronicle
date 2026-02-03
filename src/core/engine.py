from collections.abc import Iterator
from ..interfaces import GitProvider, LLMProvider
from ..models import Commit, AnalyzedCommit

class ChronicleGenerator:
    def __init__(self, git_provider: GitProvider, llm_provider: LLMProvider):
        self.git_provider = git_provider
        self.llm_provider = llm_provider

    def generate(self, limit: int = 5) -> Iterator[AnalyzedCommit]:
        # Lazy import to optimize startup time
        import concurrent.futures

        # Optimize: Parallelize LLM analysis calls as they are I/O bound.
        # This significantly reduces total time when using real network-based LLM providers.
        # map() preserves the order of results corresponding to the input iterator.
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(limit, 32)) as executor:
            # Optimize: Stream results as they become available using yield from.
            # This improves time-to-first-result significantly compared to buffering in a list.
            # The context manager ensures executor.shutdown(wait=True) is called on exit.
            yield from executor.map(
                self._process_commit,
                self.git_provider.get_commit_history(limit)
            )

    def _process_commit(self, commit: Commit) -> AnalyzedCommit:
        return AnalyzedCommit(
            commit=commit,
            analysis=self.llm_provider.analyze_commit(commit)
        )
