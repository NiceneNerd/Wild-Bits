from functools import lru_cache, reduce
from pathlib import Path
from typing import List, Mapping, Union

from botw import extensions
from oead import Sarc
from oead.yaz0 import decompress
from . import util

def open_sarc(sarc: Union[Path, Sarc]) -> (Sarc, dict):
    if isinstance(sarc, Path):
        data = util.unyaz_if_yazd(sarc.read_bytes())
        sarc = Sarc(data)
    def get_sarc_tree(parent_sarc: Sarc) -> {}:
        tree = {}
        for file in parent_sarc.get_files():
            path_parts = Path(file.name).parts
            magic = file.data[0:4]
            nest_tree = {}
            if magic == b'SARC' or (
                magic == b'Yaz0' and file.data[0x11:0x15] == b'SARC'
            ):
                nest_sarc = Sarc(
                    file.data if not magic == b'Yaz0' else decompress(file.data)
                )
                nest_tree = get_sarc_tree(nest_sarc)
                del nest_sarc
            _dict_merge(
                tree,
                reduce(
                    lambda res, cur: {cur: res},
                    reversed(path_parts), nest_tree
                )
            )
        return tree
    return sarc, get_sarc_tree(sarc)


@lru_cache(10)
def get_nested_file_data(sarc: Sarc, file: str, unyaz: bool = True) -> bytes:
    if file.endswith('/'):
        file = file[0:-1]
    nests = file.split('//')
    sarcs: List[Sarc] = [
        sarc
    ]
    i = 0
    while i < len(nests) - 1:
        nf = sarcs[i - 1].get_file(nests[i])
        sarc_bytes = util.unyaz_if_yazd(
            nf.data
        )
        sarcs.append(Sarc(sarc_bytes))
        i += 1
    file_bytes = sarcs[-1].get_file(nests[-1]).data
    return memoryview(file_bytes) if not unyaz else memoryview(
        util.unyaz_if_yazd(file_bytes)
    )


@lru_cache(32)
def get_nested_file_meta(sarc: Sarc, file: str, wiiu: bool) -> {}:
    data: memoryview = get_nested_file_data(sarc, file)
    filename = Path(file).name.replace('.s', '.')
    return {
        'file': Path(file).name,
        'rstb': util.get_rstb_value(
            filename, data, wiiu
        ),
        'modified': util.get_hashtable(wiiu).is_file_modded(
            file.split('//')[-1].replace('.s', '.'),
            data
        ),
        'size': len(data),
        'is_yaml': (
            Path(filename).suffix in
            (extensions.AAMP_EXTS | extensions.BYML_EXTS)
        )
    }


def _dict_merge(dct: dict, merge_dct: dict, overwrite_lists: bool = False):
    for k in merge_dct:
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)):
            _dict_merge(dct[k], merge_dct[k])
        elif (k in dct and isinstance(dct[k], list)
              and isinstance(merge_dct[k], list)):
            if overwrite_lists:
                dct[k] = merge_dct[k]
            else:
                dct[k].extend(merge_dct[k])
        else:
            dct[k] = merge_dct[k]
