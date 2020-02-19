import webview

from . import EXEC_DIR

def main():
    webview.create_window('Wild Bits', url=str(EXEC_DIR / 'assets' / 'index.html'))
    webview.start(debug=True, http_server=False)


if __name__ == "__main__":
    main()