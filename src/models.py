from dataclasses import dataclass

@dataclass(slots=True)
class Commit:
    hash_id: str
    message: str
