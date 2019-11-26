from torrentclient.mlcode.defineparam import DefineParams


class MagnetLink:
    """Data class of all supported parameters of a magnet-link"""

    dp = DefineParams([
        ('dn', 'display_name', "filename to display to the user"),
        ('xl', 'exact_length', "file(s) size in bytes"),
        ('xt', 'exact_topic', "file(s) hash URN"),
        ('as', 'acceptable_source', "direct web link to the file(s) online"),
        ('xs', 'exact_source', "direct or backup at P2P source (HTTPS, FTPS, etc) with file hash"),
        ('kt', 'keyword_topic', "list of search words used in P2P networks"),
        ('mt', 'manifest_topic', "link to a list of links (web, URN)"),
        ('tr', 'address_tracker', "list of tracker URLs for BitTorrent downloads"),
    ])
    """
    Definitions of all of MagnetLink's attributes
    Reference: https://en.wikipedia.org/wiki/Magnet_URI_scheme
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
    __init__.__doc__ = dp.__doc__

    def __repr__(self):
        return "MagnetLink:\n{}".format('\n'.join("{}:{}".format(key, value) for key, value in self.__dict__.items()))

    def __eq__(self, other) -> bool:
        return isinstance(other, MagnetLink) and self.__dict__.items() == other.__dict__.items()
