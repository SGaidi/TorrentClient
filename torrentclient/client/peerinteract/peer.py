import os
import socket
import logging

from torf import Torrent


class Peer:
    """Data class of BitTorrent remote peer"""

    LOCAL_PEER_ID = bytes("-{}{}-{}".format('BT', '1000', str(os.getpid()).zfill(12)), "utf-8")

    logger = logging.getLogger('peer')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, ip_address: str, port: str):
        self.ip_address = ip_address
        self.port = port
        self.peer_id = None

    def __str__(self):
        return "Peer({}:{})".format(self.ip_address, self.port)

    def __repr__(self):
        return {'ip_address': self.ip_address, 'port': self.port}

    def get_single_file(self, torrent_path: str):
        from torrentclient.client.peercode.allmessages import Interested, UnChoke, RequestBlock
        interested_message = Interested().create_message()
        unchoke_message = UnChoke().create_message()
        torrent = Torrent.read(filepath=torrent_path)
        with open([file for file in torrent.files][0], "ab+") as out_file:
            self.logger.debug("include md5sum={}".format(torrent.include_md5))
            self.sock.send(interested_message)
            self.sock.send(unchoke_message)
            peer_response = recv_timeout(self.sock)
            self.logger.debug("peer_response={}".format(peer_response))
            self.logger.debug("[:4]={}, [4]={}".format(
                int.from_bytes(peer_response[:4], "big"),
                peer_response[4], "big",
                ))
            block_length = 2**14
            for piece_idx in range(torrent.pieces):

                received_piece = b''
                for begin_bytes in range(0, torrent.piece_size-block_length, block_length):
                    request_message = RequestBlock(
                        piece_index=piece_idx, block_begin=begin_bytes, block_length=block_length
                    ).create_message()
                    self.sock.send(request_message)
                    try:
                        peer_response = self.sock.recv(5 + block_length)
                        received_piece += peer_response[8:]
                    except (socket.timeout, ConnectionRefusedError) as e:
                        raise Peer.Exception("Could not send request to {}: {}".format(self, e))
                if len(received_piece) != torrent.piece_size:
                    self.logger.warning("received_piece size ({}) is different than torrent's piece size ({})".format(
                        len(received_piece), torrent.piece_size
                    ))
                out_file.write(received_piece)
