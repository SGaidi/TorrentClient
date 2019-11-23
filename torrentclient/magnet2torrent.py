from torrentclient.mlcode.magnetlink import MagnetLink
from torrentclient.mlcode.encode import encode


def magnet2torrent(magnet_link: MagnetLink):
    raw_ml = encode(magnet_link)
    ml_str = ""
    for tracker in magnet_link.address_tracker:
        ml_str += '&tr=' + tracker
    filename = "meta-" + magnet_link.exact_topic.split("urn:btih:")[1] + ".torrent"
    with open(filename, 'w+') as f:
        bencoded_ml = u'd10:magnet-uri' + str(len(raw_ml)) + u':' + raw_ml + u'e'
        f.write(bencoded_ml)


magnet2torrent(MagnetLink(
        display_name="Eminem - Lose Yourself [Single - 2012]",
        exact_topic="urn:btih:440ab7cfe0d0c1d8bf515e1add4a26aebb321191",
        address_tracker=[
            "udp://tracker.leechers-paradise.org:6969",
            "udp://tracker.openbittorrent.com:80",
            "udp://open.demonii.com:1337",
            "udp://tracker.coppersurfer.tk:6969",
            "udp://exodus.desync.com:6969",
        ],
    ))