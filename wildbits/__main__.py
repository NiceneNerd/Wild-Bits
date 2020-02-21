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
            self._open_sarc, tree = _sarc.open_sarc(file)
            return {
                'path': str(file.resolve()),
                'sarc': tree,
                'be': self._open_sarc.get_endianness() == oead.Endianness.Big
            }


def main():
    api = Api()
    api.window = webview.create_window('Wild Bits', url=str(EXEC_DIR / 'assets' / 'index.html'), js_api=api)
    webview.start(debug=True, http_server=False)


if __name__ == "__main__":
    main()