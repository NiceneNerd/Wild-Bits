from functools import lru_cache
from pathlib import Path
from typing import ByteString

from botw.hashes import StockHashTable
from oead.yaz0 import decompress
from rstb import SizeCalculator


def unyaz_if_yazd(data: ByteString) -> ByteString:
    return data if data[0:4] != b"Yaz0" else memoryview(decompress(data))


@lru_cache(2)
def get_hashtable(wiiu: bool) -> StockHashTable:
    return StockHashTable(wiiu)


@lru_cache(1)
def get_rstb_calc() -> SizeCalculator:
    return SizeCalculator()


@lru_cache(10)
def get_rstb_value(filename: str, data: ByteString, wiiu: bool) -> (int, bool):
    ext = filename[filename.rindex("."):]
    value = get_rstb_calc().calculate_file_size_with_ext(data, wiiu, ext)
    if value and ext != ".bdmgparam":
        return value, False
    else:
        from botw import rstb, extensions

        if ext in {".bfres", ".sbfres"}:
            return rstb.guess_bfres_size(bytes(data), wiiu, filename), True
        elif ext in extensions.AAMP_EXTS:
            return rstb.guess_aamp_size(bytes(data), wiiu, ext), True
        else:
            return 0, False
