import bencode

from torrentclient.meta.paramclass import ParamClass
from torrentclient.meta.defineparam import DefineParams


class Torrent(ParamClass):
    """Data class of all supported parameters of a torrent file"""

    dp = DefineParams([
        ('info',            "a dictionary that describes the file(s) of the torrent"),
        ('announce',        "announce URL of the tracker"),
        ('announce_list',   "extension to the official specification, offering backwards-compatibility"),
        ('creation_date',   "creation time of the torrent, in standard UNIX epoch format"),
        ('comment',         "free-form textual comments of the author"),
        ('created_by',      "name and version of the program used to create the file"),
        ('encoding',        "str encoding format used to generate the pieces part of the info dictionary in the file"),
    ])
    """
    Definitions of all of Torrent's attributes
    Reference: https://wiki.theory.org/index.php/BitTorrentSpecification#Metainfo_File_Structure
    """

    @classmethod
    def from_file(cls, path: str):
        metadata = bencode.bdecode(open(path, 'r').read())
        return cls(**metadata)

"""
hashcontents = bencode.bencode(metadata['info'])
import hashlib
digest = hashlib.sha1(hashcontents).digest()
import base64
b32hash = base64.b32encode(digest)
b32hash

# should be => magnet:?xt=urn:btih:CT76LXJDDCH5LS2TUHKH6EUJ3NYKX4Y6

params = {'xt': 'urn:btih:%s' % b32hash,
    'dn': metadata['info']['name'],
    'tr': metadata['announce'],
    'xl': metadata['info']['length']}
"""

print(Torrent.__init__.__doc__)