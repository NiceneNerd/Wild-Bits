from io import StringIO
from pathlib import Path
import tempfile
from typing import Union

import yaml
import aamp
from aamp import yaml_util as yu_aamp
import byml
from byml import yaml_util as yu_byml
import syaz0
import pymsyt

def open_byml(file: Union[Path, bytes]) -> (str, bool):
    byml_bytes = file.read_bytes() if isinstance(file, Path) else file
    if byml_bytes[0:4] == b'Yaz0':
        byml_bytes = syaz0.decompress(byml_bytes)
    byml_reader = byml.Byml(byml_bytes)
    data = byml_reader.parse()
    dump = StringIO()
    dumper = yaml.CSafeDumper
    yu_byml.add_representers(dumper)
    yaml.dump(data, dump, Dumper=dumper, allow_unicode=True, encoding='utf-8')
    del byml_bytes
    del data
    return dump.getvalue(), byml_reader._be # pylint: disable=protected-access


def open_aamp(file: Union[Path, bytes]) -> str:
    aamp_bytes = file.read_bytes() if isinstance(file, Path) else file
    if aamp_bytes[0:4] == b'Yaz0':
        aamp_bytes = syaz0.decompress(aamp_bytes)
    reader = aamp.Reader(aamp_bytes)
    data = reader.parse()
    dump = StringIO()
    dumper = yaml.CSafeDumper
    setattr(dumper, '__aamp_reader', reader)
    yu_aamp.register_representers(dumper)
    yaml.dump(data, dump, Dumper=dumper, allow_unicode=True, encoding='utf-8')
    del aamp_bytes
    del data
    return dump.getvalue()


def open_msbt(file: Union[Path, bytes]) -> str:
    if isinstance(file, bytes):
        tmp = tempfile.NamedTemporaryFile('wb', delete=False)
        tmp.write(file)
        tmp.close()
        file = Path(tmp.name)
    tmp_path = Path(tempfile.mkstemp('.msyt')[1])
    if pymsyt.export(file, tmp_path):
        return tmp_path.read_text(encoding='utf-8').replace('\\', '\\\\')


def save_byml(contents: str, big_endian: bool = True) -> bytes:
    loader = yaml.CSafeLoader
    yu_byml.add_constructors(loader)
    data = yaml.load(contents, Loader=loader)
    return byml.Writer(data, be=big_endian).get_bytes()


def save_aamp(contents: str,) -> bytes:
    loader = yaml.CSafeLoader
    yu_aamp.register_constructors(loader)
    data = yaml.load(contents, Loader=loader)
    return aamp.Writer(data).get_bytes()


def save_msbt(contents: str, file: Path, platform: str = 'wiiu'):
    data = yaml.safe_load(contents)
    pymsyt._debug = True
    pymsyt.write_msbt(data, file, platform=platform)
