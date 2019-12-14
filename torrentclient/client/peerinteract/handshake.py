import socket
import logging

from torrentclient.torcode.mytorrent import MyTorrent
from torrentclient.client.peerinteract.peer import Peer


class PeerHandshake:
    """Class for establishing a connection with a remote Peer"""

    PSTR = bytes("BitTorrent protocol", "utf-8")
    PSTR_LEN = bytes([len(PSTR)])
    RESERVED = b'\x00' * 8

    RESPONSE_BUFFER_SIZE = 1024

    PSTR_LEN_BYTE = 0
    PSTR_BYTE = 1

    logger = logging.getLogger('peer-handshake')

    class Exception(Exception):
        """An exception with peer handshake"""

    def __init__(self, peer: Peer, torrent: MyTorrent):
        self.peer = peer
        self.torrent = torrent
        # TODO: use `with socket...` in handshake method
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self):
        return "PeerHandshake(peer={}, torrent={})".format(self.peer, self.torrent)

    def _create_message(self):
        self.request = self.PSTR_LEN + self.PSTR + self.RESERVED + self.torrent.infohash + Peer.LOCAL_PEER_ID

    def _send_message(self):
        self.logger.debug("Sending message")
        self.socket.settimeout(5)
        try:
            self.socket.send(self.request)
        except (socket.timeout, ConnectionRefusedError) as e:
            raise PeerHandshake.Exception("Could not send message to {}: {}".format(self.peer, e))

    @property
    def RESERVED_BYTE(self) -> int:
        return self.PSTR_BYTE + self.response_pstrlen

    @property
    def INFO_HASH_BYTE(self) -> int:
        return self.RESERVED_BYTE + len(self.RESERVED)

    @property
    def PEER_ID_BYTE(self) -> int:
        return self.INFO_HASH_BYTE + len(self.info_hash)

    def _validate_length(self):
        if len(self.peer_response) < len(self.request):
            raise PeerHandshake.Exception("Invalid response length from {}: {}".format(
                self.peer, len(self.peer_response)))

    def _validate_protocol(self):
        self.response_pstrlen = self.peer_response[self.PSTR_LEN_BYTE]
        self.response_pstr = self.peer_response[self.PSTR_BYTE:self.RESERVED_BYTE]
        if self.response_pstr != self.PSTR:
            raise PeerHandshake.Exception("{}'s protocol ({}) is different than ours ({})".format(
                self.peer, self.response_pstr, self.PSTR))

    def _validate_reserved(self):
        self.response_reserved = self.peer_response[self.RESERVED_BYTE:self.INFO_HASH_BYTE]
        if self.response_reserved != self.RESERVED:
            self.logger.warning("{} used reserved bytes which are not supported: {}".format(
                self.peer, self.response_reserved))

    def _validate_info_hash(self):
        self.response_info_hash = self.peer_response[self.INFO_HASH_BYTE:self.PEER_ID_BYTE]
        if self.response_info_hash != self.info_hash:
            raise Peer.Exception(
                "{}'s hash info ({}) does not match ours ({})".format(
                    self.peer, self.response_info_hash, self.info_hash))

    def _validate_peer_id(self):
        self.peer.peer_id = self.peer_response[self.PEER_ID_BYTE:]
        if self.PEER_ID_BYTE + 20 == len(self.peer_response):
            raise PeerHandshake.Exception("Invalid peer_id length ({}) from {}".format(
                len(self.peer_response) - self.PEER_ID_BYTE - 20,
                self.peer,
            ))
        # TODO: used only in dictionary mode where compact=0?
        # if self.peer.peer_id != peer_id:
        #    raise PeerHandshake.Exception(
        #        "{}'s peer id ({}) does not match ours ({})".format(self.peer, response_peer_id, peer_id))

    def _validate_response(self):
        """raises an exception if the received handshake is not as expected"""
        self.logger.debug("Receiving and validating response")
        self.peer_response = self.socket.recv(self.RESPONSE_BUFFER_SIZE)
        self._validate_length()
        self._validate_protocol()
        self._validate_reserved()
        self._validate_info_hash()
        self._validate_peer_id()

    def handshake(self) -> socket.socket:
        """returns socket of established connection to remote peer"""
        try:
            self._create_message()
            self._send_message()
            self._validate_response()
        except Exception as e:
            self.socket.close()
            raise e
        else:
            return self.socket
