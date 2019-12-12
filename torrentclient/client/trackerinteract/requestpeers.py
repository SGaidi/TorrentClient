import bencode
import logging

from torrentclient.client.trackerinteract.tracker import Tracker


class RequestPeers:
    """Class for requesting peers for a Torrent from a specific Tracker
    Only standard HTTP GET from BitTorrent protocol is supported"""

    # TODO: change back to 6889
    LOCAL_PORTS = list(range(6881, 6882)) #6889 + 1))

    # TODO: update trackers interval
    # probably in a different class
    TRACKER_INTERVALS = {}
    DEFAULT_INTERVAL = 1000  # seconds

    logger = logging.getLogger("request-peers")

    class Exception(Exception):
        """An exception with requesting peers occurred"""

    def __init__(self, tracker: Tracker, torrent_path: str):
        self.tracker = tracker
        self.torrent_path = torrent_path

    def __str__(self):
        return "RequestPeers(tracker={}, torrent_path={})".format(self.tracker, self.torrent_path)

    def __repr__(self):
        return {'tracker': self.tracker, 'torrent_path': self.torrent_path}

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

    def _create_request(self):
        """set all standard parameters for request"""
        import os
        import hashlib
        # TODO: should be part of custom Torrent class
        bcode = bencode.bread(self.torrent_path)
        self.hash_info = hashlib.sha1(bencode.bencode(bcode['info'])).digest()
        self.peer_id = "-{}{}-{}".format('BT', '1000', str(os.getpid()).zfill(12))
        if 'length' in bcode['info']:
            self.left = bcode['info']['length']
        else:
            self.left = 0
            for file in bcode['info']['files']:
                self.left += file['length']
        self.port = self._get_local_port()

    def _send_request(self):
        import requests
        try:
            self.response = requests.get(
                url=self.tracker.url,
                params={
                    "info_hash": self.hash_info,
                    "peer_id": self.peer_id,
                    "port": str(self.port),
                    "uploaded": "0",
                    "downloaded": "0",
                    "left": str(self.left),
                    "compact": "1",
                    "event": "started",
                },
            )
        except requests.exceptions.ConnectionError as e:
            raise RequestPeers.Exception("Could not send HTTP GET to {}: {}".format(self.tracker.url, e))

    def get(self):
        """returns a list of peers to get content according to the torrent file"""
        self._create_request()
        self._send_request()
        return self.response
