from dataclasses import dataclass

@dataclass(slots=True)
class Commit:
    hash_id: str
    author: str
    date: str
    message: str
    body: str
