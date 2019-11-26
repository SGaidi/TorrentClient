import urllib.parse

from torrentclient.mlcode.magnetlink import MagnetLink


def encode(ml_obj: MagnetLink) -> str:
    """
    :param ml_obj: MagnetLink with URI parameters
    :return: str of encoded magnet-link
    """
    ml_pairs = []
    ml_str = "magnet:?"
    for ml_attr_name, ml_attr_value in ml_obj.__dict__.items():
        defined_param = MagnetLink.dp.match_name(ml_attr_name)
        if defined_param is None:
            raise ValueError("encode() cannot classify '{}' attribute name.".format(ml_attr_name))
        if isinstance(ml_attr_value, list):
            for obj_attr_item in ml_attr_value:
                ml_pairs.append((defined_param.key, obj_attr_item))
        elif ml_attr_name != "exact_topic":
            ml_pairs.append((defined_param.key, ml_attr_value))
        else:
            ml_str += "xt=urn:btih:" + ml_attr_value.split("urn:btih:")[1] + '&'
    return ml_str + urllib.parse.urlencode(ml_pairs)
