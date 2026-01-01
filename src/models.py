from dataclasses import dataclass
from typing import Optional

@dataclass
class Commit:
    hash_id: str
    message: str
    diff: Optional[str] = None

@dataclass
class NarrativeChunk:
    commit: Commit
    analysis: str
