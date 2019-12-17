import socket
import logging

from torrentclient.client.peerinteract.connection import PeerConnection
from torrentclient.torcode.mytorrent import MyTorrent
from torrentclient.client.peercode.allmessages import RequestBlock


class GetPiece:
    """Class for getting a torrent piece using a peer connection"""

    RECEIVE_BLOCK_RETRY = 3

    logger = logging.getLogger('get-piece')

    class Exception(Exception):
        """An exception with getting a piece from peer"""

    def __init__(self, peer_connection: PeerConnection, torrent: MyTorrent, piece_idx: int):
        self.peer_connection = peer_connection
        self.torrent = torrent
        self.piece_idx = piece_idx

    def get(self) -> bytes:
        recv_piece = b''
        request = RequestBlock(
            piece_index=self.piece_idx, block_begin=0, block_length=self.torrent.piece_size
        ).create()
        self.logger.debug("request={}".format(request))
        self.peer_connection.send(request)
        self.logger.info("Waiting for {} to send Block message".format(self.peer_connection.peer))
        errors = []
        for retry_count in range(1, self.RECEIVE_BLOCK_RETRY+1):
            self.logger("Try #{} out of {}".format(retry_count, self.RECEIVE_BLOCK_RETRY))
            try:
                recv_block = self.peer_connection.expect_blocks()
                if not recv_block:
                    raise GetPiece.Exception("No Blocks received")
                recv_block = recv_block[0].payload

                # TODO: should be removed
                while len(recv_piece) < self.torrent.piece_size and recv_block != b'':
                    self.logger.info("Received {} bytes of block".format(len(recv_block)))
                    omit_length = len(recv_piece)
                    recv_piece += recv_block
                    recv_block = self.peer_connection.socket.recv(self.torrent.piece_size-omit_length)

                if len(recv_piece) < 2**14:
                    raise GetPiece.Exception("Did not get all of piece #{} ({}) - length ({})".format(
                        self.piece_idx,
                        self.torrent.piece_size,
                        len(recv_piece)
                    ))
            except GetPiece.Exception as e:
                errors.append(e)
            else:
                break
        """
        if hashlib.sha1(piece).digest() != \
            self.torrent.hashes[self.piece_idx*subpieces_count+subpiece_idx]:
            raise GetPiece.Exception("Invalid SHA-1 hash of sub-piece #{} in piece #{}".format(subpiece_idx, self.piece_idx))
        """
        # TODO: check hashes!!!
        return recv_piece
