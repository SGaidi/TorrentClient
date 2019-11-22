

class DefineParam:
    """Data class of attributes in magnet-link encoder and decoder

    Reference:
        https://en.wikipedia.org/wiki/Magnet_URI_scheme
        https://libtorrent.org/manual.html#magnet-links - BitTorrent minimal parameters used in libtorrent.
    """

    DEFINED_PARAMS = []

    def __init__(self, key: str, name: str, doc: str):
        """
        :param key: actual parameter in magnet-link URI
        :param name: full name to be converted to attribute name
        :param doc: to be set as attribute's __doc__
        """
        self.key = key
        self.name = name
        self.doc = doc
        self.DEFINED_PARAMS.append(self)

    @classmethod
    def match_name(cls, attribute_name: str):
        """
        returns DefineParam if `attribute_name` matches any,
        returns None otherwise.
        """
        matches = [defined_param for defined_param in cls.DEFINED_PARAMS if attribute_name == defined_param.name]
        if matches:
            return matches[0]
        else:
            return None

    @classmethod
    def match_param(cls, param: str):
        """
        returns DefineParam if `attribute_name` matches any,
        returns None otherwise.
        """
        matches = [defined_param for defined_param in cls.DEFINED_PARAMS if param == defined_param.key]
        if matches:
            return matches[0]
        else:
            return None


DefineParam('dn', 'display_name', "filename to display to the user")
DefineParam('xl', 'exact_length', "file(s) size in bytes")
DefineParam('xt', 'exact_topic', "file(s) hash URN")
DefineParam('as', 'acceptable_source', "direct web link to the file(s) online")
DefineParam('xs', 'exact_source', "direct or backup at P2P source (HTTPS, FTPS, etc) with file hash")
DefineParam('kt', 'keyword_topic', "list of search words used in P2P networks")
DefineParam('mt', 'manifest_topic', "link to a list of links (web, URN)")
DefineParam('tr', 'address_tracker', "list of tracker URLs for BitTorrent downloads")
