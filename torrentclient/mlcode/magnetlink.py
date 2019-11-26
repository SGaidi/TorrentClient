from torrentclient.meta.paramclass import ParamClass
from torrentclient.meta.defineparam import DefineParams


class MagnetLink(ParamClass):
    """Data class of all supported parameters of a magnet-link"""

    dp = DefineParams([
        ('dn', 'display_name',      "filename to display to the user"),
        ('xl', 'exact_length',      "file(s) size in bytes"),
        ('xt', 'exact_topic',       "file(s) hash URN"),
        ('as', 'acceptable_source', "direct web link to the file(s) online"),
        ('xs', 'exact_source',      "direct or backup at P2P source (HTTPS, FTPS, etc) with file hash"),
        ('kt', 'keyword_topic',     "list of search words used in P2P networks"),
        ('mt', 'manifest_topic',    "link to a list of links (web, URN)"),
        ('tr', 'address_tracker',   "list of tracker URLs for BitTorrent downloads"),
    ])
    """
    Definitions of all of MagnetLink's attributes
    Reference: https://en.wikipedia.org/wiki/Magnet_URI_scheme
    """

    def __init__(self, **kwargs):
        super(MagnetLink, self).__init__(**kwargs)
    __init__.__doc__ = dp.__doc__()
