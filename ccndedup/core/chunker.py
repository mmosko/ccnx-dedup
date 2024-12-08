from abc import ABC, abstractmethod


class Chunker(ABC):
    def chunk_file(self, filename):
        with open(filename, "rb") as fh:
            buffer = fh.read()
            self.chunk_buffer(buffer)

    @abstractmethod
    def chunk_buffer(self, buffer: bytes):
        pass

