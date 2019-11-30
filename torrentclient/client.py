from torrentclient.torcode.torrent import Torrent


class Client:
    """Holds torrents with IDs"""

    def __load_torrents(self):
        """TODO
        self.torrents = get from file
        assume file is correct and self is a singleton
        """
        return []

    def __save_torrents(self):
        """TODO: should it be called for each single torrent change?"""

    def __init__(self):
        self.torrents = self.__load_torrents()

    def __str__(self):
        # TODO: add header for idx, name, path and status
        return "Torrent Client\n" + '\n'.join("{}: {}".format(idx, torrent) for idx, torrent in enumerate(self.torrents))

    def add(self, new_torrent: Torrent):
        if new_torrent in self.torrents:
            raise ValueError("{} already exists in torrents list".format(new_torrent))
        self.torrents.append(new_torrent)
        # TODO: start thread for downloading

    def remove(self, torrent_idx: int):
        if torrent_idx < 0 or torrent_idx >= len(self.torrents):
            raise ValueError("No torrent with ID {}, only {} exist".format(torrent_idx, len(self.torrents)))
        self.torrents.pop(torrent_idx)
