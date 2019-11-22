"""depends on `test_magnetlink.py`"""
from torrentclient.mlcode.magnetlink import MagnetLink as ml
from torrentclient.mlcode.encode import encode


def test_empty():
    assert encode(ml()) == "magnet:?"


def test_sample():
    assert encode(ml(display_name="Sarah Gaidi", address_tracker="1.2.3.4")) == \
           "magnet:?dn=Sarah+Gaidi&tr=1.2.3.4"
    assert encode(ml(display_name="Sarah Gaidi", address_tracker=["1.2.3.4", "5.6.7.8"])) == \
           "magnet:?dn=Sarah+Gaidi&tr=1.2.3.4&tr=5.6.7.8"


def test_real():
    assert encode(ml(
        display_name="wikipedia_en_all_novid_2018-06.zim",
        exact_topic="urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858",
        address_tracker="udp%3a%2f%2ftracker.mg64.net"
    )) == "magnet:?dn=wikipedia_en_all_novid_2018-06.zim&xt=urn:btih:b54a3ba68fd398ed019e21290beecc9dda64a858&tr=udp%3a%2f%2ftracker.mg64.net"


def test_real_with_list():
    assert encode(ml(
        display_name="Eminem+-+Lose+Yourself+%5BSingle+-+2012%5D",
        exact_topic="urn:btih:440ab7cfe0d0c1d8bf515e1add4a26aebb321191",
        address_tracker=[
            "udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969",
            "udp%3A%2F%2Ftracker.openbittorrent.com%3A80",
            "udp%3A%2F%2Fopen.demonii.com%3A1337",
            "udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969",
            "udp%3A%2F%2Fexodus.desync.com%3A6969",
        ],
    )) == "magnet:?dn=Eminem+-+Lose+Yourself+%5BSingle+-+2012%5D&xt=urn:btih:440ab7cfe0d0c1d8bf515e1add4a26aebb321191&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969"
