from torrentclient.mlcode.defineparam import DefineParam, DefineParams


def test_init():
    DefineParam('k', 'key', "A test key")


def test_match_key():
    obj = DefineParam('k', 'key', "A test key")
    dp = DefineParams([('k', 'key', "A test key")])
    assert dp.match_key('k') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_key('l') is None, "Not previously defined param should not be matched"


def test_match_name():
    obj = DefineParam('k', 'key', "A test key")
    dp = DefineParams([('k', 'key', "A test key")])
    assert dp.match_name('key') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_name('ley') is None, "Not previously defined param should not be matched"
