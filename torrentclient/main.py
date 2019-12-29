import os
import logging
import argparse
from typing import List
from multiprocessing import Queue, Process

from torrentclient.trackerinteract.parallel import map_parallel
from torrentclient.mytorrent import MyTorrent
from torrentclient.peerinteract.connection import PeerConnection
from torrentclient.peerinteract.getpiece import GetPiece


QUEUE_STOP_FLAG = None


PARALLEL_TRACKERS_COUNT = 40
"""number of parallel processes establishing a connection with a tracker"""


def add_peers(tracker_url: str, torrent: MyTorrent) -> List:
    from torrentclient.trackerinteract.tracker import Tracker
    from torrentclient.trackerinteract.requestpeers import RequestPeers
    from torrentclient.trackerinteract.handleresponse import HandleResponse

    try:
        response = RequestPeers(Tracker(tracker_url), torrent).send()
    except (Tracker.Exception, RequestPeers.Exception) as e:
        RequestPeers.logger.warning("Failed requesting peers of '{}' from {}: {}".format(
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


def peers_from_trackers(torrent: MyTorrent):
    if torrent.trackers is not None:
        trackers = torrent.trackers
    else:
        trackers = []
    trackers.extend(
        [tracker[:-1]] for tracker in open(os.path.join(os.getcwd(), "tests\\trackers.txt"), "r").readlines())
    map_args = [(tracker_url[0], torrent) for tracker_url in trackers]
    peers = map_parallel(add_peers, map_args, PARALLEL_TRACKERS_COUNT)
    return set(peers)


def next_connected_peer(peers: Queue, torrent: MyTorrent) -> PeerConnection:
    from torrentclient.peerinteract.handshake import PeerHandshake
    while not peers.empty():
        peer = peers.get()
        # TODO: use priority queue
        #  so that recently connected/working peers will be tried again earlier than other peers
        #  but also do not put peers until finished using them
        peers.put(peer)  # move it back to end of queue
        hs = PeerHandshake(peer=peer, torrent=torrent)
        try:
            connection = hs.handshake()
        except PeerHandshake.Exception as e:
            hs.logger.error(e)
        else:
            hs.logger.info("Connected to {}!".format(peer))
            return connection
    print("No peers left!")


def write_piece(pieces_queue: Queue, peers_queue: Queue, torrent: MyTorrent):
    piece_idx = pieces_queue.get()
    connection = next_connected_peer(peers_queue, torrent)
    while connection is not None and piece_idx is not QUEUE_STOP_FLAG:
        GetPiece.logger.debug("Process {}:{} {}".format(connection.peer, piece_idx, os.getpid()))
        try:
            piece = GetPiece(peer_connection=connection, torrent=torrent, piece_idx=piece_idx).get()
        except Exception as e: #(GetPiece.Exception, PeerConnection.Exception) as e:
            GetPiece.logger.error("Failed to get piece #{} with {}: {}".format(piece_idx, connection, e))
            connection.socket.close()
            connection = next_connected_peer(peers_queue, torrent)
        else:
            GetPiece.logger.info("Successfully obtained piece #{} with {}".format(piece_idx, connection))
            with open(torrent.out_filename, "wb+") as out:
                out.seek(piece_idx*torrent.my_piece_size)
                out.write(piece)
            piece_idx = pieces_queue.get()
    if connection is not None:
        connection.socket.close()


def feed_pieces_queue(pieces_queue: Queue, pieces_count: int, parallel_peers_count: int):
    for idx in range(pieces_count):
        pieces_queue.put(idx)
    for p_count in range(parallel_peers_count):
        pieces_queue.put(QUEUE_STOP_FLAG)
    GetPiece.logger.debug("Done feeding queue: {}".format(pieces_queue.qsize()))


def update_progress(pieces_queue: Queue, total_pieces: int, parallel_peers_count: int):
    import time
    while not pieces_queue.empty():
        with open("progress.txt", "w+") as out:
            # TODO: create bitarray with semaphore to update pieces status
            out.write("{}/{} downloaded".format(total_pieces-pieces_queue.qsize()-parallel_peers_count, total_pieces))
        time.sleep(1)


def get_content(torrent_path: str):
    torrent = MyTorrent.read(filepath=torrent_path)

    peers_queue = Queue()
    for peer in peers_from_trackers(torrent):
        peers_queue.put(peer)

    GetPiece.logger.info("Trying to get {} pieces".format(torrent.piece_count))
    pieces_queue = Queue()
    processes = []
    parallel_peers_count = peers_queue.qsize() // 5
    GetPiece.logger.info("parallel_peers_count={}".format(parallel_peers_count))
    for _ in range(parallel_peers_count):
        peer_process = Process(target=write_piece, args=(pieces_queue, peers_queue, torrent))
        peer_process.daemon = True
        processes.append(peer_process)
    progress_process = Process(target=update_progress, args=(pieces_queue, torrent.piece_count, parallel_peers_count))
    progress_process.daemon = True
    processes.append(progress_process)
    for process in processes:
        process.start()
    feed_pieces_queue(pieces_queue, torrent.piece_count, parallel_peers_count)
    for process in processes:
        process.join()
    print("Done downloading torrent content!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='torrent-client')
    parser.add_argument("path")
    parser.add_argument('-v', "--verbose", action="store_true")
    args = parser.parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    get_content(torrent_path=args.path)
