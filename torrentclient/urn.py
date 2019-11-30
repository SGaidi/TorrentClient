import hashlib

"""
available: {'sha', 'md4', 'dsaEncryption', 'shake_128', 'blake2s', 'SHA384', 'md5', 'SHA256', 'sha512'
    , 'ecdsa-with-SHA1', 'MD4', 'shake_256', 'sha256', 'SHA224', 'sha3_256', 'blake2b', 'sha3_512', 'DSA-SHA'
    , 'ripemd160', 'sha224', 'RIPEMD160', 'SHA512', 'whirlpool', 'sha384', 'sha1', 'dsaWithSHA', 'SHA1', 'DSA'
    , 'sha3_224', 'SHA', 'sha3_384', 'MD5'}
guaranteed: {'sha3_256', 'blake2b', 'sha3_512', 'shake_128', 'blake2s', 'sha224', 'md5', 'sha384', 'sha1', 'sha512'
    , 'shake_256', 'sha256', 'sha3_224', 'sha3_384'}
"""


class URN:
    """Class for extracting all BitTorrent related information from a URN
    Reference: https://en.wikipedia.org/wiki/Magnet_URI_scheme
    """

    HASH_TO_FUNC = {
        "tree:tiger:": None,  # 32 TTH - need to find best package or implement it by self
        "sha1:": hashlib.sha1,  # 32
        "bitprint:": None,  # 32 sha1 + '.' + TTH
        "ed2k:": None,  # hex
        "aich:": None,  # 32
        "kzhash:": None,  # hex
        "btih:": None,  # hex
        "md5:": hashlib.md5,
    }

    def __init__(self, value: str):
        self.value = value
        try:
            self.value = value.split('urn:')[1]
        except IndexError:
            raise ValueError("Invalid URN '{}', should begin with 'urn:'".format(value))
        hash_func = None
        for hash_name, hash_func in URN.HASH_TO_FUNC.items():
            if self.value.startswith(hash_name):
                hash_func = hash_func
        if hash_func is None:
            raise ValueError("Invalid hash in URN '{}', should be one of: {}".format(
                self.value, URN.HASH_TO_FUNC.keys()))
