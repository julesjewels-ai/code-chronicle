import subprocess
from typing import List, Dict, Any

class CodeChronicleApp:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def _get_git_log(self, limit: int) -> List[str]:
        cmd = ["git", "-C", self.repo_path, "log", f"-n {limit}", "--pretty=format:%h|%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')

    def _mock_llm_insight(self, message: str) -> str:
        # In a real app, this calls OpenAI/Anthropic
        return f"This change evolves the codebase by '{message}'."

    def get_narrative_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        commits = self._get_git_log(limit)
        events = []
        
        for line in commits:
            if not line: continue
            hash_id, msg = line.split('|', 1)
            insight = self._mock_llm_insight(msg)
            events.append({
                "hash": hash_id,
                "message": msg,
                "insight": insight
            })

        return events

    def generate_narrative(self, limit: int = 5) -> str:
        # Kept for backward compatibility, but uses get_narrative_events internally
        events = self.get_narrative_events(limit)
        narrative = []

        for event in events:
            narrative.append(f"Commit {event['hash']}: {event['message']}\n  -> LLM Analysis: {event['insight']}")
            
        return "\n\n".join(narrative)