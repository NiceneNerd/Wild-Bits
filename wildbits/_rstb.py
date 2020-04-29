from functools import lru_cache
from pathlib import Path
from typing import List, Union
from zlib import crc32

from botw.hashes import StockHashTable
from rstb import ResourceSizeTable
from oead.yaz0 import decompress

RSTB_HASHES = {
    crc32(file.encode('utf8')): file for file in StockHashTable(True).get_stock_files()
}


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


@lru_cache
def get_name_from_hash(crc: int) -> Union[str, int]:
    return RSTB_HASHES.get(crc, crc)
