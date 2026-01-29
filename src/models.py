class Commit:
    __slots__ = ('hash_id', 'message')
    __match_args__ = ('hash_id', 'message')

    def __init__(self, hash_id: str, message: str):
        self.hash_id = hash_id
        self.message = message

    def __repr__(self):
        return f"Commit(hash_id={self.hash_id!r}, message={self.message!r})"

    def __eq__(self, other):
        if not isinstance(other, Commit):
            return NotImplemented
        return self.hash_id == other.hash_id and self.message == other.message
