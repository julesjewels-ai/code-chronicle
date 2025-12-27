import re
from src.core.git_manager import GitManager

class CodeChronicleApp:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.git_manager = GitManager(repo_path)

    def _mock_llm_insight(self, message: str, diff: str) -> str:
        # In a real app, this calls OpenAI/Anthropic
        # This is a placeholder for more sophisticated analysis

        files_changed = re.findall(r'diff --git a/(.+) b/', diff)
        added_lines = len(re.findall(r'^\+', diff, re.MULTILINE))
        removed_lines = len(re.findall(r'^-', diff, re.MULTILINE))

        summary = (
            f"LLM Analysis: The commit '{message}' modified {len(files_changed)} file(s). "
            f"It added {added_lines} lines and removed {removed_lines} lines."
        )
        if files_changed:
            summary += f"\n    Files changed: {', '.join(files_changed)}."

        return summary

    def generate_narrative(self, limit: int = 5) -> str:
        commits = self.git_manager.get_commits(limit)
        narrative = []
        
        for commit in commits:
            diff = self.git_manager.get_diff(commit['hash'])
            insight = self._mock_llm_insight(commit['message'], diff)
            narrative.append(f"Commit {commit['hash']}: {commit['message']}\n  -> {insight}")
            
        return "\n\n".join(narrative)
