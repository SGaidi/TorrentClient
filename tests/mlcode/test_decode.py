"""depends on `test_magnetlink.py`"""
from torrentclient.mlcode.magnetlink import MagnetLink as ml
from torrentclient.mlcode.decode import decode


def test_empty():
    assert decode("magnet:?") == ml()


def test_sample():
    assert decode("magnet:?dn=Sarah+Gaidi&tr=1.2.3.4") == \
        ml(display_name="Sarah Gaidi", address_tracker="1.2.3.4")
    assert decode("magnet:?dn=Sarah+Gaidi&tr=1.2.3.4&tr=5.6.7.8") == \
           ml(display_name="Sarah Gaidi", address_tracker=["1.2.3.4", "5.6.7.8"])


def test_real():
    assert decode(
        "magnet:?dn=wikipedia_en_all_novid_2018-06.zim&xt=urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858&tr=udp%3a%2f%2ftracker.mg64.net"
    ) == ml(
        display_name="wikipedia_en_all_novid_2018-06.zim",
        exact_topic="urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858",
        address_tracker="udp://tracker.mg64.net"
    )


def test_real_with_list():
    assert decode(
        "magnet:?dn=Eminem+-+Lose+Yourself+%5BSingle+-+2012%5D&xt=urn:btih:440ab7cfe0d0c1d8bf515e1add4a26aebb321191&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969"
    ) == ml(
        display_name="Eminem - Lose Yourself [Single - 2012]",
        exact_topic="urn:btih:440ab7cfe0d0c1d8bf515e1add4a26aebb321191",
        address_tracker=[
            "udp://tracker.leechers-paradise.org:6969",
            "udp://tracker.openbittorrent.com:80",
            "udp://open.demonii.com:1337",
            "udp://tracker.coppersurfer.tk:6969",
            "udp://exodus.desync.com:6969",
        ],
    )
