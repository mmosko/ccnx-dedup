import binascii
from pathlib import Path
from typing import Optional, Tuple

from ccnpy.core.HashValue import HashValue
from ccnpy.core.Name import Name
from ccnpy.core.Packet import PacketReader, Packet
from ccnpy.crypto.Signer import Signer
from ccnpy.flic.tlvs.Locators import Locators
from ccnpy.flic.tree.TreeIO import TreeIO


class StructuredDirectoryWriter(TreeIO.PacketDirectoryWriter, PacketReader):
    """
    A structured directory writer puts objects in subdirectories based on a prefix of the name.
    """

    def __init__(self, directory_root: str, link_named_objects: bool = False, signer: Optional[Signer]=None,
                 bytes_per_level: int = 1, levels: int = 4):
        """
        Use 1 bytes per level (i.e. subdirectory names are '00' ... 'FF') and structure the
        layout to 4 levels.

        :param directory_root:
        :param bytes_per_level:
        :param levels:
        """
        self._root_path = Path(directory_root)
        self._root_path.mkdir(parents=True, exist_ok=True)

        TreeIO.PacketDirectoryWriter.__init__(self, directory=directory_root, link_named_objects=link_named_objects, signer=signer)

        # create directory if it does not exist, and ensures existing path is a directory
        self._bytes_per_level = bytes_per_level
        self._levels = levels

    def _bytes_to_str(self, b) -> str:
        return str(binascii.hexlify(b), 'utf-8')

    def _path_from_hash(self, input: HashValue) -> Tuple[Path, str]:
        h = input.value()
        prefixes = [self._directory]
        for i in range(0, self._levels):
            start = i * self._bytes_per_level
            end = start + self._bytes_per_level
            p = h[start:end]
            prefixes.append(self._bytes_to_str(p.tobytes()))
        filename = self._bytes_to_str(h)
        path = Path(*prefixes)
        return path, filename

    def _path_from_name(self, name: Name) -> Tuple[Path, str]:
        # All name components are made directory names, then filename is serialization of whole name
        prefixes = [self._directory]
        for i in range(0, name.count()):
            c = name.component(i)
            if c.is_name_segment():
                prefixes.append(c.value().decode('utf-8'))
            else:
                break
        filename = self._bytes_to_str(name.serialize().tobytes())
        path = Path(*prefixes)
        return path, filename

    def to_path(self, input: Packet | Name | HashValue):
        if isinstance(input, Packet):
            prefix, filename = self._path_from_hash(input.content_object_hash())
        elif isinstance(input, HashValue):
            prefix, filename = self._path_from_hash(input)
        elif isinstance(input, Name):
            prefix, filename = self._path_from_name(input)
        else:
            raise TypeError(f"input must be a Packet or a Name, got: {type(input)}: {input}")

        prefix.mkdir(parents=True, exist_ok=True)
        return Path(prefix, filename)

    def get(self, name: Name, hash_restriction: HashValue, locators: Optional[Locators] = None) -> Packet:
        pass

