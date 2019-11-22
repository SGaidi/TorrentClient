from torrentclient.mlcode.defineparam import DefineParam as df


def reset_defined_params():
    df.DEFINED_PARAMS = []


def test_init():
    df('k', 'key', "A test key")


def test_match_key():
    reset_defined_params()
    obj = df('k', 'key', "A test key")
    assert df.match_key('k') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert df.match_key('l') is None, "Not previously define param should not be matched"


def test_match_name():
    reset_defined_params()
    obj = df('k', 'key', "A test key")
    assert df.match_name('key') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert df.match_name('ley') is None, "Not previously define param should not be matched"
