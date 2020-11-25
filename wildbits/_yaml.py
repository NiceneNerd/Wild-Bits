# pylint: disable=bad-continuation
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Union

import oead
from pymsyt import Msbt
from oead.aamp import get_default_name_table


@lru_cache(1)
def _init_deepmerge_name_table():
    table = get_default_name_table()
    for i in range(10000):
        table.add_name(f"File{i}")

def open_yaml(file: Path) -> dict:
    yaml: str
    big_endian: bool
    obj: Union[oead.byml.Hash, oead.byml.Array, oead.aamp.ParameterIO, Msbt]
    obj_type: str
    data = file.read_bytes()
    if data[0:4] == b"Yaz0":
        data = oead.yaz0.decompress(data)
    if data[0:4] == b"AAMP":
        obj = oead.aamp.ParameterIO.from_binary(data)
        big_endian = False
        _init_deepmerge_name_table()
        yaml = obj.to_text()
        obj_type = "aamp"
    elif data[0:2] in {b"BY", b"YB"}:
        obj = oead.byml.from_binary(data)
        big_endian = data[0:2] == b"BY"
        yaml = oead.byml.to_text(obj)
        obj_type = "byml"
    elif data[0:8] == b"MsgStdBn":
        obj = Msbt.from_binary(data)
        big_endian = data[0x08:0x0A] == b"\xfe\xff"
        yaml = obj.to_yaml()
        obj_type = "msbt"
    else:
        raise ValueError()
    return {"yaml": yaml, "big_endian": big_endian, "obj": obj, "type": obj_type}


def get_sarc_yaml(file) -> dict:
    yaml: str
    big_endian: bool
    obj: Union[oead.byml.Hash, oead.byml.Array, oead.aamp.ParameterIO, Msbt]
    obj_type: str
    data = file.data if file.data[0:4] != b"Yaz0" else oead.yaz0.decompress(file.data)
    if data[0:4] == b"AAMP":
        obj = oead.aamp.ParameterIO.from_binary(data)
        big_endian = False
        yaml = obj.to_text()
        obj_type = "aamp"
    elif data[0:2] in {b"BY", b"YB"}:
        obj = oead.byml.from_binary(data)
        big_endian = data[0:2] == b"BY"
        yaml = oead.byml.to_text(obj)
        obj_type = "byml"
    elif data[0:8] == b"MsgStdBn":
        obj = Msbt.from_binary(bytes(data))
        big_endian = data[0x08:0x0A] == b"\xfe\xff"
        yaml = obj.to_yaml()
        obj_type = "msbt"
    else:
        raise ValueError()
    return {"yaml": yaml, "big_endian": big_endian, "obj": obj, "type": obj_type}


def save_yaml(yaml: str, obj_type: str, big_endian: bool = False):
    if obj_type == "aamp":
        return oead.aamp.ParameterIO.from_text(yaml).to_binary()
    elif obj_type == "byml":
        return oead.byml.to_binary(oead.byml.from_text(yaml), big_endian=big_endian)
    elif obj_type == "msbt":
        return Msbt.from_yaml(yaml).to_binary(big_endian)
