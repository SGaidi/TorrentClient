import html
import urllib.parse

from torrentclient.mlcode.magnetlink import MagnetLink
from torrentclient.mlcode.defineparam import DefineParam as dp


def decode(magnet_link: str):
    """
    :param magnet_link: str of encoded magnet-link
    :return: MagnetLink with URI parameters
    """
    magnet_link = html.unescape(magnet_link)
    magnet_dict = urllib.parse.parse_qs(magnet_link.split('magnet:?')[1])
    for key, value in magnet_dict.items():
        # flatten one-item lists
        if isinstance(value, list) and len(value) == 1:
            magnet_dict[key] = value[0]
    kwargs = {}
    for key, value in magnet_dict.items():
        defined_param = dp.match_key(key)
        if defined_param is None:
            raise ValueError("decode() cannot classify '{}' param.".format(key))
        kwargs[defined_param.name] = value
    return MagnetLink(**kwargs)
