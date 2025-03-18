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

from cryptography.hazmat.primitives import hashes
from spookyhash import hash128


def fash_hash(s: bytes):
    return hash128(s)


def slow_hash(s: bytes):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(s)
    return digest.finalize()
