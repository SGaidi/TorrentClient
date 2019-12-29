import logging
from typing import List

from torrentclient.peerinteract.peer import Peer
from torrentclient.peercode.message import PeerMessage
from torrentclient.peercode.allmessages import KeepAlive, Choke, UnChoke, Interested, \
    NotInterested, RequestBlock, Block, CancelRequest, Port, id_to_message


class PeerConnection:
    """Class for a Peer wire protocol TCP connection"""

    LENGTH_BYTES = 4
    MESSAGE_ID_BYTES = 1

    BUFFER_SIZE = 1024

    logger = logging.getLogger('peer-connection')

    keepalive_message = KeepAlive().create()

    class Exception(Exception):
        """An exception with connection to peer occurred"""

    def __init__(self, peer: Peer, socket):
        """
        :param peer: Peer connected to
        :param socket: connected socket after a handshake
        """
        self.peer = peer
        self.socket = socket
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

    def __str__(self):
        return "PeerConnection(peer={})".format(self.peer)

    def _recv(self, buffer_size: int) -> bytes:
        self.socket.send(self.keepalive_message)
        try:
            return self.socket.recv(buffer_size)
        except Exception as e:
            self.socket.close()
            raise PeerConnection.Exception("Failed to read from socket: {}".format(e))

    def _read_missing_bytes(self, missing_count: int):
        """tries reading `missing_count` bytes from socket"""
        missing_bytes = b''
        while len(missing_bytes) < missing_count:
            recv_bytes = self._recv(missing_count)
            self.logger.debug("Received {} Block bytes".format(len(recv_bytes)))
            if recv_bytes == b'':
                raise PeerConnection.Exception("Expected {} more bytes and did not receive them".format(
                    missing_count))
            missing_bytes += recv_bytes
        self.response += missing_bytes

    def _handle_response_length(self):
        """validates length, updates idx, and receives any missing bytes"""
        if self.idx + self.LENGTH_BYTES > len(self.response):
            raise PeerMessage.Exception("Corrupt response: {}".format(self.response))
        self.length = int.from_bytes(self.response[self.idx:self.idx + self.LENGTH_BYTES], byteorder="big")
        self.idx += self.LENGTH_BYTES
        if self.length + self.idx > len(self.response):
            self.logger.debug("Message length ({}) is higher than current length in buffer ({})".format(
                self.length, len(self.response) - self.idx
            ))
            self._read_missing_bytes(self.length + self.idx - len(self.response))

    def _determine_message_type(self):
        """messages factory-like method"""
        if self.length == 0:
            self.message = KeepAlive()
        else:
            # Messages that at least have an ID
            id = self.response[self.idx]
            payload = self.response[self.idx+self.MESSAGE_ID_BYTES:self.idx + self.length]
            message_cls = id_to_message[id]
            self.logger.debug("'{}' message".format(message_cls.__name__))
            if message_cls in [Choke, UnChoke, Interested, NotInterested]:
                # All messages with id only and no payload
                if self.length != self.MESSAGE_ID_BYTES:
                    raise PeerMessage.Exception("{} messages should be of length 1 ({})".format(
                        type(message_cls).__name__, self.length
                    ))
                self.message = message_cls()
            else:
                self.message = message_cls.from_payload(payload)

    def _parse_response(self) -> List[PeerMessage]:
        """returns list of messages objects
        tries reading whole messages, but not everything from socket"""
        self.response = self._recv(self.BUFFER_SIZE)
        self.logger.debug("Parsing response")
        messages = []
        self.idx = 0
        while self.idx < len(self.response):
            try:
                self._handle_response_length()
                self._determine_message_type()
            except (PeerMessage.Exception, KeyError) as e:
                self.logger.error("Failed to parse messages, dropping all read messages from buffer: {}".format(e))
                return messages
            messages.append(self.message)
            self.idx += self.length
        return messages

    def _handle_messages(self, messages: list) -> List[Block]:
        """changes state machine according to received messages
        and appends any Block messages to be handled by GetPiece class"""
        block_messages = []
        for message in messages:
            self.logger.info("Handling {} message".format(message))
            if isinstance(message, (KeepAlive, RequestBlock, CancelRequest, Port)):
                self.logger.debug("Ignoring message of type {} - not supported".format(type(message).__name__))
            elif isinstance(message, Choke):
                self.peer_choking = True
            elif isinstance(message, UnChoke):
                self.peer_choking = False
            elif isinstance(message, Interested):
                self.peer_interested = True
            elif isinstance(message, NotInterested):
                self.peer_interested = False
            elif isinstance(message, Block):
                block_messages.append(message)
        return block_messages

    def expect_blocks(self) -> List[Block]:
        """returns a list of any received blocks"""
        messages = self._parse_response()
        return self._handle_messages(messages)

    def _wait_peer_unchoked(self):
        """waits till peer can handle new requests"""
        for retry_count in range(6):
            self.logger.info("Waiting for {} to send UnChoke message".format(self.peer))
            self.expect_blocks()
            if not self.peer_choking:
                return
        raise PeerConnection.Exception("Timeout of UnChoke message")

    def _send_peer_interested(self):
        """notifies peer it will start sending requests"""
        self.logger.info("Sending Interested message to {}".format(self.peer))
        self.socket.send(Interested().create())
        self.am_interested = True

    def send(self, message: bytes):
        """wrapper of socket.send, applying BitTorrent specifications with `choking` and `interested` values"""
        self.socket.send(self.keepalive_message)
        if not self.am_interested:
            self._send_peer_interested()
        if self.peer_choking:
            self._wait_peer_unchoked()
        try:
            self.socket.send(message)
        except Exception as e:
            self.socket.close()
            raise PeerConnection.Exception("Failed to send message to socket: {}".format(e))
