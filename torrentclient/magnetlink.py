import html
import urllib.parse


class MagnetLink:
    """Class for extracting all supported information from a magnet link
    Reference: https://en.wikipedia.org/wiki/Magnet_URI_scheme
    """

    def __init__(self, value: str):
        self.value = value
        try:
            self.__parsed = urllib.parse.parse_qs(value.split('magnet:?')[1])
        except Exception as e:
            raise ValueError("Could not parse magnet link '{}': {}".format(value, e))

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
        """tracker URL for BitTorrent downloads"""
        return self.__parsed['tr']

    @staticmethod
    def is_experimental_param(param: str) -> bool:
        return param.startswith('x.') and param[2:].isalpha()

    @property
    def experimental_parameters(self) -> dict:
        """application-specific experimental parameters"""
        return dict({key: value for key, value in self.__parsed.items() if self.is_experimental_param(key)})

    def __getattr__(self, name):
        """gets called only if no attributes of `self` instance matches `name`
        tries to find a match in experimental parameters"""
        if name in self.experimental_parameters:
            return self.experimental_parameters[name]
        else:
            raise AttributeError


def convert(magnet_link: str):
    magnet_link = html.unescape(magnet_link)
    magnet_parsed = urllib.parse.parse_qs(magnet_link.split('magnet:?')[1])
    print(magnet_parsed)


"""
#Add the trackers
magnetLink = base
for tracker in trackers:
    magnetLink += '&tr=' + tracker

# TODO: URN parser in separate class
#Create the torrent file name
magnetName = magnetLink[magnetLink.find("btih:") + 1:magnetLink.find("&")]
magnetName = magnetName.replace('tih:','')
torrentfilename = 'meta-' + magnetName + '.torrent'

# TODO: pass all these parameters to Torrent class
#Write the magnet link to the torrent file
with open(torrentfilename, 'w') as o:
    linkstr = u'd10:magnet-uri' + str(len(magnetLink)) + u':' + magnetLink + u'e'
    linkstr = linkstr.encode('utf8')
    o.write(linkstr)
"""
convert('magnet:?xt=urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858&dn=wikipedia_en_all_novid_2018-06.zim&tr=udp%3a%2f%2ftracker.mg64.net')