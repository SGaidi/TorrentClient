import math
import bencode

from torf import Torrent


class MyTorrent(Torrent):
    """Class wrapper to torf's Torrent, adding fixes and additional features"""

    @classmethod
    def read(cls, *args, **kwargs):
        obj = super().read(*args, **kwargs)
        if obj.path is None:
            obj.path = kwargs['filepath']
        return obj

    @property
    def total_length(self) -> int:
        bcode = bencode.bread(self.path)
        if 'length' in bcode['info']:
            self._total_length = bcode['info']['length']
        else:
            self._total_length = 0
            for file in bcode['info']['files']:
                self._total_length += file['length']
        return self._total_length

    @property
    def infohash(self) -> bytes:
        import hashlib
        return hashlib.sha1(bencode.bencode(bencode.bread(self.path)['info'])).digest()

    @property
    def raw_hashes(self) -> bytes:
        return bencode.bread(self.path)['info']['pieces']

    @property
    def hashes(self):
        """fix of hashes attribute in torf
        and used list instead of generator"""
        return [self.raw_hashes[idx:idx+20] for idx in range(0, self.pieces)]

    @property
    def piece_count(self) -> int:
        """number of hashed pieces"""
        return len(self.raw_hashes) // 20

    @property
    def my_piece_size(self) -> int:
        """size of hashed piece [bytes]"""
        minimal_size = round(self.total_length / self.piece_count)
        return 2 ** math.ceil(math.log(minimal_size, 2))  # rounds up to highest 2**x value

    @property
    def block_count(self) -> int:
        """number of maximum blocks in a piece"""
        return math.ceil(self.my_piece_size / self.block_size)

    @property
    def block_size(self) -> int:
        """block length to request from peer [bytes]"""
        return self.piece_size

