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

from typing import List

from ccndedup.core.chunk_writer import ChunkWriter
from ccndedup.core.file_chunk import FileChunk


class MockChunkWriter(ChunkWriter):
    def __init__(self):
        self.chunks: List[FileChunk] = []

    def write(self, file_chunk: FileChunk):
        self.chunks.append(file_chunk)

    def data(self):
        value = b''
        for chunk in self.chunks:
            value += chunk.value
        return value
