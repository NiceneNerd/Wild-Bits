from pathlib import Path

from oead import Sarc
from oead.yaz0 import decompress

def open_sarc(path: Path) -> (Sarc, dict):
    data = path.read_bytes()
    if data[0:4] == b'Yaz0':
        data = decompress(data)
    sarc = Sarc(data)
    def get_sarc_tree(parent_sarc: Sarc) -> {}:
        tree = {}
        for file in parent_sarc.get_files():
            tree[file.name] = {}
            magic = file.data[0:4]
            if magic == b'SARC' or (magic == b'Yaz0' and data[0x11:0x15] == b'SARC'):
                nest_sarc = Sarc(data if not magic == b'Yaz0' else decompress(data))
                tree[file.name].update(
                    get_sarc_tree(nest_sarc)
                )
                del nest_sarc
        return tree
    return sarc, get_sarc_tree(sarc)
