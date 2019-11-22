import html
import urllib.parse
from torrentclient.mlcode.defineparam import DefineParam as df
from torrentclient.mlcode.magnetlink import MagnetLink


def decode(magnet_link: str):
    """
    :param magnet_link: string of encoded magnet-link
    :return: MagnetLink object
    """
    magnet_link = html.unescape(magnet_link)
    magnet_dict = urllib.parse.parse_qs(magnet_link.split('magnet:?')[1])
    kwargs = {}
    for key, value in magnet_dict.items():
        defined_param = df.match_param(key)
        if defined_param is None:
            raise ValueError("decode() cannot classify '{}' param.".format(key))
        kwargs[defined_param.name] = value
    return MagnetLink(**kwargs)


decode('magnet:?dn=Sarah+Gaidi&tr=1.2.3.4&tr=5.6.7.8')
decode('magnet:?xt=urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858&dn=wikipedia_en_all_novid_2018-06.zim&tr=udp%3a%2f%2ftracker.mg64.net')