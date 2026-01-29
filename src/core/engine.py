from ..interfaces import GitProvider, LLMProvider
from ..models import Commit


class ChronicleGenerator:
    def __init__(self, git_provider: GitProvider, llm_provider: LLMProvider):
        self.git_provider = git_provider
        self.llm_provider = llm_provider

    def generate(self, limit: int = 5) -> str:
        # Lazy import to optimize startup time
        import concurrent.futures

        commits = self.git_provider.get_commit_history(limit)

        # Optimize: Parallelize LLM analysis calls as they are I/O bound.
        # This significantly reduces total time when using real network-based
        # LLM providers. map() preserves the order of results.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self._process_commit, commits)

        return "\n\n".join(results)

    def _process_commit(self, commit: Commit) -> str:
        analysis = self.llm_provider.analyze_commit(commit)
        return (
            f"Commit {commit.hash_id}: {commit.message}\n"
            f"  -> {analysis}"
        )
