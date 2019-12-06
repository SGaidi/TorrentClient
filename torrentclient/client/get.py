from torf import Torrent

from torrentclient.client.tracker import Tracker
from torrentclient.client.requestpeers import RequestPeers


def get_content(torrent_path: str):
    torrent = Torrent.read(filepath=torrent_path)

    for tracker_url in torrent.trackers:
        try:
            tracker = Tracker(tracker_url[0])
        except Tracker.Exception as e:
            Tracker.logger.warning("Invalid Tracker url ({}): {}".format(tracker_url[0], e))
            continue

        rp = RequestPeers(tracker, torrent_path)
        try:
            peers = rp.get()
        except RequestPeers.Exception as e:
            RequestPeers.logger.warning("{} failed to get peers: {}".format(rp, e))
            continue
