import argparse

from torrentclient.client import Client
from torrentclient.torrent import Torrent


def add(path: str):
    Client().add(Torrent(path))


def remove(torrent: str):
    Client().remove(torrent)


def list(torrent: list):
    print(str(Client()))


def main():
    parser = argparse.ArgumentParser(prog='torrent-client')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_add = subparsers.add_parser('add', help='add a torrent')
    parser_add.add_argument('path', help='magnet link or local path')
    parser_add.set_defaults(func=add)
    parser_remove = subparsers.add_parser('remove', help='remove an existing torrent')
    parser_remove.add_argument('torrent', help='torrent ID or name')
    parser_remove.set_defaults(func=remove)
    parser_list = parser.add_subparsers('list', help='list all torrents or a specific torrent')
    parser_list.add_argument('torrent', nargs='?', default=None)
    parser_list.set_defaults(func=list)
    args = parser.parse_args()


if __name__ == "__main__": main()
