import logging


class PeerMessage:
    """Data class of a peer message in BitTorrent protocol"""

    PARAM_LENGTH = 4

    logger = logging.getLogger('peer-message')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    @staticmethod
    def int_to_4bytes(param: int) -> bytes:
        return param.to_bytes(length=PeerMessage.PARAM_LENGTH, byteorder="big", signed=False)

    def __init__(self, payload: bytes = b''):
        """
        :param payload: message content in bytes
        """
        if self.MESSAGE_ID is None:
            self.message_id = b''
        else:
            self.message_id = bytes([self.MESSAGE_ID])  # 1 byte
        self.payload = payload
        self.length = self.int_to_4bytes(len(self.message_id + self.payload))

    def __str__(self):
        """used for debug logging"""
        return "{}(MESSAGE_ID={}, length={})".format(
            self.__class__.__name__,
            self.MESSAGE_ID,
            len(self.message_id + self.payload),
        )

    @property
    def MESSAGE_ID(self) -> int:
        raise NotImplementedError("MESSAGE_ID must be specified in child class ({}) of ParentMessage".format(
            self.__class__.__name__
        ))

    def create(self) -> bytes:
        """returns the entire encoded message in bytes"""
        return self.length + self.message_id + self.payload
