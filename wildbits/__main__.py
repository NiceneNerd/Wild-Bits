from pathlib import Path
from typing import Union

import botw
import oead
from oead.yaz0 import decompress
from rstb import ResourceSizeTable
import webview
from . import EXEC_DIR, _sarc

class Api:
    window: webview.Window
    _open_sarc: oead.Sarc
    _open_rstb: ResourceSizeTable
    _open_byml: Union[oead.byml.Hash, oead.byml.Array]
    _open_pio: oead.aamp.ParameterIO
    _open_msbt: dict

    def open_sarc(self) -> dict:
        result = self.window.create_file_dialog(webview.OPEN_DIALOG)
        if result:
            file = Path(result[0])
            try:
                self._open_sarc, tree = _sarc.open_sarc(file)
            except ValueError:
                return {}
            return {
                'path': str(file.resolve()),
                'sarc': tree,
                'be': self._open_sarc.get_endianness() == oead.Endianness.Big
            }
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
            new_sarc: oead.SarcWriter = oead.SarcWriter.from_sarc(self._open_sarc)
            data = self._open_sarc.get_file(file).data
            new_sarc.files[new_name] = data
            self._open_sarc, tree = _sarc.open_sarc(oead.Sarc())
        except (ValueError, KeyError) as e:
            return {'error': str(e)}
        return tree


def main():
    api = Api()
    api.window = webview.create_window('Wild Bits', url=str(EXEC_DIR / 'assets' / 'index.html'), js_api=api)
    webview.start(
        debug=False,
        http_server=False
    )


if __name__ == "__main__":
    main()