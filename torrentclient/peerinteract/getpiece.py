import logging
from retry import retry

from torrentclient.peerinteract.connection import PeerConnection
from torrentclient.mytorrent import MyTorrent
from torrentclient.peercode.allmessages import RequestBlock


class GetPiece:
    """Class for getting a torrent piece using a peer connection"""

    logger = logging.getLogger('get-piece')

    class Exception(Exception):
        """An exception with getting a piece from peer"""

    def __init__(self, peer_connection: PeerConnection, torrent: MyTorrent, piece_idx: int):
        self.peer_connection = peer_connection
        self.torrent = torrent
        self.piece_idx = piece_idx
        self.previous_sha = None

    @retry(Exception, tries=3)
    def get_block(self, block_idx: int, is_last_block: False):
        block_begin = block_idx * self.torrent.block_size
        request = RequestBlock(
            piece_index=self.piece_idx,
            block_begin=block_begin,
            block_length=self.torrent.block_size
        ).create()
        self.logger.debug("request={}".format(request))
        self.peer_connection.send(request)
        self.logger.info("Waiting for {} to send Block message of block index #{}".format(
            self.peer_connection.peer, block_idx))
        recv_messages = self.peer_connection.expect_blocks()
        if not recv_messages:
            raise GetPiece.Exception("No Blocks received")
        if len(recv_messages) > 1:
            raise GetPiece.Exception("Received more than one Block: {}".format(recv_messages))
        recv_message = recv_messages[0]
        if recv_message.piece_index != self.piece_idx:
            raise GetPiece.Exception("Got Block of different piece ({}) - requested piece #{}".format(
                recv_message.piece_index,
                self.piece_idx,
            ))
        if recv_message.block_begin != block_begin:
            raise GetPiece.Exception("Wrong Block begin value ({}) - requested {}".format(
                recv_message.block_begin,
                block_begin,
            ))
        if len(recv_message.block) < self.torrent.block_size and not is_last_block:
            raise GetPiece.Exception("Did not get all of block #{} ({}): {}}".format(
                self.piece_idx,
                self.torrent.block_size,
                recv_message.payload,
            ))
        return recv_message.block

    @retry(Exception, tries=3)
    def get(self) -> bytes:
        import hashlib
        piece = b''
        if self.piece_idx == self.torrent.piece_count-1:
            last_block_idx = self.torrent.block_count - 1
        else:
            last_block_idx = -1
        self.logger.info("Trying to get {} blocks from piece #{}".format(self.torrent.block_count, self.piece_idx))
        # TODO: if it is the last piece - some blocks requests will fail or return smaller blocks
        for block_idx in range(0, self.torrent.block_count):
            is_last_block = block_idx == last_block_idx
            piece += self.get_block(block_idx=block_idx, is_last_block=is_last_block)
        if hashlib.sha1(piece).digest() != self.torrent.hashes[self.piece_idx]:
            if self.previous_sha is not None and self.previous_sha == hashlib.sha1(piece).digest():
                self.logger.warning("SHA-1 of previous requests are the same!")
            raise GetPiece.Exception("Invalid SHA-1 hash of piece #{}: {}\nExpected: {}".format(
                self.piece_idx,
                hashlib.sha1(piece).digest(),
                self.torrent.hashes[self.piece_idx],
            ))
        return piece
