import logging

from torrentclient.client.peerinteract.connection import PeerConnection
from torrentclient.torcode.mytorrent import MyTorrent
from torrentclient.client.peercode.allmessages import RequestBlock


class GetPiece:
    """Class for getting a torrent piece using a peer connection"""

    logger = logging.getLogger('get-piece')

    class Exception(Exception):
        """An exception with getting a piece from peer"""

    def __init__(self, peer_connection: PeerConnection, torrent: MyTorrent, piece_idx: int):
        self.peer_connection = peer_connection
        self.torrent = torrent
        self.piece_idx = piece_idx

    def get(self) -> bytes:
        import hashlib
        blocks = []
        blocks_in_piece = round(self.torrent.piece_size / self.torrent.block_size)
        for block_idx, block_start in enumerate(range(0, self.torrent.piece_size, self.torrent.block_size)):
            self.logger.info("Requesting block #{} of piece #{}".format(block_idx, self.piece_idx))
            request = RequestBlock(
                piece_index=self.piece_idx, block_begin=block_start, block_length=self.torrent.block_size
            ).create_message()
            self.peer_connection.send(request)
            self.logger.info("Waiting for response from {}".format(self.peer_connection.peer))
            recv_blocks = self.peer_connection.expect_blocks()
            self.logger.info(recv_blocks)
            if not recv_blocks:
                raise GetPiece.Exception("Could not get piece #{}".format(self.piece_idx))
            if hashlib.sha1(recv_blocks[0]).digest() != \
                    self.torrent.hashes[self.piece_idx*blocks_in_piece+block_idx]:
                raise GetPiece.Exception("Invalid SHA-1 hash of sub-piece #{} in piece #{}".format(block_idx, self.piece_idx))
            blocks.append(recv_blocks[0])
        return b''.join(blocks)
