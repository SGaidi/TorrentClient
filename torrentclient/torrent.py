import bencode
import hashlib


class Torrent:
    """Class for extracting meta-info from a torrent file.

    Reference: https://wiki.theory.org/index.php/BitTorrentSpecification#Metainfo_File_Structure
    """

    def __init__(self, path: str):
        self.file = open(path, 'r').read()
        self.metadata = bencode.bdecode(self.file)

    @property
    def info(self) -> dict:
        """a dictionary that describes the file(s) of the torrent
        TODO: has 2 modes (1 or multiple files), use a design pattern / class for it"""
        return self.metadata['info']

    @property
    def announce(self) -> str:
        """announce URL of the tracker"""
        return self.metadata['']

"""
hashcontents = bencode.bencode(metadata['info'])
import hashlib
digest = hashlib.sha1(hashcontents).digest()
import base64
b32hash = base64.b32encode(digest)
b32hash

# should be => magnet:?xt=urn:btih:CT76LXJDDCH5LS2TUHKH6EUJ3NYKX4Y6

# this below can be passed to MagnetLink.encode() / torrent2magnet?
# see: http://dan.folkes.me/2012/04/converting-a-magnet-link-into-a-torrent/
params = {'xt': 'urn:btih:%s' % b32hash,
    'dn': metadata['info']['name'],
    'tr': metadata['announce'],
    'xl': metadata['info']['length']}
"""