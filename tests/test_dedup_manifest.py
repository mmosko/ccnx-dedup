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

from ccnpy.core.Name import Name
from ccnpy.core.Packet import Packet
from ccnpy.crypto.RsaKey import RsaKey
from ccnpy.crypto.RsaSha256 import RsaSha256Signer
from ccnpy.flic.tree.Traversal import Traversal
from ccnpy.flic.tree.TreeIO import TreeIO
from tests import MockKeys

from ccndedup.dedup_manifest import DedupManifest
from ccndedup.fastcdc.fastcdc import FastCdc
from tests.ccndup_testcase import CcndupTestCase


class TestDedupManifest(CcndupTestCase):

    def _dedup_file(self, dd_manifest, fastcdc, root_name, signer, filename) -> Packet:
        fastcdc.chunk_file(filename)
        return dd_manifest.save(name=root_name, signer=signer)

    def test_chunk_buffer(self):
        output_buffer = TreeIO.PacketMemoryWriter()
        dd_manifest = DedupManifest(output_buffer)
        fastcdc = FastCdc(chunk_writer=dd_manifest)

        filename="../workloads/tar/patch-2.7.tar"
        root_name = Name.from_uri('ccnx:/patch-2.7.tar')
        root_packet = self._dedup_file(dd_manifest, fastcdc, root_name, None, filename)

        with open(filename, "rb") as fh:
            expected = fh.read()

        actual = TreeIO.DataBuffer()
        tr = Traversal(packet_input=output_buffer, data_writer=actual, build_graph=True)
        tr.traverse(root_name=root_name, hash_restriction=root_packet.content_object_hash())
        tr.get_graph().save('ddtree.dot')

        self.assertEqual(expected, actual.buffer.tobytes())

    def test_two_files(self):
        signer = RsaSha256Signer(RsaKey(MockKeys.private_key_pem))
        output_buffer = TreeIO.PacketMemoryWriter()
        dd_manifest = DedupManifest(output_buffer)
        fastcdc = FastCdc(chunk_writer=dd_manifest)

        print("Dedup 2.7")
        root_name_2_7 = Name.from_uri('ccnx:/patch-2.7.tar')
        root_packet_2_7 = self._dedup_file(dd_manifest, fastcdc, root_name_2_7, signer,"../workloads/tar/patch-2.7.tar")

        print(f"Packet count = {len(output_buffer.packets)}, Hash count = {len(output_buffer.by_hash)}")
        print(f"Packet bytes = {output_buffer.total_bytes_by_packet}, Hash bytes = {output_buffer.total_bytes_by_hash}")

        print("Dedup 2.7.4")
        root_name_2_7_4 = Name.from_uri('ccnx:/patch-2.7.4.tar')
        root_packet_2_7_4 = self._dedup_file(dd_manifest, fastcdc, root_name_2_7_4, signer,"../workloads/tar/patch-2.7.4.tar")

        print(f"Packet count = {len(output_buffer.packets)}, Hash count = {len(output_buffer.by_hash)}")
        print(f"Packet bytes = {output_buffer.total_bytes_by_packet}, Hash bytes = {output_buffer.total_bytes_by_hash}")

        # with open(filename, "rb") as fh:
        #     expected = fh.read()
        #
        # actual = TreeIO.DataBuffer()
        # tr = Traversal(packet_input=output_buffer, data_writer=actual, build_graph=True)
        # tr.traverse(root_name=root_name, hash_restriction=root_packet.content_object_hash())
        # tr.get_graph().save('ddtree.dot')
        #
        # self.assertEqual(expected, actual.buffer.tobytes())
