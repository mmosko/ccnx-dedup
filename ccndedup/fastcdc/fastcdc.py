import logging
from typing import Dict

import numpy as np

from .gear import gears
from ..core.chunk_writer import ChunkWriter
from ..core.chunker import Chunker
from ..core.file_chunk import FileChunk


class FastCdc(Chunker):
    """
    FastCDC8KB with NC

    """
    logger = logging.getLogger(__name__)

    __MASK_S = np.uint64(0x0000d9f003530000)
    __MASK_A = np.uint64(0x0000d93003530000)
    __MASK_L = np.uint64(0x0000d90003530000)

    __MIN_SIZE = 2048
    __MAX_SIZE = 65536
    __AVG_SIZE = 8192

    def __init__(self, chunk_writer: ChunkWriter):
        self._writer = chunk_writer
        self._counts: Dict[bytes, int] = {}

    def chunk_file(self, filename):
        self.logger.info("Chunking filename %s", filename)
        with open(filename, "rb") as fh:
            buffer = fh.read()
            self.chunk_buffer(buffer)

    def chunk_buffer(self, buffer: bytes):
        self.logger.info("Chunking buffer len %d", len(buffer))
        self._extract_substrings(buffer)
        self._histogram()

    def _histogram(self):
        h = {}
        for x in self._counts.values():
            if x not in h:
                h[x] = 1
            else:
                h[x] += 1
        self.logger.info("histogram of substring occurances: %s", h)

    def _save_substring(self, substring: FileChunk):
        self._writer.write(substring)
    # def _save_substring(self, substring: FileChunk):
    #     filename = "chunk_" + DisplayFormatter.hexlify(substring.slow_hash)
    #     path = Path(self._output_dir, filename)
    #
    #     # open for exclusive "x".  If already exists, do not write.
    #     try:
    #         with open(path, "xb") as fh:
    #             fh.write(substring.value)
    #     except FileExistsError:
    #         pass

    def _increment_counts(self, substring: FileChunk):
        if substring.slow_hash not in self._counts:
            self._counts[substring.slow_hash] = 1
            return
        self._counts[substring.slow_hash] += 1

    def _extract_substrings(self, buffer):
        start_pos = 0
        file_size = len(buffer)
        percent_increment = int(file_size * 0.10)
        next_percent = percent_increment
        while start_pos < file_size:
            end_offset = self._chunk(buffer[start_pos:])
            self.logger.debug("end_offset: %d", end_offset)
            end_pos = start_pos + end_offset
            substring = FileChunk(starting_position=start_pos, value=buffer[start_pos: end_pos])
            self._increment_counts(substring)
            self._save_substring(substring)
            self.logger.debug("substring: %s", substring)
            start_pos = end_pos
            if start_pos > next_percent:
                self.logger.info("percent done: %d", int(start_pos / file_size * 100))
                next_percent += percent_increment
        self.logger.info("percent done: %d", int(start_pos / file_size * 100))

    def _chunk(self, buffer):
        normal_size = self.__AVG_SIZE
        n = len(buffer)
        if n <= self.__MIN_SIZE:
            return n
        if n >= self.__MAX_SIZE:
            n = self.__MAX_SIZE
        elif n <= normal_size:
            normal_size = n

        fp = np.uint64()
        i = self.__MIN_SIZE

        while i < normal_size:
            fp = (fp << 1) + gears[buffer[i]]
            if (fp & self.__MASK_S) == 0:
                return i
            i += 1

        while i < n:
            fp = (fp << 1) + gears[buffer[i]]
            if (fp & self.__MASK_L) == 0:
                return i
            i += 1
        return n


