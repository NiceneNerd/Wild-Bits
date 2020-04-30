import json
from io import BytesIO
from functools import lru_cache
from pathlib import Path
from typing import List, Union
from zlib import crc32

import botw.rstb, botw.extensions
from botw.hashes import StockHashTable
from rstb import ResourceSizeTable, SizeCalculator
from oead.yaz0 import decompress, compress
from . import DATA_DIR

RSTB_HASHES = {
    crc32(file.encode('utf8')): file for file in StockHashTable(True).get_stock_files()
}

_CUSTOM_PATH = DATA_DIR / 'custom.json'

if not _CUSTOM_PATH.exists():
    _CUSTOM_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CUSTOM_PATH.write_text('{}')


def open_rstb(file: Path) -> ResourceSizeTable:
    data = file.read_bytes()
    if data[0:4] == b'Yaz0':
        data = decompress(data)
    be = True
    rstb = ResourceSizeTable(data, be=True)
    random_tests = {
        'EventFlow/PictureMemory.bfevfl',
        'Camera/Demo648_0/C04-0.bcamanim',
        'Effect/FldObj_ScaffoldIronParts_A_01.esetlist',
        'Physics/TeraMeshRigidBody/MainField/9-8.hktmrb'
    }
    if not any(rstb.is_in_table(f) for f in random_tests):
        del rstb
        rstb = ResourceSizeTable(data, be=False)
        be = False
        if not any(rstb.is_in_table(f) for f in random_tests):
            raise ValueError('File does not appeat to be a valid BOTW RSTB')
    return rstb, be


@lru_cache(2048)
def get_name_from_hash(crc: int) -> Union[str, int]:
    if crc in RSTB_HASHES:
        return RSTB_HASHES[crc]
    else:
        addeds: dict = json.loads(
            _CUSTOM_PATH.read_text('utf-8')
        )
        return addeds.get(crc, crc)


def get_rstb_value(file: Path, be: bool) -> (int, bool):
    guess = False
    size = SizeCalculator().calculate_file_size(
        str(file),
        wiiu=be,
        force=False
    )
    if size == 0:
        ext = file.suffix
        if ext in botw.extensions.AAMP_EXTS:
            size = botw.rstb.guess_aamp_size(file)
            guess = True
        elif ext in {'.sbfres', '.bfres'}:
            size = botw.rstb.guess_bfres_size(file)
            guess = True
    return size, guess


def add_custom(path: str):
    addeds: dict = json.loads(
        _CUSTOM_PATH.read_text('utf-8')
    )
    addeds[crc32(path.encode('utf8'))] = path
    _CUSTOM_PATH.write_text(
        json.dumps(addeds),
        encoding='utf-8'
    )


def write_rstb(rstb: ResourceSizeTable, path: Path, be: bool):
    buf = BytesIO()
    rstb.write(buf, be)
    path.write_bytes(
        compress(buf.getvalue())
    )


def rstb_to_json(rstb: ResourceSizeTable, path: Path):
    path.write_text(
        json.dumps(
            {get_name_from_hash(crc): size for crc, size in rstb.crc32_map.items()},
            ensure_ascii=False,
            indent=4
        ),
        encoding='utf-8'
    )
