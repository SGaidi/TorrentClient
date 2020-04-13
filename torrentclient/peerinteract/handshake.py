import socket
import logging

from torrentclient.mytorrent import MyTorrent
from torrentclient.peerinteract.peer import Peer
from torrentclient.peerinteract.connections import PeerConnection


socket.setdefaulttimeout(30)


class PeerHandshake:
    """Class for establishing a connection with a remote Peer"""

    PSTR = bytes("BitTorrent protocol", "utf-8")
    PSTR_LEN = bytes([len(PSTR)])
    RESERVED = b'\x00' * 8

    PSTR_LEN_BYTE = 0
    PSTR_BYTE = 1

    logger = logging.getLogger('peer-handshake')

    class Exception(Exception):
        """An exception with peer handshake"""

    def __init__(self, peer: Peer, torrent: MyTorrent):
        self.peer = peer
        self.torrent = torrent

    def __str__(self):
        return "PeerHandshake(peer={}, torrent={})".format(self.peer, self.torrent)

    def _create_message(self):
        self.request = self.PSTR_LEN + self.PSTR + self.RESERVED + self.torrent.infohash + Peer.LOCAL_PEER_ID

    def _send_message(self):
        self.logger.debug("Trying to send initial handshake to {}".format(self.peer))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.peer.ip_address, self.peer.port))
        except Exception as e:
            raise PeerHandshake.Exception("Could not connect to {}: {}".format(self.peer, e))
        try:
            self.socket.send(self.request)
        except Exception as e:
            self.socket.close()
            raise PeerHandshake.Exception("Could not send message to {}: {}".format(self.peer, e))

    @property
    def RESERVED_BYTE(self) -> int:
        return self.PSTR_BYTE + self.response_pstrlen

    @property
    def INFO_HASH_BYTE(self) -> int:
        return self.RESERVED_BYTE + len(self.RESERVED)

    @property
    def PEER_ID_BYTE(self) -> int:
        return self.INFO_HASH_BYTE + len(self.torrent.infohash)

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
        if self.response_info_hash != self.torrent.infohash:
            raise Peer.Exception(
                "{}'s info hash ({}) does not match ours ({})".format(
                    self.peer, self.response_info_hash, self.torrent.infohash))

    def _validate_peer_id(self):
        self.peer.peer_id = self.peer_response[self.PEER_ID_BYTE:]
        if len(self.peer.peer_id) != 20:
            self.logger.warning("peer_id ({}) length {}".format(self.peer.peer_id, len(self.peer.peer_id)))

    def _validate_response(self):
        """raises an exception if the received handshake is not as expected"""
        self.logger.debug("Validating response handshake")
        self.peer_response = self.socket.recv(len(self.request))
        self._validate_length()
        self._validate_protocol()
        self._validate_reserved()
        self._validate_info_hash()
        self._validate_peer_id()

    def handshake(self) -> PeerConnection:
        """returns PeerConnection if handshake was successful"""
        try:
            self._create_message()
            self._send_message()
            self._validate_response()
        except Exception as e:
            self.socket.close()
            raise PeerHandshake.Exception(e)
        else:
            return PeerConnection(peer=self.peer, socket=self.socket)
