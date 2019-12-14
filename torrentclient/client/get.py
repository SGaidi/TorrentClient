import os
import queue

from torrentclient.torcode.mytorrent import MyTorrent
from torrentclient.client.trackerinteract.tracker import Tracker
from torrentclient.client.trackerinteract.requestpeers import RequestPeers
from torrentclient.client.trackerinteract.handleresponse import HandleResponse
from torrentclient.client.peerinteract.handshake import PeerHandshake
from torrentclient.client.peerinteract.connection import PeerConnection
from torrentclient.client.peerinteract.getpiece import GetPiece


def add_peers(tracker_url: str, torrent: MyTorrent) -> []:
    try:
        response = RequestPeers(Tracker(tracker_url), torrent).send()
    except (Tracker.Exception, RequestPeers.Exception) as e:
        RequestPeers.logger.warning("Failed requesting peers of {} from {}: {}".format(
            torrent.name, tracker_url, e))
        return []

    hr = HandleResponse(response)
    peers = []
    try:
        peers = hr.get_peers()
    except HandleResponse.Exception as e:
        HandleResponse.logger.warning("Failed to get peers with {}: {}".format(hr, e))
    if len(peers) == 0:
        HandleResponse.logger.warning("Could not get any peers with {}".format(hr))
    return peers


def next_connected_peer(peers: queue.Queue, torrent: MyTorrent) -> PeerConnection:
    while not peers.empty():
        peer = peers.get()
        if (peer.ip_address, peer.port) in next_connected_peer.seen_peers:
            continue
        else:
            next_connected_peer.seen_peers.add((peer.ip_address, peer.port))
        hs = PeerHandshake(peer=peer, torrent=torrent)
        try:
            hs.handshake()
        except PeerHandshake.Exception as e:
            hs.logger.error("Failed to handshake {}: {}".format(peer, e))
        else:
            hs.logger.info("Connected to {}!".format(peer))
            return hs
    return None
next_connected_peer.seen_peers = set()


def get_content(torrent: str):
    torrent = MyTorrent.read(filepath=torrent)

    if torrent.trackers is not None:
        trackers = torrent.trackers
    else:
        trackers = []
    trackers.extend([tracker[:-1]] for tracker in open(os.path.join(os.getcwd(), "tests\\trackers.txt"), "r").readlines())
    trackers = trackers[:10]

    from torrentclient.client.trackerinteract.parallel import map_parallel
    peers = map_parallel(add_peers, [(tracker_url[0], torrent) for tracker_url in trackers])
    peers_queue = queue.Queue()
    for peer in peers:
        peers_queue.put(peer)
    RequestPeers.logger.debug("peers queue: {}".format(peers_queue))

    conn = next_connected_peer(peers_queue, torrent)
    for piece_hash in torrent.hashes:
        while conn is not None:
            try:
                piece = GetPiece().get()
            except GetPiece.Exception as e:
                pass

    #TODO: decide whether to pass PeerConnection around, or return it from handshake
    # (I think the second option is better)

    # handshake first peer
    # for each piece:
    #   while (there are peers):
    #     try to get it with the current peer
    #     if any failure occurred with this peer:
    #       close current connection
    #       pop another peer and handshake it
    #     else:
    #       break (inner while loop)
    # close current peer connection
    # check if have all pieces... etc


