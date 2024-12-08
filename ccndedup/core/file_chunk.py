#  Copyright 2024 Marc Mosko
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
