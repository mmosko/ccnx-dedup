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
