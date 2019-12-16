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
        subpieces = []
        subpieces_count = round(self.torrent.piece_size / self.torrent.subpiece_size)
        self.logger.debug("self.torrent.piece_size={}, self.torrent.subpiece_size={}".format(
            self.torrent.piece_size,
            self.torrent.subpiece_size,
        ))
        for subpiece_idx, subpiece_start in enumerate(range(0, self.torrent.piece_size, self.torrent.subpiece_size)):
            self.logger.debug("subpiece_idx={}, subpiece_start={}, ".format(
                subpiece_idx,
                subpiece_start,
            ))
            self.logger.info("Fetching sub-piece #{} of piece #{} of size {}".format(
                subpiece_idx,
                self.piece_idx,
                self.torrent.subpiece_size,
            ))
            piece = b''
            for block_idx, block_start in enumerate(range(0, self.torrent.subpiece_size, 2**14)):
                self.logger.info("Requesting block #{} of sub-piece #{} of piece #{}".format(
                    block_idx, subpiece_idx, self.piece_idx))
                request = RequestBlock(
                    piece_index=self.piece_idx, block_begin=block_start, block_length=2**14
                ).create()
                self.logger.debug("request={}".format(request))
                self.peer_connection.send(request)
                self.logger.info("Waiting for a block from {}".format(self.peer_connection.peer))
                recv_blocks = self.peer_connection.expect_blocks()
                if len(recv_blocks) == 0:
                    raise GetPiece.Exception("Could not get block #{}".format(block_idx))
                elif len(recv_blocks) > 1:
                    self.logger.warning("Got more than one block - {}".format(
                        ", ".join("#{}".format(block_msg.block_id) for block_msg in recv_blocks))
                    )
                self.logger.info(recv_blocks[0])
                piece += recv_blocks[0].block
            if hashlib.sha1(piece).digest() != \
                    self.torrent.hashes[self.piece_idx*subpieces_count+subpiece_idx]:
                raise GetPiece.Exception("Invalid SHA-1 hash of sub-piece #{} in piece #{}".format(subpiece_idx, self.piece_idx))
            subpieces.append(piece)
        return b''.join(subpieces)
