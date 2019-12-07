import re
import bencode
import logging
from typing import List

from torrentclient.client.tracker import Tracker
from torrentclient.client.peer import Peer


class RequestPeers:
    """Class for requesting peers for a Torrent from a specific Tracker
    Only standard HTTP GET from BitTorrent protocol is supported"""

    # TODO: change back to 6889
    LOCAL_PORTS = list(range(6881, 6882)) #6889 + 1))
    VALID_CONTENT_TYPES = [None, "text/plain", "text/plain; charset=utf-8", "application/octet-stream"]
    PEERS_PATTERN = re.compile(r"(?P<left>.*)5:peers(?P<length>\d+):(?P<right>.*)$")
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

        self.peer_id = "-{}{}{}-".format('BT', '1000', str(os.getpid()).zfill(12))
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
        except Exception as e:
            self.logger.debug(type(e).__name__)
            raise e

    def _check_response(self):
        if self.response.status_code != 200:
            raise RequestPeers.Exception("HTTP response status code {}".format(self.response.status_code))

        if 'Content-Type' in self.response.headers and \
                self.response.headers['Content-Type'] not in RequestPeers.VALID_CONTENT_TYPES:
            raise RequestPeers.Exception("Invalid Content-Type ({}), not in {}".format(
                self.response.headers.get('Content-Type', None), RequestPeers.VALID_CONTENT_TYPES))

        try:
            self.response.text
        except UnicodeEncodeError:
            self.logger.warning("Wrong encoding of response ({}). Apparent encoding ({}).".format(
                self.response.encoding,
                self.response.apparent_encoding
            ))
            if self.response.encoding == self.response.apparent_encoding:
                raise RequestPeers.Exception("Could not determine encoding of ({})'".format(self.response.content))
            self.response.encoding = self.response.apparent_encoding
            try:
                self.response.text
            except UnicodeEncodeError as e:
                raise RequestPeers.Exception("Could not encode ({}) with apparent encoding ({})".format(
                    self.response.content,
                ))

    def _parse_peers(self):
        match = RequestPeers.PEERS_PATTERN.match(self.response.text)
        if not match:
            raise RequestPeers.Exception("Could not match response content ({}) with pattern ({})".format(
                self.response.content, self.PEERS_PATTERN))

        left_response = match.group("left")
        peers_len = int(match.group("length"))
        peers = match.group("right")[:peers_len].encode()
        right_response = match.group("right")[peers_len:]
        self.logger.debug("left_response={}\npeers_len={}\npeers={}\nright_response={}".format(
            left_response, peers_len, peers, right_response,
        ))
        peerless_response = left_response + right_response
        response = bencode.bdecode(peerless_response.encode())
        if "failure reason" in response:
            raise RequestPeers.Exception("Failure in response text: {}".format(response["failure reason"]))
        if "warning message" in response:
            self.logger.warning("Warning in response text: {}".format(response["warning message"]))
        #TODO: handle interval in response
        self.logger.debug("response={}".format(response))

        if len(peers) % 6 != 0:
            self.logger.warning("Peers length is not divisible by 6 - omitting last bytes")
            peers = peers[:6*(len(peers)//6)]
            self.logger.debug(len(peers))

        # TODO: add support for dictionary mode
        self.peers = []
        for index in range(0, len(peers), 6):
            peer_ip_bytes = peers[index:index+4]
            peer_ip = ".".join(str(octet) for octet in peer_ip_bytes)
            peer_port = int.from_bytes(peers[index+4:index+6], byteorder="big")
            self.peers.append(Peer(peer_ip, peer_port))
        self.logger.debug("peers={}".format(", ".join(str(peer) for peer in self.peers)))

    def get(self) -> List[Peer]:
        """return a list of peers to get content according to the torrent file"""
        self._create_request()
        self._send_request()
        self._check_response()
        self._parse_peers()
        return self.peers
