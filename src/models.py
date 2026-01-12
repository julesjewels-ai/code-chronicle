from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class Commit:
    hash_id: str
    message: str
    diff: Optional[str] = None

