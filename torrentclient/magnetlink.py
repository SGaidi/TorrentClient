import html
import functools
import urllib.parse


class MagnetLink:
    """Class for extracting all BitTorrent supported information from a magnet link.

    Reference:
        https://en.wikipedia.org/wiki/Magnet_URI_scheme
        https://libtorrent.org/manual.html#magnet-links - BitTorrent minimal parameters used in libtorrent.

    Parameters used in libtorrent:
        `Display Name` - Supported by all clients.
        `Exact Topic` - Each client implements different encryption & decryption methods,
            libtorrent uses BTIH (BitTorrent Info Hash), which is most common.
        `Address Tracker` - List of trackers, supported by most clients.

    Optional parameters:
        `Exact Length` - Supported by most clients.
        `Exact Source` - Direct or backup source (HTTPS, FTPS, etc) at P2P source with file hash,
            supported by some clients.
        `Acceptable Source` - Direct download from a web server, supported by some clients.

    Rarely used parameters:
        `Keyword Topic` - List of search words used in P2P networks.
        `Manifest` - Link to a list of links (web, URN).
    """

    SUPPORTED_PARAMS = {
        'dn': "Display Name",
        'xl': "Exact Length",
        'xt': "Exact Topic",
        'as': "Acceptable Source",
        'xs': "Exact Source",
        'kt': "Keyword Topic",
        'mt': "Manifest Topic",
        'tr': "Address Tracker",
    }

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("MagnetLink value ({}) is of type ({}), should be str".format(value, type(value).__name__))
        try:
            self.__parsed = urllib.parse.parse_qs(value.split('magnet:?')[1])
        except Exception as e:
            raise ValueError("Could not parse magnet link '{}': {}".format(value, e))

    def __str__(self):
        return "MagnetLink '{}'".format(self.display_name)

    @property
    def display_name(self) -> str:
        """filename for convenience"""
        return self.__parsed['dn']

    @property
    def exact_length(self) -> int:
        """size in Byes"""
        return int(self.__parsed['xl'])

    @property
    def exact_topic(self) -> str:
        """URN containing file hash"""
        return self.__parsed['xt']

    @property
    def acceptable_source(self) -> str:
        """web link to the file online"""
        return self.__parsed['as']

    @property
    def exact_source(self) -> str:
        """P2P link identified by a content-hash"""
        return self.__parsed['xs']

    @property
    def keyword_topic(self) -> str:
        """a general search, specifying keywords, rather than a particular file"""
        return self.__parsed['kt']

    @property
    def manifest_topic(self) -> str:
        """link to the meta-file that contains a list of magneto"""
        return self.__parsed['mt']

    @property
    def address_tracker(self) -> list:
        """tracker URLs for BitTorrent downloads"""
        return self.__parsed['tr']

    @staticmethod
    def __is_experimental_param(param: str) -> bool:
        return param.startswith('x.') and param[2:].isalpha()

    @property
    @functools.lru_cache()
    def experimental_parameters(self) -> dict:
        """application-specific experimental parameters"""
        return dict({key: value for key, value in self.__parsed.items() if self.__is_experimental_param(key)})

    def __getattr__(self, name):
        """gets called only if no attributes of `self` instance matches `name`
        tries to find a match in experimental parameters"""
        if name in self.experimental_parameters:
            return self.experimental_parameters[name]
        else:
            raise AttributeError


def encode(values: dict):
    """TODO: TBD"""
    return "magnet:?{}".format(urllib.urlencode(values))


def decode(text: str):
    return MagnetLink(text)


def convert(magnet_link: str):
    magnet_link = html.unescape(magnet_link)
    magnet_parsed = urllib.parse.parse_qs(magnet_link.split('magnet:?')[1])
    print(magnet_parsed)
    ml = MagnetLink(magnet_link)
    print(ml.experimental_parameters)


convert('magnet:?xt=urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858&dn=wikipedia_en_all_novid_2018-06.zim&tr=udp%3a%2f%2ftracker.mg64.net')