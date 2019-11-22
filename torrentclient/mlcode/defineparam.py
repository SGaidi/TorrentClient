

class DefineParam:
    """Data class of a parameter attribute of the MagnetLink class"""

    DEFINED_PARAMS = []

    def __init__(self, key: str, name: str, doc: str):
        """
        :param key: parameter key in magnet-link URI
        :param name: attribute name in MagnetLink class
        :param doc: __doc__ string of MagnetLink attribute
        """
        self.key = key
        self.name = name
        self.doc = doc
        self.DEFINED_PARAMS.append(self)

    @classmethod
    def match_key(cls, key: str):
        """
        returns DefineParam if `key` matches any,
        returns None otherwise.
        """
        matches = [defined_param for defined_param in cls.DEFINED_PARAMS if key == defined_param.key]
        if matches:
            return matches[0]
        else:
            return None

    @classmethod
    def match_name(cls, name: str):
        """
        returns DefineParam if `name` matches any,
        returns None otherwise.
        """
        matches = [defined_param for defined_param in cls.DEFINED_PARAMS if name == defined_param.name]
        if matches:
            return matches[0]
        else:
            return None
