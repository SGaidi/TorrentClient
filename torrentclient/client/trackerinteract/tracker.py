import re
import logging


class Tracker:
    """Data class of BitTorrent tracker URL"""

    URL_PATTERN = re.compile(r"(?P<protocol>wss|http|udp)://(?P<hostname>[.\w]+)(:(?P<port>[0-9]+))?(/announce)?")

    logger = logging.getLogger('tracker')

    class Exception(Exception):
        """An exception with Tracker URL occurred"""

    def __init__(self, url: str):
        self.url = url
        match = Tracker.URL_PATTERN.match(url)
        if match is None:
            raise Tracker.Exception("Invalid Tracker URL scheme: {}".format(self.url))
        self.protocol = match.group("protocol")
        if self.protocol != "http":
            raise Tracker.Exception("Unsupported protocol ({})".format(self.protocol))
        self.hostname = match.group("hostname")
        self.port = match.group("port")

    def __str__(self):
        return "Tracker(url={})".format(self.url)

    def __repr__(self):
        return {'protocol': self.protocol, 'hostname': self.hostname, 'port': self.port}
