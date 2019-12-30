"""All classes below inherit from PeerMessages.
Each message presents a specific message from the peer wire BitTorrent protocol."""
from torrentclient.peercode.message import PeerMessage


# basic messages


class KeepAlive(PeerMessage):
    """Peers may close a connection if they receive no messages for a certain period of time, so a keep-alive message
    must be sent to maintain the connection alive if no command have been sent for a given amount of time."""

    MESSAGE_ID = None


class Choke(PeerMessage):
    """Indicating the sending peer will not handle current and future requests until un-chocked"""

    MESSAGE_ID = 0


class UnChoke(PeerMessage):
    """Indicating the sending peer will handle future requests"""

    MESSAGE_ID = 1


class Interested(PeerMessage):
    """Indicating the sending peer will send requests when the receiver peer is un-choked"""

    MESSAGE_ID = 2


class NotInterested(PeerMessage):
    """Indicating the sending peer will stop sending requests"""

    MESSAGE_ID = 3


# messages regarding existence of pieces


class HavePiece(PeerMessage):
    """Indicating the sending peer has a specific piece"""

    MESSAGE_ID = 4

    def __init__(self, piece_index: int):
        """
        :param piece_index: zero-based index of a piece
        """
        self.piece_index = piece_index
        if not isinstance(piece_index, int):
            raise super().Exception("piece_index must be a positive integer ({})".format(piece_index))
        super().__init__(payload=self.int_to_4bytes(piece_index))

    def __str__(self):
        return "HavePiece(piece_index={})".format(self.piece_index)

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != cls.PARAM_LENGTH:
            raise super().Exception("Invalid payload length ({}), should be {} bytes".format(
                len(payload), cls.PARAM_LENGTH))
        piece_index = int.from_bytes(payload, byteorder="big")
        return cls(piece_index=piece_index)


class PiecesBitField(PeerMessage):
    """Indicating which of all of the pieces the sending peer has, using a bitfield.
    May only be sent immediately after the handshaking sequence is completed, and before any other messages are sent,
    It is optional, and need not be sent if a client has no pieces."""

    MESSAGE_ID = 5

    def __init__(self, bitfield: bytes):
        """"
        :param bitfield: representing the pieces indices,
            where the high bit in the first byte corresponds to piece index 0.
            spare bits at the end are set to zero.
        """
        self.bitfield = bitfield
        super().__init__(payload=bitfield)

    def __str__(self):
        return "PiecesBitField(bitfield={})".format(self.bitfield)

    @classmethod
    def from_payload(cls, payload: bytes):
        return cls(bitfield=payload)


class RequestBlock(PeerMessage):
    """Request of a specific block of a piece"""

    MESSAGE_ID = 6

    def __init__(self, piece_index: int, block_begin: int, block_length: int):
        """
        :param piece_index: zero-based index of a piece
        :param block_begin: zero-based byte offset within the piece
        :param block_length: block length in bytes
        """
        self.piece_index = piece_index
        self.block_begin = block_begin
        self.block_length = block_length
        super().__init__(
            payload=self.int_to_4bytes(piece_index) + self.int_to_4bytes(block_begin) + self.int_to_4bytes(block_length)
        )

    def __str__(self):
        return "RequestBlock(piece_index={}, block_begin={}, block_length={})".format(
            self.piece_index,
            self.block_begin,
            self.block_length,
        )

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != cls.PARAM_LENGTH*3:
            raise super().Exception("Invalid payload length ({}), should be {} bytes".format(
                len(payload), cls.PARAM_LENGTH*3))
        piece_index = int.from_bytes(payload[:cls.PARAM_LENGTH], byteorder="big")
        block_begin = int.from_bytes(payload[cls.PARAM_LENGTH:cls.PARAM_LENGTH*2], byteorder="big")
        block_length = int.from_bytes(payload[cls.PARAM_LENGTH*2:cls.PARAM_LENGTH*3], byteorder="big")
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

    def __str__(self):
        return "Block(piece_index={}, block_begin={})".format(self.piece_index, self.block_begin)

    @classmethod
    def from_payload(cls, payload: bytes):
        piece_index = int.from_bytes(payload[:cls.PARAM_LENGTH], byteorder="big")
        block_begin = int.from_bytes(payload[cls.PARAM_LENGTH:cls.PARAM_LENGTH*2], byteorder="big")
        block = payload[cls.PARAM_LENGTH*2:]
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

    def __str__(self):
        return "CancelRequest(piece_index={}, block_begin={}, block_length={})".format(
            self.piece_index,
            self.block_begin,
            self.block_length,
        )

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != cls.PARAM_LENGTH*3:
            raise super().Exception("Invalid payload length ({}), should be {} bytes".format(
                len(payload), cls.PARAM_LENGTH*3))
        piece_index = int.from_bytes(payload[:cls.PARAM_LENGTH], byteorder="big")
        block_begin = int.from_bytes(payload[cls.PARAM_LENGTH:cls.PARAM_LENGTH*2], byteorder="big")
        block_length = int.from_bytes(payload[cls.PARAM_LENGTH*2:cls.PARAM_LENGTH*3], byteorder="big")
        return cls(piece_index, block_begin, block_length)


class Port(PeerMessage):
    """Sent by newer versions of the Mainline that implements a DHT tracker.
    The listen port is the port this peer's DHT node is listening on.
    This peer should be inserted in the local routing table"""

    MESSAGE_ID = 9

    def __init__(self, listen_port: int):
        self.listen_port = listen_port
        super.__init__(payload=self.int_to_4bytes(listen_port))

    def __str__(self):
        return "Port(listen_port={})".format(self.listen_port)

    @classmethod
    def from_payload(cls, payload: bytes):
        if len(payload) != cls.PARAM_LENGTH:
            raise super().Exception("Invalid payload length ({}), should be {} bytes".format(
                len(payload), cls.PARAM_LENGTH))
        listen_port = int.from_bytes(payload[:cls.PARAM_LENGTH], byteorder="big")
        return cls(listen_port)


all_messages = [
    KeepAlive, Choke, UnChoke, Interested, NotInterested,
    HavePiece, PiecesBitField, RequestBlock, Block, CancelRequest, Port
]

id_to_message = {}
for message in all_messages:
    id_to_message[message.MESSAGE_ID] = message
