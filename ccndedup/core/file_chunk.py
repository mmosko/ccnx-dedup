from dataclasses import dataclass, field
from typing import Optional

from .hash_wrapper import fash_hash, slow_hash


@dataclass
class FileChunk:
    starting_position: int
    value: bytes = field(repr=False)
    value_len: int = field(default=0, init=False)
    fast_hash: int = field(default=None, init=False)
    slow_hash: Optional[bytes] = field(default=None, init=False)

    def __post_init__(self):
        self.fast_hash = fash_hash(self.value)
        self.slow_hash = slow_hash(self.value)
        self.value_len = len(self.value)

    def __eq__(self, other):
        if not isinstance(other, FileChunk):
            return False
        return self.fast_hash == other.fast_hash and self.value == other.value

    def __hash__(self):
        return self.fast_hash
