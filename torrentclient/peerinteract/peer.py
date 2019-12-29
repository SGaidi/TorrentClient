import os
import socket
import logging

from torf import Torrent


class Peer:
    """Data class of BitTorrent remote peer"""

    LOCAL_PEER_ID = bytes("-{}{}-{}".format('SG', '1000', str(os.getpid()).zfill(12)), "utf-8")

    logger = logging.getLogger('peer')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, ip_address: str, port: int):
        """
        :param ip_address: IPv4 address str
        :param port: port number
        """
        import socket
        try:
            socket.inet_aton(ip_address)
        except socket.error as e:
            raise Peer.Exception("Invalid IP address ({}): {}".format(ip_address, e))
        self.ip_address = ip_address
        try:
            self.port = int(port)
        except TypeError:
            raise Peer.Exception("Invalid port type ({}) - should be convertible to int".format(type(port).__name__))
        self.id = None  # determined in PeerHandshake response

    def __eq__(self, other):
        return isinstance(other, Peer) and self.ip_address == other.ip_address and self.port == other.port

    def __hash__(self):
        return hash((
            'ip_address', self.ip_address,
            'port', self.port,
        ))

    def __str__(self):
        return "Peer({}:{})".format(self.ip_address, self.port)
