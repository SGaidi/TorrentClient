import logging


class Peer:
    """Data class of BitTorrent remote peer"""

    logger = logging.getLogger('peer')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, ip_address: str, port: str):
        self.ip_address = ip_address
        self.port = port

    def __str__(self):
        return "Peer({}:{})".format(self.ip_address, self.port)

    def __repr__(self):
        return {'ip_address': self.ip_address, 'port': self.port}

    def handshake(self, torrent_path: str):
        import os
        import socket
        import bencode
        import hashlib

        pstr = "BitTorrent protocol"
        pstrlen = str(len(pstr))
        reserved = "0" * 8
        bcode = bencode.bread(torrent_path)
        hash_info = str(hashlib.sha1(bencode.bencode(bcode['info'])).digest())
        peer_id = "-{}{}{}-".format('BT', '1000', str(os.getpid()).zfill(12))

        message = pstrlen + pstr + reserved + hash_info + peer_id

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.ip_address, int(self.port)))
            except Exception as e:
                raise RuntimeError("Unexpected exception when connecting to {}: {}".format(self, e))
            try:
                sock.send(message)
            except Exception as e:
                raise RuntimeError("Unexpected exception when sending message to {}: {}".format(self, e))
            try:
                sock.recv()
            except Exception as e:
                raise RuntimeError("Unexpected exception when receiving message to {}: {}".format(self, e))