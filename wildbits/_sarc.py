from functools import lru_cache, reduce
from pathlib import Path
from typing import List, Mapping, Union

from botw import extensions
from oead import Sarc, SarcWriter, Endianness, Bytes
from oead.yaz0 import decompress
from . import util

def open_sarc(sarc: Union[Path, Sarc]) -> (Sarc, dict, list):
    if isinstance(sarc, Path):
        data = util.unyaz_if_yazd(sarc.read_bytes())
        sarc = Sarc(data)

    modified_files = set()
    def get_sarc_tree(parent_sarc: Sarc) -> (dict, list):
        tree = {}
        modded = set()
        for file in sorted(parent_sarc.get_files(), key=lambda f: f.name):
            path_parts = Path(file.name).parts
            magic = file.data[0:4]
            nest_tree = {}
            if magic == b'SARC' or (
                magic == b'Yaz0' and file.data[0x11:0x15] == b'SARC'
            ):
                nest_sarc = Sarc(
                    file.data if not magic == b'Yaz0' else decompress(file.data)
                )
                nest_tree, mods = get_sarc_tree(nest_sarc)
                modded.update(mods)
                del nest_sarc
            _dict_merge(
                tree,
                reduce(
                    lambda res, cur: {cur: res},
                    reversed(path_parts), nest_tree
                )
            )
            if (util
                .get_hashtable(parent_sarc.get_endianness() == Endianness.Big)
                .is_file_modded(file.name, bytes(file.data))):
                modded.add(file.name)
        return tree, modded
    get_nested_file_data.cache_clear()
    get_nested_file_meta.cache_clear()
    tree, modded = get_sarc_tree(sarc)
    return sarc, tree, list(modded)


@lru_cache(10)
def get_nested_file(sarc: Sarc, file: str):
    if file.endswith('/'):
        file = file[0:-1]
    return get_parent_sarc(sarc, file).get_file(
        file.split('//')[-1]
    )     


@lru_cache(10)
def get_nested_file_data(sarc: Sarc, file: str, unyaz: bool = True) -> bytes:
    file_bytes = get_nested_file(sarc, file).data
    return bytes(file_bytes) if not unyaz else bytes(
        util.unyaz_if_yazd(file_bytes)
    )


@lru_cache(32)
def get_nested_file_meta(sarc: Sarc, file: str, wiiu: bool) -> {}:
    if file.endswith('/'):
        file = file[0:-1]
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
            (extensions.AAMP_EXTS | extensions.BYML_EXTS | {".msbt"})
        )
    }
    

@lru_cache(8)
def get_parent_sarc(root_sarc: Sarc, file: str) -> Sarc:
    if file.endswith('/'):
        file = file[0:-1]
    nests = file.replace("SARC:", "").split('//')
    parent = root_sarc
    i = 0
    while i < len(nests) - 1:
        try:
            nf = parent.get_file(nests[i])
            sarc_bytes = util.unyaz_if_yazd(
                nf.data
            )
        except AttributeError:
            raise FileNotFoundError(f"Could not find file {nests[i]} in {nests[i - 1]}")
        ns = Sarc(sarc_bytes)
        del parent
        parent = ns
        i += 1
    return parent


def delete_file(root_sarc: Sarc, file: str) -> Sarc:
    if file.endswith('/'):
        file = file[0:-1]
    parent = get_parent_sarc(root_sarc, file)
    filename = file.split('//')[-1]
    new_sarc: SarcWriter = SarcWriter.from_sarc(parent)
    del new_sarc.files[filename]
    while root_sarc != parent:
        _, child = new_sarc.write()
        file = file[0:file.rindex('//')]
        parent = get_parent_sarc(root_sarc, file)
        new_sarc = SarcWriter.from_sarc(parent)
        new_sarc.files[file] = child
    return Sarc(new_sarc.write()[1])


def rename_file(root_sarc: Sarc, file: str, new_name: str) -> Sarc:
    if file.endswith('/'):
        file = file[0:-1]
    if any(char in new_name for char in "\/:*?\"'<>|"):
        raise ValueError(f'{new_name} is not a valid file name.')
    parent = get_parent_sarc(root_sarc, file)
    filename = file.split('//')[-1]
    new_sarc: SarcWriter = SarcWriter.from_sarc(parent)
    del new_sarc.files[filename]
    new_sarc.files[
        str(Path(filename).parent / new_name)
    ] = Bytes(parent.get_file(filename).data)
    while root_sarc != parent:
        _, child = new_sarc.write()
        file = file[0:file.rindex('//')]
        parent = get_parent_sarc(root_sarc, file)
        new_sarc = SarcWriter.from_sarc(parent)
        new_sarc.files[file] = child
    return Sarc(new_sarc.write()[1])


def add_file(root_sarc: Sarc, file: str, data: memoryview) -> Sarc:
    if file.endswith('/'):
        file = file[0:-1]
    file = file.replace("SARC:", "")
    parent = get_parent_sarc(root_sarc, file)
    filename = file.split('//')[-1]
    new_sarc: SarcWriter = SarcWriter.from_sarc(parent)
    new_sarc.files[filename] = Bytes(data)
    while root_sarc != parent:
        _, child = new_sarc.write()
        file = file[0:file.rindex('//')]
        parent = get_parent_sarc(root_sarc, file)
        new_sarc = SarcWriter.from_sarc(parent)
        new_sarc.files[file] = child
    return Sarc(new_sarc.write()[1])


def update_from_folder(sarc: Sarc, folder: Path) -> Sarc:
    new_sarc: SarcWriter = SarcWriter.from_sarc(sarc)
    for file in {f for f in folder.rglob('**/*') if f.is_file()}:
        new_sarc.files[file.relative_to(folder).as_posix()] = file.read_bytes()
    return Sarc(new_sarc.write()[1])


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
