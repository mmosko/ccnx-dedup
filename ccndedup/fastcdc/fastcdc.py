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
import datetime
import logging
from pprint import pprint
from typing import Dict

import numpy as np

from .gear import gears
from ..core.chunk_writer import ChunkWriter
from ..core.chunker import Chunker
from ..core.file_chunk import FileChunk


class FastCdc(Chunker):
    """
    FastCDC8KB with NC

    Based on:
        Xia, Wen, Xiangyu Zou, Hong Jiang, Yukun Zhou, Chuanyi Liu, Dan Feng, Yu Hua, Yuchong Hu, and Yucheng Zhang.
        "The design of fast content-defined chunking for data deduplication based storage systems."
        IEEE Transactions on Parallel and Distributed Systems 31, no. 9 (2020): 2017-2031.
        https://ranger.uta.edu/~jiang/publication/Journals/2020/2020-IEEE-TPDS(Wen%20Xia).pdf
    """

    logger = logging.getLogger(__name__)

    __MASK_S = np.uint64(0x0000d9f003530000)
    __MASK_A = np.uint64(0x0000d93003530000)
    __MASK_L = np.uint64(0x0000d90003530000)

    # __MIN_SIZE = 2800
    # __MAX_SIZE = 65536
    # __AVG_SIZE = 8192

    __MIN_SIZE = 4096
    __MAX_SIZE = 65536
    __AVG_SIZE = 8192

    __MIN_PROGRESS_DELTA = datetime.timedelta(seconds=10)

    def __init__(self, chunk_writer: ChunkWriter):
        self._writer = chunk_writer
        self._counts: Dict[bytes, int] = {}

    def chunk_file(self, filename):
        """Returns the file size"""
        self.logger.info("Chunking filename %s", filename)
        with open(filename, "rb") as fh:
            buffer = fh.read()
            self.chunk_buffer(buffer)
            return len(buffer)

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
        # use pprint to get sorted keys
        print(f"histogram of substring occurrences: {pprint(h)}")

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

    def _log_progress(self, start_time, start_pos, last_time, file_size):
        # Only log progress if it has been at least 10 seconds since the last progress.
        finish_time = datetime.datetime.now()
        if finish_time - last_time < self.__MIN_PROGRESS_DELTA:
            return last_time

        delta = finish_time - start_time
        seconds = delta.microseconds * 1E-6
        mbps = file_size / seconds / 1000000.0

        self.logger.info("percent done: %d, MB/sec: %s",
                         int(start_pos / file_size * 100),
                         "{:,.2f}".format(mbps))
        return finish_time

    def _extract_substrings(self, buffer):
        start_time = datetime.datetime.now()
        last_time = start_time
        start_pos = 0
        file_size = len(buffer)
        total_substring_size = 0
        percent_increment = int(file_size * 0.10)
        next_percent = percent_increment
        while start_pos < file_size:
            end_offset = self._chunk(buffer, start_pos)
            # self.logger.debug("end_offset: %d", end_offset)
            end_pos = start_pos + end_offset
            substring = FileChunk(starting_position=start_pos, value=buffer[start_pos: end_pos])
            total_substring_size += substring.value_len
            self._increment_counts(substring)
            self._save_substring(substring)
            self.logger.debug("substring: %s", substring)
            start_pos = end_pos
            if start_pos > next_percent:
                last_time = self._log_progress(start_time, start_pos, last_time, file_size)
                next_percent += percent_increment
        # passing min for last_time forces it to log regardless of the timedelta.
        self._log_progress(start_time, start_pos, datetime.datetime.min, file_size)

        # print(f"Chunked buffer size {len(buffer)} total substring size {total_substring_size}")
        assert file_size == total_substring_size

    def _chunk(self, buffer, start_pos):
        normal_size = self.__AVG_SIZE
        n = len(buffer) - start_pos
        assert n > 0
        if n <= self.__MIN_SIZE:
            return n
        if n >= self.__MAX_SIZE:
            n = self.__MAX_SIZE
        elif n <= normal_size:
            normal_size = n

        fp = np.uint64()
        i = self.__MIN_SIZE

        while i < normal_size:
            fp = (fp << 1) + gears[buffer[start_pos + i]]
            if (fp & self.__MASK_S) == 0:
                return i
            i += 1

        while i < n:
            fp = (fp << 1) + gears[buffer[start_pos + i]]
            if (fp & self.__MASK_L) == 0:
                return i
            i += 1
        return n
