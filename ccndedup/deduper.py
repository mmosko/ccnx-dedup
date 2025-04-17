#  Copyright 2025 Marc Mosko
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
import logging
import sys
from typing import Tuple

from ccnpy.core.Name import Name, NameComponent
from ccnpy.core.Packet import Packet
from ccnpy.crypto.RsaKey import RsaKey
from ccnpy.crypto.RsaSha256 import RsaSha256Signer
from ccnpy.flic.name_constructor.SchemaType import SchemaType
from ccnpy.flic.tree.TreeIO import TreeIO

from tests import MockKeys
from ccndedup.dedup_manifest import DedupManifest
from ccndedup.fastcdc.fastcdc import FastCdc


class Deduper:
    @staticmethod
    def _dedup_file(dd_manifest, fastcdc, root_name, signer, filename) -> Tuple[Packet, int]:
        file_size = fastcdc.chunk_file(filename)
        return dd_manifest.save(name=root_name, signer=signer), file_size

    def __init__(self):
        self.signer = RsaSha256Signer(RsaKey(MockKeys.private_key_pem))
#        self.output_buffer = TreeIO.PacketMemoryWriter()
        self.output_buffer = None
        self.dd_manifest = None
        self.fastcdc = None

    def run(self):
        file_groups = [
             [
                 "patch-2.7.tar",
                 "patch-2.7.1.tar",
                 "patch-2.7.2.tar",
                 "patch-2.7.3.tar",
                 "patch-2.7.4.tar",
                 "patch-2.7.5.tar",
                 "patch-2.7.6.tar"
             ],
#             [
#                 "bison-3.7.tar",
#                 "bison-3.7.1.tar",
#                 "bison-3.7.2.tar",
#                 "bison-3.7.3.tar",
#                 "bison-3.7.4.tar",
#                 "bison-3.7.5.tar",
#                 "bison-3.7.6.tar",
#                 "bison-3.8.tar",
#                 "bison-3.8.1.tar",
#                 "bison-3.8.2.tar",
#             ],
#             [
#                 "binutils-2.43.tar",
#                 "binutils-2.43.1.tar",
#                 "binutils-2.44.tar"
#             ],
#             [
#                 "emacs-29.1.tar",
#                 "emacs-29.2.tar",
#                 "emacs-29.3.tar",
#                 "emacs-29.4.tar"
#                 ],
#            [
#                "gcc-12.1.0.tar",
#                "gcc-12.2.0.tar",
#                "gcc-12.3.0.tar",
#                "gcc-12.4.0.tar",
#            ],
        ]

        for g in file_groups:
            print("\n+++ NEW GROUP +++\n")
            self._init_state()
            for f in g:
                self._dedup(f)

    def _init_state(self):
        self.output_buffer = TreeIO.PacketDirectoryWriter(directory="../dedup-experiment/output", link_named_objects=True,
                                                          nested=True)
        self.dd_manifest = None
        self.fastcdc = None

    def _dedup(self, name):
        print(f"Dedup {name}")
        schema_type = SchemaType.SEGMENTED
        data_name = Name.from_uri(f'ccnx:/com/objectstore/gnu/{name}')
        manifest_name = Name.from_uri(f'ccnx:/com/objectstore/gnu/{name}/m')

        self.dd_manifest = DedupManifest(self.output_buffer, schema_type=schema_type,
                                         data_prefix=data_name, manifest_prefix=manifest_name)

        self.fastcdc = FastCdc(chunk_writer=self.dd_manifest)

        root_packet, file_size = self._dedup_file(dd_manifest=self.dd_manifest,
                                                  fastcdc=self.fastcdc,
                                                  root_name=manifest_name,
                                                  signer=self.signer,
                                                  filename=f"../dedup-experiment/workloads/tar/{name}")

        print(f"Root packet = {root_packet.content_object_hash().value().tobytes().hex()}")
        # print(f"Packet count = {len(self.output_buffer.packets)}, Hash count = {len(self.output_buffer.by_hash)}")
        # print(f"Packet bytes = {self.output_buffer.total_bytes_by_packet}, Hash bytes = {self.output_buffer.total_bytes_by_hash}")
        print(f"Manifest Cnt {self.output_buffer.cnt_manifest} Bytes {self.output_buffer.bytes_manifest}, Data Cnt {self.output_buffer.cnt_data} Bytes {self.output_buffer.bytes_data}")
        print(f"CSV  {name}, {file_size}, {len(self.output_buffer.by_hash)}, {self.output_buffer.total_bytes_by_hash}, {self.output_buffer.total_bytes_by_packet}")

        # with open(filename, "rb") as fh:
        #     expected = fh.read()
        #
        # actual = TreeIO.DataBuffer()
        # tr = Traversal(packet_input=output_buffer, data_writer=actual, build_graph=True)
        # tr.traverse(root_name=root_name, hash_restriction=root_packet.content_object_hash())
        # tr.get_graph().save('ddtree.dot')
        #
        # self.assertEqual(expected, actual.buffer.tobytes())


def run():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='/tmp/myapp.log',
                        filemode='w')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)


    root_logger = logging.getLogger()
    root_logger.addHandler(console)
    root_logger.setLevel(logging.INFO)
    logging.getLogger('ccndedup.fastcdc.fastcdc').setLevel(logging.INFO)

    dd = Deduper()
    dd.run()


if __name__ == "__main__":
    run()

