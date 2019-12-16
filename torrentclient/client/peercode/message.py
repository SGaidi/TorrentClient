import logging
from functools import lru_cache


class PeerMessage:
    """Data class of a peer message in BitTorrent protocol"""

    logger = logging.getLogger('peer-message')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, payload: bytes = b''):
        if self.MESSAGE_ID is None:
            self.message_id = b''
        else:
            self.message_id = bytes([self.MESSAGE_ID])  # 1 byte
        self.payload = payload
        self.length = len(self.message_id + self.payload).to_bytes(4, byteorder="big")  # 4 bytes

    def __str__(self):
        return "PeerMessage(message_id={}, length={})".format(self.message_id, self.length)

    @property
    def MESSAGE_ID(self) -> int:
        raise NotImplementedError("MESSAGE_ID must be specified in child class ({}) of ParentMessage".format(
            self.__class__.__str__()
        ))

    @staticmethod
    def int_to_4bytes(x: int) -> bytes:
        return x.to_bytes(length=4, byteorder="big", signed=False)

    def create(self) -> bytes:
        return self.length + self.message_id + self.payload
