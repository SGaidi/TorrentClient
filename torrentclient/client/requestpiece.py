import logging

from torf import Torrent

from torrentclient.client.peer import Peer


class RequestPiece:
    """Class for requesting a piece of a Torrent from a specific Peer"""

    logger = logging.getLogger("request-piece")

    class Exception(Exception):
        """An exception with requesting a piece occurred"""

    def __init__(self, peer: Peer, torrent: Torrent, piece: int):
        self.peer = peer
        self.torrent = torrent
        self.piece = piece

    def __str__(self):
        return "RequestPiece(peer={}, torrent={}, piece={})".format(self.peer, self.torrent, self.piece)

    def __repr__(self):
        return {'peer': self.peer, 'torrent': self.torrent, 'piece': self.piece}

    def get(self) -> bytes:
        pass
