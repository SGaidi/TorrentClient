import socket
import logging
import traceback
from typing import List

from torrentclient.client.peerinteract.peer import Peer
from torrentclient.client.peercode.message import PeerMessage
from torrentclient.client.peercode.allmessages import KeepAlive, Choke, UnChoke, Interested, \
    NotInterested, RequestBlock, Block, CancelRequest, Port, id_to_message


class PeerConnection:
    """Class for a Peer wire protocol TCP connection"""

    LENGTH_BYTES = 4
    MESSAGE_ID_BYTES = 1

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
        self.socket.settimeout(15)
        try:
            return self.socket.recv(buffer_size)
        except Exception as e:
            self.socket.settimeout(socket.getdefaulttimeout())
            self.socket.close()
            raise PeerConnection.Exception("{} Failed to read from socket: {}".format(self, e))

    def _read_missing_bytes(self, missing_count: int):
        """tries reading `missing_count` bytes from socket"""
        missing_bytes = b''
        while len(missing_bytes) < missing_count:
            recv_bytes = self._recv(missing_count)
            if recv_bytes == b'':
                raise PeerConnection.Exception("Expected {} more bytes from {} and did not receive them".format(
                    missing_count, self.peer))
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
            self.response += self._read_missing_bytes(self.length + self.idx - len(self.response))

    def _determine_message_type(self):
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
                        message_cls, self.length
                    ))
                self.message = message_cls()
            else:
                self.message = message_cls.from_payload(payload)

    def _parse_response(self) -> List[PeerMessage]:
        """factory-like method - returns list of messages objects
        tries reading whole messages, but not everything in buffer"""
        self.response = self._recv(4096)
        self.logger.debug("Parsing response: {}".format(self.response))
        messages = []
        self.idx = self.LENGTH_BYTES
        while self.idx < len(self.response):
            try:
                self._handle_response_length()
                self._determine_message_type()
            except (PeerMessage.Exception, KeyError) as e:
                self.logger.error("Failed to parse messages, dropping all read messages from buffer: {}".format(e))
                traceback.print_exc()
                return messages
            messages.append(self.message)
            self.idx += self.length
        return messages

    def _handle_messages(self, messages: list) -> List[Block]:
        """change state machine according to received messages, and append any Block messages"""
        block_messages = []
        for message in messages:
            self.logger.info("Handling {} message".format(message))
            if isinstance(message, (KeepAlive, RequestBlock, CancelRequest, Port)):
                self.logger.warning("Ignoring message of type {} - not supported".format(type(message).__name__))
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

    def expect_blocks(self) -> list:
        messages = self._parse_response()
        return self._handle_messages(messages)

    def _wait_peer_unchoked(self):
        for retry_count in range(3):
            self.logger.info("Waiting for {} to send UnChoke message".format(self.peer))
            block_messages = self.expect_blocks()
            assert len(block_messages) == 0, "_wait_peer_unchoked should be called before sending any requests"
            if not self.peer_choking:
                return
        raise PeerConnection.Exception("Timeout of UnChoke message")

    def _send_peer_interested(self):
        self.logger.info("Sending Interested message to {}".format(self.peer))
        self.socket.send(Interested().create())
        self.am_interested = True

    def send(self, message: bytes):
        """wrapper of socket.send, applying BitTorrent specifications with `choking` and `interested` values"""
        self.socket.send(PeerConnection.keepalive_message)
        if not self.am_interested:
            self._send_peer_interested()
        if self.peer_choking:
            self._wait_peer_unchoked()
        try:
            self.socket.send(message)
        except Exception as e:
            self.socket.close()
            raise PeerConnection.Exception("{} Failed to send message to socket: {}".format(self, e))

