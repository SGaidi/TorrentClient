

class ParamClass:
    """Parameterized parent class"""

    @property
    def dp(self):
        raise AttributeError("{} must have dp defined".format(self.__class__.__name__))

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
        return "{}}:\n{}\n".format(self.__class__.__name__,
            '\n'.join("{}:{}".format(key, value) for key, value in self.__dict__.items()),
        )

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__.items() == other.__dict__.items()
