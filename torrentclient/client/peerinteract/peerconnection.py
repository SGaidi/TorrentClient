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

    @lru_cache
    def socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.peer.ip_address, int(self.peer.port)))
        return self._socket
