from pathlib import Path
from platform import system
from typing import Union
from zlib import crc32

import botw, botw.rstb, botw.extensions
import oead
from oead.yaz0 import decompress, compress
from rstb import ResourceSizeTable
import webview
from . import EXEC_DIR, _sarc, _rstb, _yaml

class Api:
    window: webview.Window
    _open_sarc: oead.Sarc
    _open_rstb: ResourceSizeTable
    _open_rstb_be: bool
    _open_yaml: Union[oead.byml.Hash, oead.byml.Array, oead.aamp.ParameterIO, _yaml.Msbt]
    
    def browse(self) -> Union[str, None]:
        result = self.window.create_file_dialog(webview.OPEN_DIALOG)
        if result:
            return result[0]
        else:
            return None
    
    ###############
    # SARC Editor #
    ###############
    def open_sarc(self) -> dict:
        result = self.browse()
        if not result:
            return {}
        file = Path(result)
        try:
            self._open_sarc, tree, modded = _sarc.open_sarc(file)
        except (ValueError, RuntimeError, oead.InvalidDataError):
            return {'error': f'{file.name} is not a valid SARC file'}
        return {
            'path': str(file.resolve()),
            'sarc': tree,
            'modded': modded,
            'be': self._open_sarc.get_endianness() == oead.Endianness.Big
        }

    def create_sarc(self, be: bool, alignment: int) -> dict:
        tmp_sarc = oead.SarcWriter(
            oead.Endianness.Big if be else oead.Endianness.Little,
            oead.SarcWriter.Mode.New if alignment == 4 else oead.SarcWriter.Mode.Legacy
        )
        self._open_sarc, tree, modded = _sarc.open_sarc(
            oead.Sarc(
                tmp_sarc.write()[1]
            )
        )
        return {
            'sarc': tree,
            'be': be,
            'path': '',
            'modded': modded,
        }
        
    def save_sarc(self, path: str = '') -> dict:
        if not path:
            result = self.window.create_file_dialog(webview.SAVE_DIALOG)
            if result:
                path = result[0]
            else:
                return {'error': 'Cancelled'}
        path = Path(path)
        try:
            path.write_bytes(
                oead.SarcWriter.from_sarc(self._open_sarc).write()[1]
            )
        except (ValueError, OSError) as e:
            return {'error': str(e)}
        else:
            return {}
        
        
    def get_file_info(self, file: str, wiiu: bool) -> dict:
        return _sarc.get_nested_file_meta(self._open_sarc, file, wiiu)
    
    def extract_sarc_file(self, file: str) -> dict:
        filename = Path(file).name
        output = self.window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=filename
        )
        if output:
            out = Path(output[0])
            try:
                out.write_bytes(
                    _sarc.get_nested_file_data(
                        self._open_sarc, file, unyaz=False
                    )
                )
                return {
                    'success': True
                }
            except Exception as e:
                return {
                    'error': str(e)
                }
    
    def rename_sarc_file(self, file: str, new_name: str) -> dict:
        try:
            self._open_sarc, tree, modded = _sarc.open_sarc(
                _sarc.rename_file(self._open_sarc, file, new_name)
            )
        except (ValueError, KeyError) as e:
            return {'error': str(e)}
        return tree, modded

    def delete_sarc_file(self, file: str) -> dict:
        try:
            self._open_sarc, tree, modded = _sarc.open_sarc(
                _sarc.delete_file(self._open_sarc, file)
            )
        except (ValueError, KeyError) as e:
            return {'error': str(e)}
        return tree, modded
    
    def add_sarc_file(self, file: str, sarc_path: str) -> dict:
        try:
            data = memoryview(Path(file).read_bytes())
            self._open_sarc, tree, modded = _sarc.open_sarc(
                _sarc.add_file(self._open_sarc, sarc_path, data)
            )
        except (AttributeError, ValueError, KeyError, OSError, TypeError, FileNotFoundError) as e:
            return {'error': str(e)}
        return tree, modded

    def update_sarc_folder(self) -> dict:
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return {}
        try:
            self._open_sarc, tree, modded = _sarc.open_sarc(
                _sarc.update_from_folder(self._open_sarc, Path(result[0]))
            )
        except (FileNotFoundError, OSError, ValueError) as e:
            return {'error': str(e)}
        return tree, modded

    def extract_sarc(self):
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return {}
        try:
            output = Path(result[0])
            for file in self._open_sarc.get_files():
                (output / file.name).parent.mkdir(parents=True, exist_ok=True)
                (output / file.name).write_bytes(file.data)
        except (FileNotFoundError, OSError) as e:
            return {'error': str(e)}
        return {}

    def get_sarc_yaml(self, path: str) -> dict:
        try:            
            file = _sarc.get_nested_file(self._open_sarc, path)
            opened = _yaml.get_sarc_yaml(file)
            self._open_yaml = opened['obj']
            return {
                'path': 'SARC:' + path,
                'yaml': opened['yaml'],
                'be': opened['be'],
                'type': opened['type']
            }
        except Exception as e:
            return {'error': str(e)}

    ###############
    # RSTB Editor #
    ###############
    def open_rstb(self) -> dict:
        result = self.browse()
        if not result:
            return {}
        file = Path(result)
        try:
            self._open_rstb, self._open_rstb_be = _rstb.open_rstb(file)
        except (ValueError, IndexError) as e:
            return {'error': str(e)}
        return {
            'path': str(file.resolve()),
            'rstb': {
                _rstb.get_name_from_hash(crc): size for crc, size in self._open_rstb.crc32_map.items()
            },
            'be': self._open_rstb_be
        }

    def browse_file_size(self) -> dict:
        result = self.browse()
        if not result:
            return {}
        try:
            size, guess = _rstb.get_rstb_value(Path(result), self._open_rstb_be)
        except ValueError as e:
            return {'error': str(e)}
        return {
            'size': size,
            'guess': guess
        }

    def set_entry(self, path: str, size: int) -> dict:
        try:
            self._open_rstb.set_size(path, size)
            if isinstance(_rstb.get_name_from_hash(crc32(path.encode('utf8'))), int):
                _rstb.add_custom(path)
        except Exception as e:
            return {'error': str(e)}
        return {}

    def delete_entry(self, path: str):
        self._open_rstb.delete_entry(path)

    def save_rstb(self, path: str = '') -> dict:
        if not path:
            result = self.window.create_file_dialog(
                webview.SAVE_DIALOG,
                file_types=tuple(['RSTB File (*.rsizetable; *.srsizetable)'])
            )
            if result:
                path = result[0]
            else:
                return {'error': 'Cancelled'}
        path = Path(path)
        try:
            _rstb.write_rstb(self._open_rstb, path, self._open_rstb_be)
        except Exception as e:
            return {'error': str(e)}
        return {'path': str(path)}

    def export_rstb(self) -> dict:
        result = self.window.create_file_dialog(webview.SAVE_DIALOG, file_types=tuple(['JSON files (*.json)']))
        if not result:
            return {}
        try:
            _rstb.rstb_to_json(self._open_rstb, Path(result[0]))
        except Exception as e:
            return {'error': str(e)}
        return {}

    ###############
    # YAML Editor #
    ###############
    def open_yaml(self) -> dict:
        result = self.browse()
        if not result:
            return {}
        file = Path(result)
        try:
            opened = _yaml.open_yaml(file)
        except ValueError:
            return {'error': f'{file.name} is not a valid AAMP, BYML, or MSBT file.'}
        self._open_yaml = opened['obj']
        return {
            'path': str(file),
            'yaml': opened['yaml'],
            'be': opened['be'],
            'type': opened['type']
        }

    def save_yaml(self, yaml: str, obj_type: str, be: bool, path: str) -> dict:
        if not path:
            result = self.window.create_file_dialog(webview.SAVE_DIALOG)
            if result:
                path = result[0]
            else:
                return {'error': 'Cancelled'}
        try:
            data = _yaml.save_yaml(yaml, obj_type, be)
            pathy_path = Path(path)
            if pathy_path.suffix.startswith(".s"):
                data = compress(data)
            if not path.startswith('SARC:'):
                pathy_path.write_bytes(data)
            else:
                self._open_sarc, tree, modded = _sarc.open_sarc(
                    _sarc.add_file(self._open_sarc, path, data)
                )
                return {'modded': modded}
        except Exception as err: # pylint: disable=broad-except
            return {'error': str(err)}
        return {}


def main():
    api = Api()
    api.window = webview.create_window('Wild Bits', url=f'{EXEC_DIR}/assets/index.html', js_api=api)
    gui: str = ''
    if system() == 'Windows':
        try:
            from cefpython3 import cefpython
            gui = 'cef'
        except ImportError:
            pass
    webview.start(
        debug=True,
        http_server=True,
        gui=gui
    )


if __name__ == "__main__":
    main()
