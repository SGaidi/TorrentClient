from torrentclient.mlcode.defineparam import DefineParam, DefineParams


def test_init():
    DefineParam('k', 'key', "A test key")


def test_match_key():
    obj = DefineParam('k', 'key', "A test key")
    dp = DefineParams([('k', 'key', "A test key")])
    assert dp.match_key('k') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_key('l') is None, "Not previously defined param should not be matched"


def test_match_name():
    obj = DefineParam('n', 'name', "A test name")
    dp = DefineParams([('n', 'name', "A test name")])
    assert dp.match_name('name') == obj, "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_name('mane') is None, "Not previously defined param should not be matched"


def test_multiple_definitions():
    dp1 = DefineParam('a', 'A name', "A test parameter A")
    dp2 = DefineParam('b', 'B name', "A test parameter B")
    dp3 = DefineParam('c', 'C name', "A test parameter C")

    dp = DefineParams([
        ('a', 'A name', "A test parameter A"),
        ('b', 'B name', "A test parameter B"),
        ('d', 'D name', "A test parameter D"),
    ])
    assert dp.match_key('a') == dp1, "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_key('b') == dp2, "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_key('c') is None, "Not previously defined param should not be matched"
    assert dp.match_key('d') is not None, "A previously defined param should be matched"
    assert dp.match_key('e') is None, "Not previously defined param should not be matched"

    assert dp.match_name('A name') == dp1,\
        "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_name('B name') == dp2, \
        "After defining a parameter, it should be matched with the DefineParam object"
    assert dp.match_name('C name') is None, \
        "Not previously defined param should not be matched"
    assert dp.match_name('D name') is not None, \
        "A previously defined param should be matched"
    assert dp.match_name('E name') is None, \
        "Not previously defined param should not be matched"
