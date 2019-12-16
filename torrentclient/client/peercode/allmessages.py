from torrentclient.client.peercode.message import PeerMessage


# basic messages


class KeepAlive(PeerMessage):
    """Peers may close a connection if they receive no messages for a certain period of time, so a keep-alive message
    must be sent to maintain the connection alive if no command have been sent for a given amount of time.
    This amount of time is generally two minutes."""

    MESSAGE_ID = None


class Choke(PeerMessage):
    """Indicating the sending peer cannot and will not handle current and future requests until un-chocked"""

    MESSAGE_ID = 0


class UnChoke(PeerMessage):
    """Indicating the sending peer can handle future requests"""

    MESSAGE_ID = 1


class Interested(PeerMessage):
    """Indicating the sending peer will send requests when the receiver is un-choked"""

    MESSAGE_ID = 2


class NotInterested(PeerMessage):
    """Indicating the sending peer will stop sendind requests"""

    MESSAGE_ID = 3


# messages regarding specific pieces and blocks


class HavePiece(PeerMessage):
    """Indicating the sending peer has successfully downloaded and verified a specific piece"""

    MESSAGE_ID = 4

    def __init__(self, piece_index: int):
        """
        :param piece_index: zero-based index of a piece that has just been downloaded and verified via the hash
        """
        if not isinstance(piece_index, int):
            raise super().Exception("piece_index must be a positive integer ({})".format(piece_index))
        super().__init__(payload=self.int_to_4bytes(piece_index))

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != 4:
            raise super().Exception("Invalid payload length ({}), should be 4 bytes".format(len(payload)))
        piece_index = int.from_bytes(payload, byteorder="big")
        return cls(piece_index=piece_index)


class PiecesBitField(PeerMessage):
    """May only be sent immediately after the handshaking sequence is completed, and before any other messages are sent,
    It is optional, and need not be sent if a client has no pieces."""

    MESSAGE_ID = 5

    def __init__(self, bitfield: bytes):
        """"
        :param bitfield: representing the pieces that have been successfully downloaded,
            where the high bit in the first byte corresponds to piece index 0.
            spare bits at the end are set to zero.
        """
        super().__init__(payload=bitfield)

    @classmethod
    def from_payload(cls, payload: bytes):
        return cls(bitfield=payload)


class RequestBlock(PeerMessage):
    """Request of a specific block from a piece"""

    MESSAGE_ID = 6

    def __init__(self, piece_index: int, block_begin: int, block_length: int):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block_length: block length in bytes, use of 2^14 (16KB) is recommended by BitTorrent specifications
        """
        super().__init__(
            payload=self.int_to_4bytes(piece_index) + self.int_to_4bytes(block_begin) + self.int_to_4bytes(block_length)
        )

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != 12:
            raise super().Exception("Invalid payload length ({}), should be 4 bytes".format(len(payload)))
        piece_index = int.from_bytes(payload[:4], byteorder="big")
        block_begin = int.from_bytes(payload[4:8], byteorder="big")
        block_length = int.from_bytes(payload[8:12], byteorder="big")
        return cls(piece_index, block_begin, block_length)


class Block(PeerMessage):
    """A block from a piece"""

    MESSAGE_ID = 7

    def __init__(self, piece_index: int, block_begin: int, block: bytes):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block: block content
        """
        self.piece_index = piece_index
        self.block_begin = block_begin
        self.block = block
        super().__init__(payload=self.int_to_4bytes(piece_index) + self.int_to_4bytes(block_begin) + block)

    @classmethod
    def from_payload(cls, payload: bytes):
        piece_index = int.from_bytes(payload[:4], byteorder="big")
        block_begin = int.from_bytes(payload[4:8], byteorder="big")
        block = payload[8:]
        return cls(piece_index, block_begin, block)


class CancelRequest(PeerMessage):
    """Cancel block requests (Request class)"""

    MESSAGE_ID = 8

    def __init__(self, piece_index: int, block_begin: int, block_length: int):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block_length: block length in bytes, use of 2^14 (16KB) is recommended by BitTorrent specifications
        """
        self.piece_index = piece_index
        self.block_begin = block_begin
        self.block_length = block_length
        super().__init__(
            payload=self.int_to_4bytes(piece_index) + self.int_to_4bytes(block_begin) + self.int_to_4bytes(block_length)
        )

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != 12:
            raise super().Exception("Invalid payload length ({}), should be 12 bytes".format(len(payload)))
        piece_index = int.from_bytes(payload[:4], byteorder="big")
        block_begin = int.from_bytes(payload[4:8], byteorder="big")
        block_length = int.from_bytes(payload[8:12], byteorder="big")
        return cls(piece_index, block_begin, block_length)


class Port(PeerMessage):
    """Sent by newer versions of the Mainline that implements a DHT tracker.
    The listen port is the port this peer's DHT node is listening on.
    This peer should be inserted in the local routing table"""

    MESSAGE_ID = 9

    def __init__(self, listen_port: int):
        self.listen_port = listen_port
        super.__init__(payload=self.int_to_4bytes(listen_port))

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != 4:
            raise super().Exception("Invalid payload length ({}), should be 4 bytes".format(len(payload)))
        listen_port = int.from_bytes(payload[:4], byteorder="big")
        return cls(listen_port)


all_messages = [
    KeepAlive, Choke, UnChoke, Interested, NotInterested,
    HavePiece, PiecesBitField, RequestBlock, Block, CancelRequest, Port
]

id_to_message = {}
for message in all_messages:
    id_to_message[message.MESSAGE_ID] = message
