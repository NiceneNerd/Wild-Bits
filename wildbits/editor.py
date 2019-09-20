import os
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtWebChannel

EXEC_DIR = os.path.dirname(os.path.realpath(__file__))

class CodeEditorWidget(QtWebEngineWidgets.QWebEngineView):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.channel = QtWebChannel.QWebChannel(self.page())
        self.page().setWebChannel(self.channel)
        self.channel.registerObject('jshelper', self)
        self.load(QtCore.QUrl.fromLocalFile(os.path.join(EXEC_DIR, 'assets', 'index.html')))
        self._text = ''
        self._readonly = False
        QtCore.qInstallMessageHandler(lambda x,y,z: None)

    def setText(self, text: str) -> None:
        self.page().runJavaScript(f'var editor = ace.edit("editor"); editor.setValue(`{text}`);')

    def text(self) -> str:
        return self._text

    def setReadonly(self, readonly: bool):
        self.page().runJavaScript(
            f'var editor = ace.edit("editor"); editor.setReadOnly({str(readonly).lower()});'
        )
        self._readonly = readonly

    def readonly(self) -> bool:
        return self._readonly

    def findText(self, subString):
        self.page().runJavaScript(
            f'var editor = ace.edit("editor"); editor.findAll("{str(subString)}");'
        )

    def replaceAll(self, needle: str, replace: str):
        self.page().runJavaScript(
            'var editor = ace.edit("editor");'
            f'editor.replaceAll("{replace}", {{needle: "{needle}"}});'
        )

    def undo(self):
        self.page().runJavaScript(
            'var editor = ace.edit("editor"); editor.undo()'
        )

    def redo(self):
        self.page().runJavaScript(
            'var editor = ace.edit("editor"); editor.redo()'
        )

    def clearSelection(self):
        self.page().runJavaScript(
            'var editor = ace.edit("editor"); editor.selection.clearSelection();'
        )

    @QtCore.Slot(str)
    def _returnText(self, value: str) -> str:
        self._text = value
