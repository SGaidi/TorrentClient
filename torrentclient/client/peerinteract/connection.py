import socket
import logging
from typing import List

from torrentclient.client.peerinteract.peer import Peer
from torrentclient.client.peercode.message import PeerMessage
from torrentclient.client.peercode.allmessages import KeepAlive, Choke, UnChoke, Interested, \
    NotInterested, HavePiece, PiecesBitField, RequestBlock, Block, CancelRequest, Port, id_to_message


class PeerConnection:
    """Class for a Peer wire protocol TCP connection"""

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

    def recv_all(self) -> bytes:
        """wrapper of socket.recv, reads everything from buffer until timeout"""
        self.socket.settimeout(15)
        response = b''
        last_response = b''
        while True:
            try:
                last_response = self.socket.recv(1024)
            except socket.timeout:
                response += last_response
                break
            else:
                if last_response == b'':
                    break
                else:
                    self.socket.send(PeerConnection.keepalive_message)
                    response += last_response
        self.socket.settimeout(socket.getdefaulttimeout())
        return response

    def parse_response(self, response: bytes) -> List[PeerMessage]:
        """returns list of messages objects
        factory-like method"""
        self.logger.debug("Parsing response: {}".format(response))
        messages = []
        idx = 0
        while idx < len(response):
            try:
                if idx + 4 >= len(response):
                    raise PeerMessage.Exception("Partial or corrupted response: {}".format(response))
                length = int.from_bytes(response[idx:idx+4], byteorder="big")
                if length + idx + 4 > len(response):
                    self.logger.warning("Invalid length ({}), should not be higher than ({})".format(
                        length, len(response) - idx - 4
                    ))
                if length == 0:
                    message = KeepAlive()
                else:
                    # messages that at least have an ID
                    id = response[idx+4]
                    payload = response[idx+5:idx+4+length]
                    message_cls = id_to_message[id]
                    self.logger.debug("'{}' message".format(message_cls.__name__))
                    if message_cls in [Choke, UnChoke, Interested, NotInterested]:
                        # All messages with id only and no payload
                        assert length == 1
                        assert payload == b''
                        message = message_cls()
                    else:
                        message = message_cls.from_payload(payload)
            except (PeerMessage.Exception, KeyError) as e:
                self.logger.error("Failed to parse messages, dropping all read messages from buffer: {}".format(e))
                return messages
            messages.append(message)
            idx += 4 + length
        return messages

    def handle_messages(self, messages: list) -> List[Block]:
        """change state machine according to received messages, and append any Block messages"""
        block_messages = []
        for message in messages:
            self.logger.info("Handling `{}` message".format(type(message).__name__))
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
            elif isinstance(message, (HavePiece, PiecesBitField)):
                self.logger.info("Peer has sub-piece #{}".format(message.piece_index))
            elif isinstance(message, Block):
                block_messages.append(message)
        return block_messages

    def expect_blocks(self) -> list:
        response = self.recv_all()
        messages = self.parse_response(response)
        return self.handle_messages(messages)

    def _wait_peer_unchoked(self):
        for retry_count in range(3):
            self.logger.info("Waiting for {} to send UnChoke message".format(self.peer))
            block_messages = self.expect_blocks()
            assert len(block_messages) == 0, "_wait_peer_unchoked should be called before sending any requests"
            if not self.peer_choking:
                return
        raise PeerConnection.Exception("Timeout of UnChoke message")

    def _send_peer_unchoked(self):
        self.logger.info("Sending UnChoke message to {}".format(self.peer))
        self.socket.send(UnChoke().create())
        self.am_choking = False

    def _send_peer_interested(self):
        self.logger.info("Sending Interested message to {}".format(self.peer))
        self.socket.send(Interested().create())
        self.am_interested = True

    def send(self, message: bytes):
        """wrapper of socket.send, applying BitTorrent specifications with `choking` and `interested` values"""
        self.socket.send(PeerConnection.keepalive_message)
        if self.am_choking:
            self._send_peer_unchoked()
        if not self.am_interested:
            self._send_peer_interested()
        if self.peer_choking:
            self._wait_peer_unchoked()
        self.socket.send(message)


