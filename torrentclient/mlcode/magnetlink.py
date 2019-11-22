from torrentclient.mlcode.defineparam import DefineParam as dp


class MagnetLink:
    """Data class of all supported parameters of a magnet-link"""

    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            param = dp.match_name(attr_name)
            if param is None:
                raise TypeError("__init__() got an unexpected keyword argument '{}'.".format(attr_name))
            setattr(self, attr_name, attr_value)
    __init__.__doc__ = '\n'.join(":param {}: {}".format(ml_param.name, ml_param.doc) for ml_param in dp.DEFINED_PARAMS)


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
