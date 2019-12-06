import re
import os
import logging
import bencode

from torrentclient.client.tracker import Tracker


class RequestPeers:
    """Class for requesting peers for a Torrent from a specific Tracker
    Only standard HTTP GET from BitTorrent protocol is supported"""

    DEFAULT_INTERVAL = 1000  # seconds
    # TODO: change back to 6889
    LOCAL_PORTS = list(range(6881, 6882)) #6889 + 1))
    VALID_CONTENT_TYPES = ["text/plain", "application/octet-stream"]
    PEERS_PATTERN = re.compile(r"(?P<left>.*)5:peers(?P<length>\d+):(?P<right>.*)$")
    # TODO: update trackers interval
    # probably in a different class
    TRACKER_INTERVALS = {}

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
                    cls.logger.warning("Unexpected exception when checking local port {}: {}".format(port, e))
                    continue
                else:
                    return port
        raise RequestPeers.Exception("Could not find any open local port from: {}".format(RequestPeers.LOCAL_PORTS))

    def _create_request(self):
        """set all standard parameters for request"""
        import hashlib
        # TODO: should be part of custom Torrent class
        bcode = bencode.bread(self.torrent_path)
        self.hash_info = hashlib.sha1(bencode.bencode(bcode['info'])).digest()

        self.peer_id = "-{}{}{}-".format('BT', '1000', str(os.getpid()).zfill(12))
        if 'length' in bcode['info']:
            self.left = bcode['info']['length']
        else:
            self.left = 0
            for file in bcode['info']['files']:
                self.left += file['length']
        self.port = self._get_local_port()

    def _send(self):
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
        except Exception as e:
            raise RequestPeers.Exception("Could not send HTTP GET to {}: {}".format(self.tracker.url, e))

    def _check_response(self):
        if self.response.status_code != 200:
            raise RequestPeers.Exception("HTTP response status code {}".format(self.response.status_code))

        self.logger.debug("\n".join("{}={}".format(key, value) for key, value in self.response.__dict__.items()))
        return

        if self.response.headers['Content-Type'] not in RequestPeers.VALID_CONTENT_TYPES:
            raise RequestPeers.Exception("Invalid Content-Type ({}), not in {}".format(
                self.response.headers['Content-Type'], RequestPeers.VALID_CONTENT_TYPES))

        # STOP HERE
        return

        # TODO: rename 'text'
        try:
            text = self.response.text
        except UnicodeEncodeError:
            self.logger.warning("Wrong encoding of response ({}). Apparent encoding ({}).".format(
                self.response.encoding,
                self.response.apparent_encoding
            ))
            self.response.encoding = self.response.apparent_encoding
            text = self.response.text.encode('utf-8')
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        elif not isinstance(text, str):
            raise RequestPeers.Exception("Invalid response text type ({}), not str".format(type(text).__name__))

    def _parse_peers(self):
        from urllib.parse import quote_from_bytes, unquote
        match = RequestPeers.PEERS_PATTERN.match(self.text)
        if not match:
            raise RequestPeers.Exception("Could not match response text '{}' with pattern '{}'".format(
                self.text, self.PEERS_PATTERN))

        left_response = match.group("left")
        peers_len = int(match.group("length"))
        peers = match.group("right")[:peers_len]
        right_response = match.group("right")[peers_len:]
        self.logger.debug("left_response={}\npeers_len={}\npeers={}\nright_response={}".format(
            left_response, peers_len, peers, right_response,
        ))
        # quote_from_bytes(peers)
        peerless_response = left_response + right_response
        self.logger.debug("peerless_response={}".format(peerless_response))
        response = bencode.bdecode(peerless_response.encode())
        if "failure reason" in response:
            raise RequestPeers.Exception("Failure in response text: {}".format(response["failure reason"]))
        if "warning message" in response:
            self.logger.warning("Warning: {}".format(response["warning message"]))
        self.logger.debug(response)
        self.logger.info("success!")

    def get(self) -> list:
        """return a list of peers to get content according to the torrent file"""
        self._create_request()
        self._send()
        self._check_response()
        #self._parse_peers()
