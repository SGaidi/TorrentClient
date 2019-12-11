import socket
import bencode
import logging

from torrentclient.client.peerinteract.peer import Peer


class PeerHandshake:
    """Class for establishing a connection with a Peer"""

    PSTR = bytes("BitTorrent protocol", "utf-8")
    PSTR_LEN = bytes([len(PSTR)])
    RESERVED = b'\x00' * 8

    RESPONSE_BUFFER_SIZE = 1024

    PSTR_LEN_BYTE = 0
    PSTR_BYTE = 1

    logger = logging.getLogger('peer-handshake')

    class Exception(Exception):
        """An exception with peer handshake"""

    def __init__(self, remote_peer: Peer, torrent_path: str):
        self.remote_peer = remote_peer
        self.torrent_path = torrent_path
        # TODO: use `with socket...` in handshake method
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self):
        return "PeerHandshake(remote_peer={}, torrent_path={})".format(self.remote_peer, self.torrent_path)

    def __repr__(self):
        return {'remote_peer': self.remote_peer, 'torrent_path': self.torrent_path, 'socket': self.socket}

    def _create_message(self):
        import hashlib
        torrent_bcode = bencode.bread(self.torrent_path)
        self.info_hash = hashlib.sha1(bencode.bencode(torrent_bcode['info'])).digest()
        self.request = self.PSTR_LEN + self.PSTR + self.RESERVED + self.info_hash + Peer.LOCAL_PEER_ID

    def _send_message(self):
        try:
            self.socket.connect((self.remote_peer.ip_address, int(self.remote_peer.port)))
            self.socket.send(self.request)
        except (socket.timeout, ConnectionRefusedError) as e:
            raise PeerHandshake.Exception("Could not send message to {}: {}".format(self.remote_peer, e))

    @property
    def RESERVED_BYTE(self) -> int:
        return self.PSTR_BYTE + self.response_pstrlen

    @property
    def INFO_HASH_BYTE(self) -> int:
        return self.RESERVED_BYTE + len(self.RESERVED)

    @property
    def PEER_ID_BYTE(self) -> int:
        return self.INFO_HASH_BYTE + len(self.info_hash)

    def _validate_response(self):
        self.peer_response = self.socket.recv(self.RESPONSE_BUFFER_SIZE)
        if len(self.peer_response) < len(self.request):
            raise PeerHandshake.Exception("Invalid response length from {}: {}".format(
                self.remote_peer, len(self.peer_response)))
        self.response_pstrlen = self.peer_response[self.PSTR_LEN_BYTE]
        self.response_pstr = self.peer_response[self.PSTR_BYTE:self.RESERVED_BYTE]
        if self.response_pstr != self.PSTR:
            raise PeerHandshake.Exception("{}'s protocol ({}) is different than ours ({})".format(
                self.remote_peer, self.response_pstr, self.PSTR))
        self.response_reserved = self.peer_response[self.RESERVED_BYTE:self.INFO_HASH_BYTE]
        if self.response_reserved != self.RESERVED:
            self.logger.warning("{} used reserved bytes which are not supported: {}".format(
                self.remote_peer, self.response_reserved))
        self.response_info_hash = self.peer_response[self.INFO_HASH_BYTE:self.PEER_ID_BYTE]
        if self.response_info_hash != self.info_hash:
            raise Peer.Exception(
                "{}'s hash info ({}) does not match ours ({})".format(
                    self.remote_peer, self.response_info_hash, self.info_hash))
        self.remote_peer.peer_id = self.peer_response[self.PEER_ID_BYTE:]
        if self.PEER_ID_BYTE + 20 == len(self.peer_response):
            raise PeerHandshake.Exception("Invalid peer_id length ({}) from {}".format(
                len(self.peer_response) - self.PEER_ID_BYTE - 20,
                self.remote_peer,
            ))
        # TODO: used only in dictionary mode where compact=0?
        # if self.remote_peer.peer_id != peer_id:
        #    raise PeerHandshake.Exception(
        #        "{}'s peer id ({}) does not match ours ({})".format(self.remote_peer, response_peer_id, peer_id))

    def handshake(self):
        try:
            self._create_message()
            self._send_message()
            self._validate_response()
        except Exception as e:
            self.socket.close()
            raise e
