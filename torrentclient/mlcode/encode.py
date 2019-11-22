import urllib.parse

from torrentclient.mlcode.magnetlink import MagnetLink
from torrentclient.mlcode.defineparam import DefineParam as dp


def encode(obj: object) -> str:
    """
    :param obj: holds attributes with names of URI parameters
    :return: string of encoded magnet-link
    """
    ml_pairs = []
    for obj_attr_name, obj_attr_value in obj.__dict__.items():
        defined_param = dp.match_name(obj_attr_name)
        if defined_param is None:
            raise ValueError("encode() cannot classify '{}' attribute name.".format(obj_attr_name))
        if not isinstance(obj_attr_value, list):
            ml_pairs.append((defined_param.key, obj_attr_value))
        else:
            for obj_attr_item in obj_attr_value:
                ml_pairs.append((defined_param.key, obj_attr_item))
    return "magnet:?{}".format(urllib.parse.urlencode(ml_pairs))


encode(MagnetLink(display_name="Sarah Gaidi", address_tracker="1.2.3.4"))
encode(MagnetLink(display_name="Sarah Gaidi", address_tracker=["1.2.3.4", "5.6.7.8"]))
