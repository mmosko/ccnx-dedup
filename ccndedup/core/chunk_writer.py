from abc import ABC, abstractmethod

from .file_chunk import FileChunk


class ChunkWriter(ABC):
    @abstractmethod
    def write(self, file_chunk: FileChunk):
        pass
