from torrentclient.mlcode.defineparam import DefineParam as df


class MagnetLink:

    def __init__(self, **kwargs):
        for attr_name, attr_value in kwargs.items():
            param = df.match_name(attr_name)
            if param is None:
                raise TypeError("__init__() got an unexpected keyword argument '{}'.".format(attr_name))
            setattr(self, attr_name, attr_value)
    __init__.__doc__ = '\n'.join(":param {}: {}".format(ml_param.name, ml_param.doc) for ml_param in df.DEFINED_PARAMS)
