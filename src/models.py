from dataclasses import dataclass, field

@dataclass(slots=True)
class Commit:
    hash_id: str
    message: str
    diff: str = field(default="")

@dataclass(slots=True)
class AnalyzedCommit:
    commit: Commit
    analysis: str
