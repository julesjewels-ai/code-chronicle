from ..interfaces import GitProvider, LLMProvider
from ..models import Commit

class ChronicleGenerator:
    def __init__(self, git_provider: GitProvider, llm_provider: LLMProvider):
        self.git_provider = git_provider
        self.llm_provider = llm_provider

    def generate(self, limit: int = 5) -> str:
        # Lazy import threading/queue (lighter than concurrent.futures)
        import threading
        import queue

        commits = list(self.git_provider.get_commit_history(limit))
        if not commits:
            return ""

        results = [None] * len(commits)
        # Use queue for thread-safe task distribution
        task_queue: queue.Queue = queue.Queue()
        for i, commit in enumerate(commits):
            task_queue.put((i, commit))

        def worker():
            while True:
                try:
                    i, commit = task_queue.get_nowait()
                except queue.Empty:
                    break

                try:
                    results[i] = self._process_commit(commit)
                except Exception as e:
                    # In case of error, store the error message to avoid NoneType
                    results[i] = f"Error processing commit {commit.hash_id}: {e}"
                finally:
                    task_queue.task_done()

        # Optimize: Parallelize LLM analysis calls as they are I/O bound.
        # Cap max threads to avoid resource exhaustion on large limits
        num_threads = min(len(commits), 20)
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return "\n\n".join(results)  # type: ignore

    def _process_commit(self, commit: Commit) -> str:
        return f"Commit {commit.hash_id}: {commit.message}\n  -> {self.llm_provider.analyze_commit(commit)}"
