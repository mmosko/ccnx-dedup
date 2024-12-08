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
