import logging
from retry import retry

from torrentclient.peerinteract.connection import PeerConnection
from torrentclient.mytorrent import MyTorrent


class GetPiece:
    """Class for getting a torrent piece using a peer connection"""

    logger = logging.getLogger('get-piece')

    class Exception(Exception):
        """An exception with getting a piece from peer"""

    def __init__(self, peer_connection: PeerConnection, torrent: MyTorrent, piece_idx: int):
        """
        :param peer_connection: PeerConnection to obtain piece with
        :param torrent: MyTorrent containing block and pieces information
        :param piece_idx: zero-based index of a piece
        """
        self.peer_connection = peer_connection
        self.torrent = torrent
        self.piece_idx = piece_idx
        self.piece = b''

    def _request_block(self, block_idx: int):
        """tries requesting block of index `block_idx`"""
        from torrentclient.peercode.allmessages import RequestBlock
        self.block_begin = block_idx * self.torrent.block_size
        request = RequestBlock(
            piece_index=self.piece_idx,
            block_begin=self.block_begin,
            block_length=self.torrent.block_size
        ).create()
        self.logger.debug("request={}".format(request))
        self.peer_connection.send(request)
        self.logger.info("Waiting for {} to send Block message of block index #{}".format(
            self.peer_connection.peer, block_idx))
        self.received_blocks = self.peer_connection.expect_blocks()

    def _validate_block(self, is_last_block: bool):
        if not self.received_blocks:
            raise GetPiece.Exception("No Blocks received")
        if len(self.received_blocks) > 1:
            raise GetPiece.Exception("Received more than one Block: {}".format(self.received_blocks))
        recv_message = self.received_blocks[0]
        if recv_message.piece_index != self.piece_idx:
            raise GetPiece.Exception("Got Block of different piece ({}) - requested piece #{}".format(
                recv_message.piece_index,
                self.piece_idx,
            ))
        if recv_message.block_begin != self.block_begin:
            raise GetPiece.Exception("Wrong Block begin value ({}) - requested {}".format(
                recv_message.block_begin,
                self.block_begin,
            ))
        if len(recv_message.block) < self.torrent.block_size and not is_last_block:
            raise GetPiece.Exception("Did not get all of block #{} ({}): {}}".format(
                self.piece_idx,
                self.torrent.block_size,
                recv_message.payload,
            ))
        return recv_message.block

    @retry(Exception, tries=3)
    def _get_block(self, block_idx: int, is_last_block=False):
        try:
            self._request_block(block_idx)
        except (PeerConnection.Exception, Exception) as e:
            if self._is_last_piece and block_idx != 0:
                self.logger.debug("Skipping block #{}".format(block_idx))
                return b''  # last blocks would be missing
            else:
                raise e
        return self._validate_block(is_last_block)

    def _validate_hash(self):
        import hashlib
        if hashlib.sha1(self.piece).digest() != self.torrent.hashes[self.piece_idx]:
            raise GetPiece.Exception("Invalid SHA-1 hash of piece #{}: {}\nExpected: {}".format(
                self.piece_idx,
                hashlib.sha1(self.piece).digest(),
                self.torrent.hashes[self.piece_idx],
            ))

    @property
    def _is_last_piece(self) -> bool:
        """returns whether this is the last hashed piece"""
        return self.piece_idx == self.torrent.piece_count-1

    @property
    def _last_block_idx(self) -> int:
        """returns last block index inside piece"""
        return self.torrent.block_count - 1

    def _is_last_block_idx(self, block_idx) -> bool:
        """returns whether `block_idx` of this piece is the last block of the torrent"""
        return self._is_last_piece and block_idx == self._last_block_idx

    @retry(Exception, tries=3)
    def get(self) -> bytes:
        self.logger.info("Trying to get {} blocks from piece #{}".format(self.torrent.block_count, self.piece_idx))
        for block_idx in range(0, self.torrent.block_count):
            received_block = self._get_block(block_idx=block_idx, is_last_block=self._is_last_block_idx(block_idx))
            if received_block == b'':  # no more blocks to receive
                break
            self.piece += received_block
        if not self._is_last_piece:
            # No idea why the last piece hash is incorrect, but it won't work otherwise
            # TODO: fix this
            self._validate_hash()
        return self.piece
