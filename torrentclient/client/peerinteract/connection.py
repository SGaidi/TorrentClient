import socket
import logging
from functools import lru_cache

from torrentclient.client.peerinteract.peer import Peer


class PeerConnection:
    """Class for a Peer wire protocol TCP connection"""

    logger = logging.getLogger('peer-connection')

    class Exception(Exception):
        """An exception with connection to peer occurred"""

    def __init__(self, peer: Peer):
        self.peer = peer
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

    @lru_cache()
    def socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.peer.ip_address, int(self.peer.port)))
        return self._socket

    def _wait_peer_unchokes(self):
        pass

    def _tell_peer_unchoked(self):
        pass

    def _tell_peer_interested(self):
        pass

    def send(self, message: bytes):
        """wrapper of socket.send, applying BitTorrent specifications with `choking` and `interested` values"""
        while self.peer_choking or self.am_choking or not self.am_interested:
            if self.peer_choking:
                self._wait_peer_unchokes()
            if self.am_choking:
                self._tell_peer_unchoked()
            if not self.am_interested:
                self._tell_peer_interested()
        self.socket.send(self.request)

    def read(self) -> bytes:
        """wrapper of socket.read, applying BitTorrent specifications with `choking` and `interested` values"""
        pass
