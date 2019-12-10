from torf import Torrent

from torrentclient.client.tracker import Tracker
from torrentclient.client.requestpeers import RequestPeers
from torrentclient.client.peer import Peer
from torrentclient.client.handleresponse import HandleResponse


def get_content(torrent_path: str):
    torrent = Torrent.read(filepath=torrent_path)
    """
    print("###\n###".join(str(file) for file in torrent.files))
    print(torrent.pieces)
    print(torrent.piece_size)
    """
    return

    for tracker_url in torrent.trackers:
        try:
            tracker = Tracker(tracker_url[0])
        except Tracker.Exception as e:
            Tracker.logger.warning("Invalid Tracker url ({}): {}".format(tracker_url[0], e))
            continue

        rp = RequestPeers(tracker, torrent_path)
        try:
            response = rp.get()
        except RequestPeers.Exception as e:
            RequestPeers.logger.warning("Failed with {}: {}".format(rp, e))
            continue

        hp = HandleResponse(response)
        try:
            peers = hp.handle()
        except HandleResponse.Exception as e:
            HandleResponse.logger.warning("Failed to handle peers with {}: {}".format(hp, e))

        # TODO: start by KISS - go over each piece, try to get it from any free peer


        return
        for peer in peers:
            try:
                peer.handshake(torrent_path)
            except Peer.Exception as e:
                peer.logger.error("Failed to handshake {}: {}".format(peer, e))
