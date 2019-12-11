from torrentclient.client.peercode.parentmessage import PeerMessage


# basic messages


class KeepAlive(PeerMessage):
    """Peers may close a connection if they receive no messages for a certain period of time, so a keep-alive message
    must be sent to maintain the connection alive if no command have been sent for a given amount of time.
    This amount of time is generally two minutes."""


class Choke(PeerMessage):
    """Indicating the sending peer cannot and will not handle current and future requests until un-chocked"""

    def __init__(self):
        super().__init__(message_id=0)


class UnChoke(PeerMessage):
    """Indicating the sending peer can handle future requests"""

    def __init__(self):
        super().__init__(message_id=1)


class Interested(PeerMessage):
    """Indicating the sending peer will send requests when the receiver is un-choked"""

    def __init__(self):
        super().__init__(message_id=2)


class NotInterested(PeerMessage):
    """Indicating the sending peer will stop sendind requests"""

    def __init__(self):
        super().__init__(message_id=2)


# messages regarding specific pieces and blocks


class HavePiece(PeerMessage):
    """Indicating the sending peer has successfully downloaded and verified a specific piece"""

    def __init__(self, piece_index: int):
        """
        :param piece_index: zero-based index of a piece that has just been downloaded and verified via the hash
        """
        if not isinstance(piece_index, int):
            raise super().Exception("piece_index must be a positive integer ({})".format(piece_index))
        super().__init__(message_id=4, payload=self.int_to_bytes(piece_index))


class PiecesBitField(PeerMessage):
    """May only be sent immediately after the handshaking sequence is completed, and before any other messages are sent,
    It is optional, and need not be sent if a client has no pieces."""

    def __init__(self, bitfield: bytes):
        """"
        :param bitfield: representing the pieces that have been successfully downloaded,
            where the high bit in the first byte corresponds to piece index 0.
            spare bits at the end are set to zero.
        """
        super().__init__(message_id=5, payload=bitfield)


class RequestBlock(PeerMessage):
    """Request of a specific block from a piece"""

    def __init__(self, piece_index: int, block_begin: int, block_length: int):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block_length: block length in bytes, use of 2^14 (16KB) is recommended by BitTorrent specifications
        """
        super().__init__(
            message_id=6,
            payload=self.int_to_bytes(piece_index) + self.int_to_bytes(block_begin) + self.int_to_bytes(block_length)
        )


class Block(PeerMessage):
    """A block from a piece"""

    def __init__(self, piece_index: int, block_begin: int, block: bytes):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block: block content
        """
        super().__init__(
            message_id=7,
            payload=self.int_to_bytes(piece_index) + self.int_to_bytes(block_begin) + block
        )


class CancelRequest(PeerMessage):
    """Cancel block requests (Request class)"""

    def __init__(self, piece_index: int, block_begin: int, block_length: int):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block_length: block length in bytes, use of 2^14 (16KB) is recommended by BitTorrent specifications
        """
        super().__init__(
            message_id=8,
            payload=self.int_to_bytes(piece_index) + self.int_to_bytes(block_begin) + self.int_to_bytes(block_length)
        )


class Port(PeerMessage):
    """Sent by newer versions of the Mainline that implements a DHT tracker.
    The listen port is the port this peer's DHT node is listening on.
    This peer should be inserted in the local routing table"""

    def __init__(self, listen_port: int):
        super.__init__(message_id=9, payload=self.int_to_bytes(listen_port))
