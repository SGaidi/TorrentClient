import logging

from torrentclient.mytorrent import MyTorrent
from torrentclient.peerinteract.peer import Peer
from torrentclient.trackerinteract.tracker import Tracker


class RequestPeers:
    """Class for requesting peers for a Torrent from a specific Tracker,
    Only standard HTTP GET from BitTorrent protocol is supported."""

    LOCAL_PORTS = list(range(6881, 6889 + 1))

    # TODO: update trackers interval
    # probably in a different class
    TRACKER_INTERVALS = {}
    DEFAULT_INTERVAL = 1000  # seconds

    logger = logging.getLogger("request-peers")

    class Exception(Exception):
        """An exception with requesting peers occurred"""

    def __init__(self, tracker: Tracker, torrent: MyTorrent):
        self.tracker = tracker
        self.torrent = torrent

    def __str__(self):
        return "RequestPeers(tracker={}, torrent={})".format(self.tracker, self.torrent)

    @classmethod
    def _get_local_port(cls) -> int:
        """returns a number of an open port, if exist
        returns None otherwise"""
        import socket
        for port in cls.LOCAL_PORTS:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                try:
                    sock.bind(('localhost', port))
                except Exception as e:
                    cls.logger.error("Unexpected exception when checking local port {}: {}".format(port, e))
                    continue
                else:
                    return port
        raise RequestPeers.Exception("Could not find any open local port from: {}".format(RequestPeers.LOCAL_PORTS))

    def send(self):
        import requests
        try:
            return requests.get(
                url=self.tracker.url,
                params={
                    "info_hash": self.torrent.infohash,
                    "peer_id": Peer.LOCAL_PEER_ID,
                    "port": str(self._get_local_port()),
                    "uploaded": "0",
                    "downloaded": "0",
                    "left": str(self.torrent.total_length),
                    "compact": "1",
                    "event": "started",
                },
            )
        except requests.exceptions.ConnectionError as e:
            raise RequestPeers.Exception("Could not send HTTP GET to {}: {}".format(self.tracker.url, e))
