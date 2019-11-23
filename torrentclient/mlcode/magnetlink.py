from torrentclient.mlcode.defineparam import DefineParam as dp


class MagnetLink:
    """Data class of all supported parameters of a magnet-link"""

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
            param = dp.match_name(attr_name)
            if param is None:
                raise TypeError("__init__() got an unexpected keyword argument '{}'.".format(attr_name))
            if not isinstance(attr_value, str) and not self._is_list_of_str(attr_value):
                raise ValueError(
                    "__init__() got invalid type of argument ({}), should be a str or list of str.".format(attr_value))
            setattr(self, attr_name, attr_value)
    __init__.__doc__ = '\n'.join(":param {}: {}".format(ml_param.name, ml_param.doc) for ml_param in dp.DEFINED_PARAMS)

    def __repr__(self):
        return "MagnetLink:\n{}".format('\n'.join("{}:{}".format(key, value) for key, value in self.__dict__.items()))

    def __eq__(self, other) -> bool:
        return isinstance(other, MagnetLink) and self.__dict__.items() == other.__dict__.items()


# Define all of MagnetLink's attributes
# Reference: https://en.wikipedia.org/wiki/Magnet_URI_scheme
dp('dn', 'display_name', "filename to display to the user")
dp('xl', 'exact_length', "file(s) size in bytes")
dp('xt', 'exact_topic', "file(s) hash URN")
dp('as', 'acceptable_source', "direct web link to the file(s) online")
dp('xs', 'exact_source', "direct or backup at P2P source (HTTPS, FTPS, etc) with file hash")
dp('kt', 'keyword_topic', "list of search words used in P2P networks")
dp('mt', 'manifest_topic', "link to a list of links (web, URN)")
dp('tr', 'address_tracker', "list of tracker URLs for BitTorrent downloads")
