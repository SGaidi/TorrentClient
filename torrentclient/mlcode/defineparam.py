from typing import List, Tuple
#TODO: add allowed types


class DefineParam:
    """Data class of a parameter attribute"""

    def __init__(self, key: str, name: str, doc: str):
        """
        :param key: parameter key in str
        :param name: attribute name in a class
        :param doc: __doc__ string of a class attribute
        """
        self.key = key
        self.name = name
        self.doc = doc

    def __eq__(self, other) -> bool:
        return isinstance(other, DefineParam) and \
            self.key == other.key and self.name == other.name


DefineParamsArgs = List[Tuple[str, str, str]]


class DefineParams:
    """Mapping class between parameter keys and attribute names"""

    def __init__(self, define_params_args: DefineParamsArgs):
        """
        :param define_params_args: list of 3-item tuples of str
        """
        self.define_params = [DefineParam(*define_param_args) for define_param_args in define_params_args]

    def __doc__(self) -> str:
        return '\n'.join(":param {}: {}".format(define_param.name, define_param.doc)
                         for define_param in self.define_params)

    def match_key(self, key: str) -> DefineParam:
        """
        returns DefineParam if `key` matches any,
        returns None otherwise.
        """
        matches = [defined_param for defined_param in self.define_params if key == defined_param.key]
        if matches:
            return matches[0]
        else:
            return None

    def match_name(self, name: str) -> DefineParam:
        """
        returns DefineParam if `name` matches any,
        returns None otherwise.
        """
        matches = [defined_param for defined_param in self.define_params if name == defined_param.name]
        if matches:
            return matches[0]
        else:
            return None
