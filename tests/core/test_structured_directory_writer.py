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

import binascii
import tempfile
from pathlib import Path

from ccnpy.core.ContentObject import ContentObject
from ccnpy.core.HashValue import HashValue
from ccnpy.core.Name import Name, NameComponent
from ccnpy.core.Packet import Packet
from ccnpy.core.Payload import Payload

from ccndedup.core.structured_directory_writer import StructuredDirectoryWriter
from tests.ccndup_testcase import CcndupTestCase

class TestStructuredDirectoryWriter(CcndupTestCase):
    def test_name_path(self):
        name_base = Name.from_uri('ccnx:/foo/bar')
        name = name_base.append(NameComponent.create_manifest_id(7))
        with tempfile.TemporaryDirectory() as tempdir:
            sdw = StructuredDirectoryWriter(directory_root=tempdir)
            actual = sdw.to_path(name)
            expected_filename = '0000001300010003666f6f000100036261720010000107'
            expected = Path(tempdir, 'foo', 'bar', expected_filename)
            self.assertEqual(expected, actual)

    def test_hash_value_path(self):
        hv = HashValue(1, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        with tempfile.TemporaryDirectory() as tempdir:
            sdw = StructuredDirectoryWriter(directory_root=tempdir)
            actual = sdw.to_path(hv)
            expected = Path(tempdir, '01', '02', '03', '04', '0102030405060708090a')
            self.assertEqual(expected, actual)

    def test_packet_path(self):
        p = Packet.create_content_object(ContentObject.create_data(payload=Payload([1, 2])))
        h = p.content_object_hash().value().tobytes()

        with tempfile.TemporaryDirectory() as tempdir:
            sdw = StructuredDirectoryWriter(directory_root=tempdir)
            actual = sdw.to_path(p)
            expected = Path(
            tempdir,
                str(binascii.hexlify(h[0].to_bytes()), 'utf-8'),
                str(binascii.hexlify(h[1].to_bytes()), 'utf-8'),
                str(binascii.hexlify(h[2].to_bytes()), 'utf-8'),
                str(binascii.hexlify(h[3].to_bytes()), 'utf-8'),
                str(binascii.hexlify(h), 'utf-8'))
            self.assertEqual(expected, actual)

    def test_put(self):
        p = Packet.create_content_object(
            ContentObject.create_data(
                name=Name.from_uri('ccnx:/foo/bar'),
                payload=Payload([1, 2])))

        with tempfile.TemporaryDirectory() as tempdir:
            sdw = StructuredDirectoryWriter(directory_root=tempdir, link_named_objects=True)
            sdw.put(p)

            p1 = sdw.to_path(p)
            self.assertTrue(p1.exists())

            link_packet = sdw._create_link(p)
            p2 = sdw.to_path(link_packet.body().name())
            self.assertTrue(p2.exists())

