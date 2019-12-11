import time
import socket
import bencode
import logging

from torf import Torrent


def recv_timeout(the_socket, timeout=2):
    the_socket.settimeout(timeout)
    total_data = []
    data = b''
    begin = time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif time.time()-begin > timeout*2:
            break
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except Exception as e:
            Peer.logger.warning(e)
    return b''.join(total_data)


class Peer:
    """Data class of BitTorrent remote peer"""

    logger = logging.getLogger('peer')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, ip_address: str, port: str):
        self.ip_address = ip_address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self):
        return "Peer({}:{})".format(self.ip_address, self.port)

    def __repr__(self):
        return {'ip_address': self.ip_address, 'port': self.port}

    def _create_message(self, length: int, message_id: int = None, payload: bytes = b'') -> bytes:
        if message_id is None:
            return length.to_bytes(4, byteorder="big") + payload
        else:
            return length.to_bytes(4, byteorder="big") + bytes([message_id]) + payload

    def _create_keep_alive(self) -> bytes:
        return self._create_message(0)

    def _create_choke(self) -> bytes:
        return self._create_message(1, 0)

    def _create_unchoke(self) -> bytes:
        return self._create_message(1, 1)

    def _create_interested(self) -> bytes:
        return self._create_message(1, 2)

    def _create_not_interested(self) -> bytes:
        return self._create_message(1, 3)

    def _create_have(self, piece_index: int) -> bytes:
        """the payload is the zero-based index of a piece that has
        just been successfully downloaded and verified via the hash"""
        return self._create_message(5, 4, piece_index.to_bytes(4, byteorder="big"))

    def _create_bitfield(self, bitfield) -> bytes:
        # TODO: complete this if needed
        return b''

    def _create_request(self, index: int, begin: int, length: int) -> bytes:
        return self._create_message(12, 6,
                                    index.to_bytes(4, byteorder="big") +
                                    begin.to_bytes(4, byteorder="big") +
                                    length.to_bytes(4, byteorder="big")
                                    )

    def _create_piece(self, index: int, begin: int, block: int) -> bytes:
        b_block = block.to_bytes(4, byteorder="big")
        return self._create_message(9+len(b_block), 7,
                                    index.to_bytes(4, byteorder="big") +
                                    begin.to_bytes(4, byteorder="big") +
                                    b_block
                                    )

    def _create_cancel(self, index: int, begin: int, length: int) -> bytes:
        return self._create_message(13, 8,
                                    index.to_bytes(4, byteorder="big") +
                                    begin.to_bytes(4, byteorder="big") +
                                    length.to_bytes(4, byteorder="big")
                                    )

    def _create_port(self, listen_port: int) -> bytes:
        return self._create_message(3, 9, listen_port.to_bytes(4, byteorder="big"))

    def handshake(self, torrent_path: str):
        import os
        import hashlib

        pstr = bytes("BitTorrent protocol", "utf-8")
        pstrlen = bytes([len(pstr)])
        reserved = b'\x00' * 8
        bcode = bencode.bread(torrent_path)
        hash_info = hashlib.sha1(bencode.bencode(bcode['info'])).digest()
        peer_id = bytes("-{}{}-{}".format('BT', '1000', str(os.getpid()).zfill(12)), "utf-8")

        message = pstrlen + pstr + reserved + hash_info + peer_id

        try:
            self.sock.connect((self.ip_address, int(self.port)))
            self.sock.send(message)
            peer_answer = self.sock.recv(1024)
        except (socket.timeout, ConnectionRefusedError) as e:
            raise Peer.Exception("Could not send message to {}: {}".format(self, e))
        if len(peer_answer) < 49:
            raise Peer.Exception("Invalid answer from {} - of length {}".format(self, len(peer_answer)))
        answer_pstrlen = peer_answer[0]
        answer_pstr = peer_answer[1:answer_pstrlen+1]
        if answer_pstr != pstr:
            raise Peer.Exception("{}'s protocol ({}) is different than ours ({})".format(self, answer_pstr, pstr))
        #answer_reserved = pstr[answer_pstrlen+1:answer_pstrlen+9]
        #self.logger.debug("answer_reserved={}".format(answer_reserved))
        answer_hash_info = peer_answer[answer_pstrlen+9:answer_pstrlen+29]
        if answer_hash_info != hash_info:
            raise Peer.Exception(
                "{}'s hash info ({}) does not match ours ({})".format(self, answer_hash_info, hash_info))
        answer_peer_id = peer_answer[answer_pstrlen+29:]
        # TODO: used only in dictionary mode where compact=0?
        #if answer_peer_id != peer_id:
        #    raise Peer.Exception(
        #        "{}'s peer id ({}) does not match ours ({})".format(self, answer_peer_id, peer_id))

    def get_single_file(self, torrent_path: str):
        torrent = Torrent.read(filepath=torrent_path)
        with open([file for file in torrent.files][0], "ab+") as out_file:
            self.logger.debug("include md5sum={}".format(torrent.include_md5))
            self.sock.send(self._create_interested())
            self.sock.send(self._create_unchoke())
            peer_answer = recv_timeout(self.sock)
            self.logger.debug("peer_answer={}".format(peer_answer))
            self.logger.debug("[:4]={}, [4]={}".format(
                int.from_bytes(peer_answer[:4], "big"),
                peer_answer[4], "big",
                ))
            block_size = 2**14
            for piece_idx in range(torrent.pieces):
                received_piece = b''
                for begin_bytes in range(0, torrent.piece_size-block_size, block_size):
                    self.sock.send(self._create_request(index=piece_idx, begin=begin_bytes, length=block_size))
                    try:
                        peer_answer = self.sock.recv(5 + block_size)
                        received_piece += peer_answer[8:]
                    except (socket.timeout, ConnectionRefusedError) as e:
                        raise Peer.Exception("Could not send request to {}: {}".format(self, e))
                if len(received_piece) != torrent.piece_size:
                    self.logger.warning("received_piece size ({}) is different than torrent's piece size ({})".format(
                        len(received_piece), torrent.piece_size
                    ))
                out_file.write(received_piece)
