from pathlib import Path
import yaml
from re import sub
from tempfile import NamedTemporaryFile
from typing import Union

import oead
import pymsyt

class Msbt:
    _msyt: str
    _be: bool

    def __init__(self, data: bytes):
        with NamedTemporaryFile(mode='wb', suffix='.msbt') as tmp:
            tmp.write(data)
            pymsyt.export(tmp.name, Path(tmp.name).with_suffix('.msyt'))
            self._msyt = Path(tmp.name).with_suffix('.msyt').read_text('utf-8')
        self._be = data[8:10] == b'\xFE\xFF'

    def to_yaml(self) -> str:
        return self._msyt

    def to_msbt(self, output: Path):
        with NamedTemporaryFile(mode='w', suffix='.msyt', encoding='utf-8') as tmp:
            tmp.write(self._msyt)
            pymsyt.create(tmp.name, output, platform='wiiu' if self._be else 'switch')

    @property
    def big_endian(self) -> bool:
        return self._be


def open_yaml(data: bytes) -> dict:
    yaml: str
    be: bool
    obj: Union[oead.byml.Hash, oead.byml.Array, oead.aamp.ParameterIO, Msbt]
    obj_type: str
    if data[0:4] == b'AAMP':
        obj = oead.aamp.ParameterIO.from_binary(data)
        be = False
        yaml = obj.to_text()
        obj_type = 'aamp'
    elif data[0:2] in {b'BY', b'YB'}:
        obj = oead.byml.from_binary(data)
        be = data[0:2] == b'BY'
        yaml = oead.byml.to_text(obj)
        obj_type = 'byml'
    elif data[0:8] == b'MsgStdBn':
        obj = Msbt(data)
        be = obj.big_endian
        yaml = obj.to_yaml()
        obj_type = 'msbt'
    else:
        raise ValueError()
    return {
        'yaml': yaml,
        'be': be,
        'obj': obj,
        'type': obj_type
    }
