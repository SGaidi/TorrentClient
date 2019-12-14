from torrentclient.client.peerinteract.connection import PeerConnection
from torrentclient.torcode.mytorrent import MyTorrent


class GetPiece:

    def __init__(self, peer_connection: PeerConnection, torrent: MyTorrent, piece_idx: int):
        self.peer_connection = peer_connection
        self.torrent = torrent
        self.piece_idx = piece_idx

    def get(self) -> bytes:

        # TODO: calculate actual index with piece_idx
        for sub_piece_hash in self.torrent.hashes:
            self.peer_connection.send(self.request)
