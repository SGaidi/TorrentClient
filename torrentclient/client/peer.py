import logging


class Peer:
    """Data class of BitTorrent remote peer"""

    logger = logging.getLogger('peer')

    class Exception(Exception):
        """An exception with remote peer occurred"""

    def __init__(self, ip_address: str, port: str):
        self.ip_address = ip_address
        self.port = port

    def __str__(self):
        return "Peer({}:{})".format(self.ip_address, self.port)

    def __repr__(self):
        return {'ip_address': self.ip_address, 'port': self.port}
