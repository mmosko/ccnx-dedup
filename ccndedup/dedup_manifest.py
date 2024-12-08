import logging
from typing import List, Optional

from ccnpy.core.Name import Name
from ccnpy.core.Packet import Packet, PacketWriter
from ccnpy.crypto.Signer import Signer
from ccnpy.flic.ManifestTree import ManifestTree
from ccnpy.flic.ManifestTreeOptions import ManifestTreeOptions
from ccnpy.flic.name_constructor.FileMetadata import FileMetadata, ChunkMetadata
from ccnpy.flic.name_constructor.NameConstructorContext import NameConstructorContext
from ccnpy.flic.name_constructor.SchemaType import SchemaType
from ccnpy.flic.tree.Traversal import Traversal
from ccnpy.flic.tree.TreeIO import TreeIO

from .core.chunk_writer import ChunkWriter
from .core.file_chunk import FileChunk
from .core.memory_reader import MemoryReader


class DedupManifest(ChunkWriter):
    logger = logging.getLogger(__name__)

    def __init__(self, output: PacketWriter):
        # self._packets: List[Packet] = []
        self._chunks: List[ChunkMetadata] = []
        self._total_bytes = 0

        self._tree_options = ManifestTreeOptions(
            name=Name(),
            data_expiry_time=None,
            schema_type=SchemaType.HASHED,
            signer=None,
            add_node_subtree_size=True,
            max_packet_size=1500)

        self._name_ctx = NameConstructorContext.create(self._tree_options)
        self._nc_cache = Traversal.NameConstructorCache()
        self._nc_cache.update(self._name_ctx.nc_def())
        self._writer = output

    def write(self, substring: FileChunk):
        self.logger.debug("Write %s", substring)
        mt = ManifestTree(
            data_input=MemoryReader(substring.value),
            packet_output=self._writer,
            tree_options=self._tree_options,
            name_context=self._name_ctx
        )
        top_packet = mt.build_top()
        self.logger.debug("Top Manifest: %s", top_packet)
        self._validate(substring, top_packet)
        chunk_bytes = len(substring.value)
        cm = ChunkMetadata(
            chunk_number=len(self._chunks),
            payload_bytes = chunk_bytes,
            content_object_hash = top_packet.content_object_hash()
        )
        self._chunks.append(cm)
        self._total_bytes += chunk_bytes
        self.logger.debug("Chunk meta  : %s", cm)
        self.logger.debug("Total bytes : %d", self._total_bytes)

    def save(self, name: Name, signer: Optional[Signer]) -> Packet:
        options = ManifestTreeOptions(
            name=name,
            data_expiry_time=None,
            schema_type=SchemaType.HASHED,
            signer=signer,
            add_node_subtree_size=True,
            max_packet_size=1500)

        file_metadata = FileMetadata(chunk_metadata=self._chunks, total_bytes=self._total_bytes)
        mt = ManifestTree(
            data_input=file_metadata,
            packet_output=self._writer,
            tree_options=options,
            name_context=self._name_ctx
        )
        root_packet = mt.build()
        return root_packet

    def _validate(self, substring: FileChunk, top_packet: Packet):
        # If debug logging for this module is enabled, then validate that that
        # top_packet really represents the underlying data.
        if not self.logger.isEnabledFor(logging.DEBUG):
            return

        actual = TreeIO.DataBuffer()
        tr = Traversal(packet_input=self._writer, data_writer=actual)
        tr.preorder(top_packet, nc_cache=self._nc_cache)

        if actual.buffer.tobytes() != substring.value:
            raise ValueError(f"Top packet {top_packet.content_object_hash()} does not match substring value {substring}")
