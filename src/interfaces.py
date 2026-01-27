from abc import ABC, abstractmethod
from collections.abc import Iterator
from .models import Commit

class GitProvider(ABC):
    @abstractmethod
    def get_commit_history(self, limit: int) -> Iterator[Commit]:
        pass

class LLMProvider(ABC):
    @abstractmethod
    def analyze_commit(self, commit: Commit) -> str:
        pass
