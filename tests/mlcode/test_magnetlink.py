"""depends on `test_defineparam.py`"""
import pytest

from torrentclient.mlcode.magnetlink import MagnetLink as ml


def test_pass():
    ml()
    ml(display_name="Sarah Gaidi", address_tracker="1.2.3.4")
    ml(display_name="Sarah Gaidi", address_tracker=["1.2.3.4", "5.6.7.8"])
    ml(display_name="Torrent Client", exact_length="32")


def test_fail_type():
    with pytest.raises(TypeError):
        ml(non_existing_param="Some value")


def test_fail_value():
    with pytest.raises(ValueError):
        ml(display_name=1)
    with pytest.raises(ValueError):
        ml(address_tracker=["1.2.3.4", 5])
