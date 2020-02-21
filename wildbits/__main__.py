import webview

import botw
from . import EXEC_DIR

class Api:
    def get_sarc_exts(self):
        return botw.extensions.SARC_EXTS

def main():
    webview.create_window('Wild Bits', url=str(EXEC_DIR / 'assets' / 'index.html'))
    webview.start(debug=True, http_server=False)


if __name__ == "__main__":
    main()