import pytest

from torrentclient.mlcode.defineparam import DefineParam as df


@pytest.fixture(autouse=True)
def backup_defined_params():
    backup = df.DEFINED_PARAMS
    df.DEFINED_PARAMS = []
    yield
    df.DEFINED_PARAMS = backup


def test_init():
    df('k', 'key', "A test key")


def test_match_key():
    obj = df('k', 'key', "A test key")
    assert df.match_key('k') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert df.match_key('l') is None, "Not previously defined param should not be matched"


def test_match_name():
    obj = df('k', 'key', "A test key")
    assert df.match_name('key') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert df.match_name('ley') is None, "Not previously defined param should not be matched"
