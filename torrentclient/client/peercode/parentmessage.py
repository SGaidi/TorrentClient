import logging
from functools import lru_cache


class PeerMessage:
    """Data class of a peer message in BitTorrent protocol"""

    logger = logging.getLogger('peer-message')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, message_id: int = None, payload: bytes = b''):
        if message_id is None:
            self.message_id = b''
        else:
            self.message_id = bytes([message_id])
        self.payload = payload
        self.length = len(self.message_id + self.payload).to_bytes(4, byteorder="big")

    def __str__(self):
        return "PeerMessage(message_id={}, length={})".format(self.message_id, self.length)

    def __repr__(self):
        return {'message_id': self.message_id, 'length': self.length, 'payload': self.payload}

    @staticmethod
    def int_to_bytes(x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')

    def create_message(self) -> bytes:
        return self.length + self.message_id + self.payload
