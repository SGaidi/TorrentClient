from typing import List, Tuple, Union
#TODO: add mandatory/optional field
#TODO: add allowed types


class DefineParam:
    """Meta class of a parameter attribute"""

    def __init__(self, key: str, name: str = None, doc: str = None):
        """
        :param key: parameter key in str
        :param name: attribute name in a class, by default it is the same as the key
        :param doc: __doc__ string of a class attribute
        """
        self.key = key
        self.doc = doc
        if name is None:
            self.name = key
        else:
            self.name = name

    def __repr__(self):
        return "key=`{}`, name=`{}`, doc=`{}`".format(self.key, self.name, self.doc)

    def __eq__(self, other) -> bool:
        return isinstance(other, DefineParam) and \
            self.key == other.key and self.name == other.name


DefineParamsArgs = List[Union[Tuple[str, str, str], Tuple[str, str]]]


class DefineParams:
    """Meta class for mapping between parameter keys and attribute names"""

    def __init__(self, define_params_args: DefineParamsArgs):
        """
        :param define_params_args: list of 3-item or 2-item tuples of str
        """
        self.define_params = []
        for define_param_args in define_params_args:
            if len(define_param_args) == 3:
                self.define_params.append(DefineParam(*define_param_args))
            elif len(define_param_args) == 2:
                self.define_params.append(DefineParam(key=define_param_args[0], doc=define_param_args[1]))
            else:
                raise TypeError(
                    "__init__() got invalid type of argument ({}), should be a list of 2-item or 3-item tuples.".format(
                        define_params_args
                    ))

    def __doc__(self) -> str:
        return '\n'.join(":param {}: {}".format(define_param.name, define_param.doc)
                         for define_param in self.define_params if define_param.doc is not None)

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
