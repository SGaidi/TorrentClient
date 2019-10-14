import argparse


def main():
    parser = argparse.ArgumentParser(title='torrent-client')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_add = subparsers.add_parser('add', help='add a torrent')
    parser_add.add_argument('torrent', help='magnet link or local path')
    parser_remove = subparsers.add_parser('remove', help='remove an existing torrent')
    parser_remove.add_argument('torrent', help='torrent ID or name')
    args = parser.parse_args()


if __name__ == "__main__": main()
