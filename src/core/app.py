import subprocess
import os
from typing import List

class CodeChronicleApp:
    def __init__(self, repo_path: str):
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        if not os.path.isdir(repo_path):
            raise ValueError(f"Repository path is not a directory: {repo_path}")
        self.repo_path = repo_path

    def _get_git_log(self, limit: int) -> List[str]:
        # Security: Split arguments to prevent argument injection and ensure proper parsing
        cmd = ["git", "-C", self.repo_path, "log", "-n", str(limit), "--pretty=format:%h|%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')

    def _mock_llm_insight(self, message: str) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"LLM Analysis: This change evolves the codebase by '{message}'."

    def generate_narrative(self, limit: int = 5) -> str:
        # Security: Validate input to prevent unexpected behavior or DoS
        if not isinstance(limit, int) or limit <= 0:
            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError("Limit must be a positive integer")

        commits = self._get_git_log(limit)
        narrative = []
        
        for line in commits:
            if not line: continue
            hash_id, msg = line.split('|', 1)
            insight = self._mock_llm_insight(msg)
            narrative.append(f"Commit {hash_id}: {msg}\n  -> {insight}")
            
        return "\n\n".join(narrative)
