from torrentclient.client import Client
from torrentclient.torrent import Torrent


def test_client():
    client = Client()
    client.add(Torrent("a"))
    client.add(Torrent("b"))
    client.add(Torrent("c"))
    print(client)
    client.add(Torrent("d"))
    print(client)
    client.remove(1)
    print(client)
