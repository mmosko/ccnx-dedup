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

import tempfile

from ccndedup.fastcdc.fastcdc import FastCdc
from tests.ccndup_testcase import CcndupTestCase
from tests.mock_chunk_writer import MockChunkWriter


class TestFastCdc(CcndupTestCase):
    def test_chunk_buffer(self):
        output_buffer = MockChunkWriter()
        with tempfile.TemporaryDirectory() as tempdir:
            fastcdc = FastCdc(chunk_writer=output_buffer)
            filename="../workloads/tar/patch-2.7.tar"
            fastcdc.chunk_file(filename)
            actual = output_buffer.data()
            with open(filename, "rb") as fh:
                expected = fh.read()
                self.assertEqual(expected, actual)
