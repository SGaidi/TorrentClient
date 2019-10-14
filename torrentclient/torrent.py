

class Torrent:

    # Constructors

    def __init__(self, path):
        self.path = path

    @classmethod
    def from_magnet_link(cls, magnet_link):
        pass

    @classmethod
    def from_data(cls, data_path):
        pass

    # Basic Attributes

    @property
    def name(self):
        pass

    def __str__(self):
        return "I'm a torrent at {}".format(self.path)
