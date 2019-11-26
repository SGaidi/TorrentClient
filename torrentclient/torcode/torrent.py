import bencode

from torrentclient.meta.defineparam import DefineParams


class Torrent:
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
    def _is_list_of_str(cls, obj) -> bool:
        if not isinstance(obj, list):
            return False
        for item in obj:
            if not isinstance(item, str):
                return False
        return True

    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            param = self.dp.match_name(attr_name)
            if param is None:
                raise TypeError("__init__() got an unexpected keyword argument '{}'.".format(attr_name))
            if not isinstance(attr_value, str) and not self._is_list_of_str(attr_value):
                raise ValueError(
                    "__init__() got invalid type of argument ({}), should be a str or list of str.".format(attr_value))
            setattr(self, attr_name, attr_value)
    __init__.__doc__ = dp.__doc__()

    @classmethod
    def from_file(cls, path: str):
        metadata = bencode.bdecode(open(path, 'r').read())
        return cls(**metadata)

    def __repr__(self):
        return "{}}:\n{}\n".format(self.__class__.__name__,
            '\n'.join("{}:{}".format(key, value) for key, value in self.__dict__.items()),
        )

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__.items() == other.__dict__.items()



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
