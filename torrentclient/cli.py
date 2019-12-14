import argparse

#from torrentclient.client import Client


def add(args):
    path = args.path
    if path.endswith(".torrent"):
        from torrentclient.client.get import get_content
        get_content(torrent=path)
    else:
        print("content file")


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
    parser_list = subparsers.add_parser('list', help='list all torrents or a specific torrent')
    parser_list.add_argument('torrent', nargs='?', default=None)
    parser_list.set_defaults(func=list)
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__": main()
