import os

from torrentclient.torcode.torrent import Torrent


EXAMPLE_MAGNET_LINK = "magnet:?xt=urn:btih:7ed1897b4be54be0544dab3fe0d0bbbe914bd162&dn=I.Am.Legend.2007.1080p.10bit.x265.HEVC.2CH+-+%5BANONA911%5D&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969"
EXAMPLE_FILE_PATHS = os.listdir(os.path.join(os.path.dirname(__file__), "raw"))
EXAMPLE_torrent = os.listdir(os.path.join(os.path.dirname(__file__), "torrents"))[0]


def test_torrent_file(path: str = EXAMPLE_torrent):
    Torrent(path)


def test_magnet_link(link: str = EXAMPLE_MAGNET_LINK):
    Torrent.from_magnet_link(link)


def test_data_paths(data_paths: str = EXAMPLE_FILE_PATHS):
    for data_path in data_paths:
        Torrent.from_data(data_path)
