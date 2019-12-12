from torf import Torrent

from torrentclient.client.trackerinteract.tracker import Tracker
from torrentclient.client.trackerinteract.requestpeers import RequestPeers
from torrentclient.client.trackerinteract.responsepeers import ResponsePeers
from torrentclient.client.peerinteract.handshake import PeerHandshake


def get_content(torrent_path: str):
    torrent = Torrent.read(filepath=torrent_path)

    for tracker_url in torrent.trackers:
        try:
            tracker = Tracker(tracker_url[0])
        except Tracker.Exception as e:
            Tracker.logger.warning("Invalid Tracker url ({}): {}".format(tracker_url[0], e))
            continue

        # TODO: make it a torrent method / make tracker_url an argument to RequestPeers
        rp = RequestPeers(tracker, torrent_path)
        try:
            response = rp.get()
        except RequestPeers.Exception as e:
            RequestPeers.logger.warning("Failed with {}: {}".format(rp, e))
            continue

        hp = ResponsePeers(response)
        try:
            peers = hp.handle()
        except ResponsePeers.Exception as e:
            ResponsePeers.logger.warning("Failed to handle peers with {}: {}".format(hp, e))

        # TODO: start by KISS - go over each piece, try to get it from any free peer

        for peer in peers:
            hs = PeerHandshake(peer=peer, torrent_path=torrent_path)
            try:
                hs.handshake()
            except PeerHandshake.Exception as e:
                hs.logger.error("Failed to handshake {}: {}".format(peer, e))
            else:
                peer.get_single_file(torrent_path)
                return
