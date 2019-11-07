# Copyright 2019 Nicene Nerd <macadamiadaze@gmail.com>
# Licensed under GPLv3+

import glob
import sys
import shutil
import os
import io
import zlib
import platform
import subprocess
import threading
import traceback
import yaml
from pathlib import Path
from typing import Union

import aamp
import aamp.converters
import byml
import byml.yaml_util
import rstb
import sarc
import wszst_yaz0
import xxhash
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from rstb import util

from wildbits.files import *
from wildbits.addrstb import Ui_dlgAddRstb
from wildbits.maingui import Ui_MainWindow
from wildbits.updaterstb import Ui_dlgUpdateRstb

EXEC_DIR = os.path.dirname(os.path.realpath(__file__))

SARC_EXTS = {'*.sarc', '*.pack', '*.bactorpack', '*.bmodelsh', '*.beventpack', '*.stera',
             '*.stats', '*.ssarc', '*.spack', '*.sbactorpack', '*.sbmodelsh', '*.sbeventpack',
             '*.sstera', '*.sstats'}
AAMP_EXTS = {'.bxml', '.sbxml', '.bas', '.sbas', '.baglblm', '.sbaglblm', '.baglccr', '.sbaglccr',
             '.baglclwd', '.sbaglclwd', '.baglcube', '.sbaglcube', '.bagldof', '.sbagldof',
             '.baglenv', '.sbaglenv', '.baglenvset', '.sbaglenvset', '.baglfila', '.sbaglfila',
             '.bagllmap', '.sbagllmap', '.bagllref', '.sbagllref', '.baglmf', '.sbaglmf',
             '.baglshpp', '.sbaglshpp', '.baiprog', '.sbaiprog', '.baslist', '.sbaslist',
             '.bassetting', '.sbassetting', '.batcl', '.sbatcl', '.batcllist', '.sbatcllist',
             '.bawareness', '.sbawareness', '.bawntable', '.sbawntable', '.bbonectrl',
             '.sbbonectrl', '.bchemical', '.sbchemical', '.bchmres', '.sbchmres', '.bdemo',
             '.sbdemo', '.bdgnenv', '.sbdgnenv', '.bdmgparam', '.sbdmgparam', '.bdrop', '.sbdrop',
             '.bgapkginfo', '.sbgapkginfo', '.bgapkglist', '.sbgapkglist', '.bgenv', '.sbgenv',
             '.bglght', '.sbglght', '.bgmsconf', '.sbgmsconf', '.bgparamlist', '.sbgparamlist',
             '.bgsdw', '.sbgsdw', '.bksky', '.sbksky', '.blifecondition', '.sblifecondition',
             '.blod', '.sblod', '.bmodellist', '.sbmodellist', '.bmscdef', '.sbmscdef', '.bmscinfo',
             '.sbmscinfo', '.bnetfp', '.sbnetfp', '.bphyscharcon', '.sbphyscharcon',
             '.bphyscontact', '.sbphyscontact', '.bphysics', '.sbphysics', '.bphyslayer',
             '.sbphyslayer', '.bphysmaterial', '.sbphysmaterial', '.bphyssb', '.sbphyssb',
             '.bphyssubmat', '.sbphyssubmat', '.bptclconf', '.sbptclconf', '.brecipe', '.sbrecipe',
             '.brgbw', '.sbrgbw', '.brgcon', '.sbrgcon', '.brgconfig', '.sbrgconfig',
             '.brgconfiglist', '.sbrgconfiglist', '.bsfbt', '.sbsfbt', '.bsft', '.sbsft', '.bshop',
             '.sbshop', '.bumii', '.sbumii', '.bvege', '.sbvege', '.bactcapt', '.sbactcapt'}
BYML_EXTS = {'.bgdata', '.sbgdata', '.bquestpack', '.sbquestpack', '.byml', '.sbyml', '.mubin',
             '.smubin', '.baischedule', '.sbaischedule', '.baniminfo', '.sbaniminfo', '.bgsvdata',
             '.sbgsvdata'}

def format_bytes(size):
    power = 2**10
    power_idx = 0
    power_labels = {0 : 'bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        power_idx += 1
    print_size = f'{size:.3f}' if power_idx > 0 else str(size)
    return f'{print_size} {power_labels[power_idx]}'

class AddRstbDialog(QtWidgets.QDialog, Ui_dlgAddRstb):
    def __init__(self, wiiu, *args, **kwargs): # pylint: disable=unused-argument
        super(AddRstbDialog, self).__init__()
        self.setupUi(self)
        self.wiiu = wiiu
        self.btnBrowseRstbAdd.clicked.connect(self.BrowseRstbAdd_Clicked)

    def BrowseRstbAdd_Clicked(self):
        file_name = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")[0]
        if file_name:
            self.txtAddRstbFile.setText(file_name)
            size = rstb.SizeCalculator().calculate_file_size(file_name, self.wiiu, False)
            if not size:
                ext = Path(file_name).suffix
                print(ext)
                if ext in {*AAMP_EXTS, '.bfres', '.sbfres'}:
                    guess = QMessageBox.question(
                        self, 'Cannot Calculate',
                        'The resource size for this kind of file cannot be properly calculated. '
                        'Do you want to generate a statistics-based estimate?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    ) == QMessageBox.Yes
                    if guess:
                        if ext in AAMP_EXTS:
                            size = guess_aamp_size(Path(file_name))
                        else:
                            size = guess_bfres_size(Path(file_name))
                else:
                    QMessageBox.warning(
                        self,
                        'Warning',
                        'The resource size for this kind of file cannot be calculated.'
                        'You may need to set it by trial and error.'
                    )
            self.spnAddResBytes.setValue(size)

    def getResult(self):
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return {
                'entry': self.txtAddRstbRes.text(),
                'size': self.spnAddResBytes.value()
            }
        else:
            return False

class UpdateRstbDialog(QtWidgets.QDialog, Ui_dlgUpdateRstb):
    def __init__(self, entry, wiiu, *args, **kwargs): # pylint: disable=unused-argument
        super(UpdateRstbDialog, self).__init__()
        self.setupUi(self)
        self.wiiu = wiiu
        self.label_2.setText(entry)
        self.btnBrowseRstbFile.clicked.connect(self.BrowseRstb_Clicked)

    def BrowseRstb_Clicked(self):
        file_name = QFileDialog.getOpenFileName(self, "Select File", "",
            "All Files (*)")[0]
        if file_name:
            self.txtRstbFile.setText(file_name)
            size = rstb.SizeCalculator().calculate_file_size(file_name, self.wiiu, False)
            if not size:
                ext = Path(file_name).suffix
                print(ext)
                if ext in {*AAMP_EXTS, '.bfres', '.sbfres'}:
                    guess = QMessageBox.question(
                        self, 'Cannot Calculate',
                        'The resource size for this kind of file cannot be properly calculated. '
                        'Do you want to generate a statistics-based estimate?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    ) == QMessageBox.Yes
                    if guess:
                        if ext in AAMP_EXTS:
                            size = guess_aamp_size(Path(file_name))
                        else:
                            size = guess_bfres_size(Path(file_name))
                else:
                    QMessageBox.warning(
                        self,
                        'Warning',
                        'The resource size for this kind of file cannot be calculated.'
                        'You may need to set it by trial and error.'
                    )
            self.spnResBytes.setValue(size)

    def getSizeResult(self):
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return self.spnResBytes.value()
        else:
            return False

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    open_sarc_path = False
    open_rstb_path = False
    open_yaml = {}
    
    rstb_hashes = {}
    game_hashes = {}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.open_sarc: sarc.SARC = None
        self.rstb_calc = rstb.SizeCalculator()
        self.tblRstb.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.treeSarc.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.treeSarc.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeSarc.customContextMenuRequested.connect(self.SarcContextMenu)

        self.btnOpenSarc.clicked.connect(self.OpenSarc_Clicked)
        self.btnNewSarc.clicked.connect(self.NewSarc_Clicked)
        self.btnAddSarc.clicked.connect(self.AddSarc_Clicked)
        self.btnUpdateSarc.clicked.connect(self.UpdateSarc_Clicked)
        self.btnDeleteSarc.clicked.connect(self.DeleteSarc_Clicked)
        self.btnExtSarc.clicked.connect(self.ExtSarc_Clicked)
        self.btnSaveAsSarc.clicked.connect(self.SaveAsSarc_Clicked)
        self.btnSaveSarc.clicked.connect(self.SaveSarc_Clicked)
        self.btnExtractSarc.clicked.connect(self.ExtractSarc_Clicked)
        self.btnCreateSarc.clicked.connect(self.CreateSarc_Clicked)

        self.btnOpenRstb.clicked.connect(self.OpenRstb_Clicked)
        self.btnAddRstb.clicked.connect(self.AddRstb_Clicked)
        self.btnUpdateRstb.clicked.connect(self.UpdateRstb_Clicked)
        self.btnDeleteRstb.clicked.connect(self.DeleteRstb_Clicked)
        self.btnSaveRstb.clicked.connect(self.SaveRstb_Clicked)
        self.btnSaveAsRstb.clicked.connect(self.SaveAsRstb_Clicked)

        self.act_open.triggered.connect(self.OpenYaml)
        self.act_save.triggered.connect(self.SaveYaml)
        self.act_saveas.triggered.connect(self.SaveAsYaml)
        self.act_find.triggered.connect(self.FindYaml)
        self.act_replace.triggered.connect(self.ReplaceYaml)
        self.act_undo.triggered.connect(self.UndoYaml)
        self.act_redo.triggered.connect(self.RedoYaml)

        self.txtFilterRstb.editingFinished.connect(self.FilterRstb)

        self.lblOpen = QtWidgets.QLabel()
        self.lblOpen.setStyleSheet('padding: 4 4')
        self.lblOpen.setText('')
        self.statusbar.addWidget(self.lblOpen)
        self.lblYaml = QtWidgets.QLabel()
        self.lblYaml.setStyleSheet('padding: 4 4')
        self.tabWidget.currentChanged.connect(self.TabWidget_Changed)
        self.TabWidget_Changed()

    def ShowProgress(self, title: str):
        self._progress = QtWidgets.QProgressDialog(
            title, 'Cancel', 0, 0, self,
            flags=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
        )
        self._progress.setWindowTitle('Wild Bits')
        self._progress.show()

    def TabWidget_Changed(self):
        if self.tabWidget.currentIndex() == 0:
            self.lblOpen.setText(self.open_sarc_path if self.open_sarc_path else 'No SARC open')
            try:
                self.statusbar.removeWidget(self.lblYaml)
            except:
                pass
        elif self.tabWidget.currentIndex() == 1:
            self.lblOpen.setText(self.open_rstb_path if self.open_rstb_path else 'No RSTB open')
            self.lblYaml.setText('')
            try:
                self.statusbar.removeWidget(self.lblYaml)
            except:
                pass
        else:
            self.lblOpen.setText(self.open_yaml['path'].as_posix() if 'path' in self.open_yaml \
                                 else 'No file open')
            if 'type' in self.open_yaml:
                self.statusbar.addWidget(self.lblYaml)
                self.lblYaml.setText(self.open_yaml['type'].upper())

    def EnableSarcButtons(self):
        self.btnAddSarc.setEnabled(True)
        self.btnUpdateSarc.setEnabled(True)
        self.btnSaveSarc.setEnabled(True)
        self.btnSaveAsSarc.setEnabled(True)
        self.btnDeleteSarc.setEnabled(True)
        self.btnExtSarc.setEnabled(True)

    def SarcContextMenu(self, pos):
        current_item = self.treeSarc.itemAt(pos)
        if current_item:
            items = self.getSelectedTreeFiles(current_item)
            menu = QtWidgets.QMenu(self)
            act_exp = QtWidgets.QAction('Extract')
            act_exp.triggered.connect(self.ExtSarc_Clicked)
            menu.addAction(act_exp)
            act_del = QtWidgets.QAction('Delete')
            act_del.triggered.connect(self.DeleteSarc_Clicked)
            menu.addAction(act_del)
            if '.' in current_item.toolTip(0):
                sarc_path = Path(items[0])
                if sarc_path.suffix in AAMP_EXTS | BYML_EXTS | {'.msbt'}:
                    act_yaml = QtWidgets.QAction('Open as YAML')
                    act_yaml.triggered.connect(lambda: self.SarcOpenYaml(sarc_path))
                    menu.insertAction(act_exp, act_yaml)
            menu.exec_(self.treeSarc.mapToGlobal(pos))

    def SarcOpenYaml(self, file):
        open_thread = OpenFileThread(Path('SARC:', file), open_sarc=self.open_sarc)
        open_thread.opened.done.connect(self.YamlFileOpened)
        open_thread.start()
        self.ShowProgress(f'Opening {file.name}...')
        self.tabWidget.setCurrentIndex(2)

    def OpenSarc_Clicked(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open RSTB File", "",
            f"SARC Packs ({'; '.join(SARC_EXTS)});;All Files (*)"
        )[0]
        if file_name:
            with open(file_name, 'rb') as sf:
                sf.seek(0)
                magic = sf.read(4)
                if magic == b'Yaz0':
                    self.open_sarc_compressed = True
                elif magic == b'SARC':
                    self.open_sarc_compressed = False
                else:
                    self.open_sarc = False
                self.open_sarc = sarc.read_file_and_make_sarc(sf)
                self.chkBeSarc.setChecked(self.open_sarc._be) # pylint: disable=protected-access
            if not self.open_sarc:
                QMessageBox.critical(
                    self,
                    'Error',
                    'SARC could not be loaded. The file may be invalid, broken, not a SARC, '
                    'or in use.'
                )
                return
            else:
                if self.open_sarc._be and not self.game_hashes: # pylint: disable=protected-access
                    with open(os.path.join(EXEC_DIR, 'hashtable_wiiu'), 'r') as hf:
                        for line in hf.readlines()[1:]:
                            parsed = line.split(',')
                            self.game_hashes[parsed[0]] = parsed[1].strip()
                self.open_sarc_path = file_name
                self.ShowProgress('Opening and Processing SARC...')
                self.LoadSarc()
                self.EnableSarcButtons()
                self.treeSarc.collapseAll()
                self.TabWidget_Changed()

    def NewSarc_Clicked(self):
        new_sarc = sarc.SARCWriter(self.chkBeSarc.isChecked())
        self.open_sarc = sarc.SARC(new_sarc.get_bytes())
        new_sarc = None
        self.LoadSarc()
        self.EnableSarcButtons()

    def AddSarc_Clicked(self):
        file_name = QFileDialog.getOpenFileName(self, "Add File to SARC", "",
            "All Files (*)")[0]
        if file_name:
            add_sarc = sarc.make_writer_from_sarc(self.open_sarc)
            new_path, accepted = QtWidgets.QInputDialog.getText(self, 'Enter File Path:', 
                'Enter the path in the SARC where the new file should be stored:', QtWidgets.QLineEdit.Normal)
            if accepted:
                with open(file_name, 'rb') as af:
                    add_sarc.add_file(new_path, af.read())
                self.open_sarc = None
                self.open_sarc = sarc.SARC(add_sarc.get_bytes())
                self.LoadSarc()

    def UpdateSarc_Clicked(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Update Folder')
        if folder:
            up_sarc = sarc.make_writer_from_sarc(self.open_sarc)
            for item in glob.glob(os.path.join(folder, '*/**'), recursive=True):
                if os.path.isfile(item):
                    canon_path = os.path.relpath(item, folder).replace('\\', '/')
                    if canon_path in self.open_sarc.list_files():
                        up_sarc.delete_file(canon_path)
                    with open(item, 'rb') as uf:
                        up_sarc.add_file(canon_path, uf.read())
            self.open_sarc = sarc.SARC(up_sarc.get_bytes())
            up_sarc = None
            self.LoadSarc()

    def getSelectedTreeFiles(self, item):
        if item.childCount() == 0:
            return [ item.toolTip(0) ]
        else:
            files = []
            for i in range(item.childCount()):
                files.extend(self.getSelectedTreeFiles(item.child(i)))
            return files

    def DeleteSarc_Clicked(self):
        del_files = self.getSelectedTreeFiles(self.treeSarc.selectedItems()[0])
        file_list = '\n'
        file_or_files = 'file' if len(del_files) == 1 else 'files'
        do_delete = (QMessageBox.question(self, 'Confirm Delete', 
            f'Are you sure you want to delete the following {file_or_files} from the SARC?\n\n{file_list.join(del_files)}',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
        if do_delete:
            del_sarc = sarc.make_writer_from_sarc(self.open_sarc)
            for del_file in del_files:
                del_sarc.delete_file(del_file)
            self.open_sarc = sarc.SARC(del_sarc.get_bytes())
            del_sarc = None
            self.LoadSarc()

    def ExtSarc_Clicked(self):
        sel_files = self.getSelectedTreeFiles(self.treeSarc.selectedItems()[0])
        if len(sel_files) == 1:
            save_file = sel_files[0]
            file_name, file_ext = os.path.splitext(save_file)
            should_decompress = False
            if file_ext.startswith('.s') and not file_ext == '.sarc':
                should_decompress = (QMessageBox.question(self, 'Decompress File', 
                    f'It appears that {file_name}{file_ext} may be yaz0 compressed. Do you want to decompress it?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
            file_name = QFileDialog.getSaveFileName(self, 'Extract File To')[0]
            if file_name:
                with open(file_name, 'wb') as wf:
                    save_data = self.open_sarc.get_file_data(save_file)
                    if should_decompress:
                        save_data = wszst_yaz0.decompress(save_data)
                    wf.write(save_data)
        else:
            folder = QFileDialog.getExistingDirectory(self, 'Extract Tree to Folder')
            if folder:
                base_path = self.treeSarc.selectedItems()[0].toolTip(0)
                for ext_file in sel_files:
                    save_path = os.path.join(folder, self.treeSarc.selectedItems()[0].text(0), os.path.relpath(ext_file, base_path))
                    if not os.path.exists(os.path.dirname(save_path)):
                        os.makedirs(os.path.dirname(save_path), exist_ok = True)
                    with open(save_path, 'wb') as wf:
                        wf.write(self.open_sarc.get_file_data(ext_file))

    def SaveSarc_Clicked(self):
        if hasattr(self, 'open_sarc_path'):
            with open(self.open_sarc_path, 'wb') as sf:
                save_sarc = sarc.make_writer_from_sarc(self.open_sarc)
                save_bytes = save_sarc.get_bytes()
                if self.open_sarc_compressed:
                    save_bytes = wszst_yaz0.compress(save_bytes, 3)
                sf.write(save_bytes)
        else:
            self.SaveAsSarc_Clicked()

    def SaveAsSarc_Clicked(self):
        should_compress = (QMessageBox.question(self, 'Compress SARC',
            'Do you want to yaz0 compress this SARC archive?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
        file_name = QFileDialog.getSaveFileName(self, 'Save SARC As', '', "All Files (*)")[0]
        if file_name:
            with open(file_name, 'wb') as sf:
                save_sarc = sarc.make_writer_from_sarc(self.open_sarc)
                save_bytes = save_sarc.get_bytes()
                if should_compress:
                    save_bytes = wszst_yaz0.compress(save_bytes, 3)
                sf.write(save_bytes)
            self.open_sarc_path = file_name
            self.open_sarc_compressed = should_compress

    def LoadSarc(self):
        self.treeSarc.clear()
        self.fill_item(
            self.treeSarc.invisibleRootItem(),
            self.files_to_dict(self.open_sarc.list_files())
        )
        self.ProgressDone()

    def getFullSarcPath(self, item):
        full_path = item.text(0)
        while item.parent() is not None:
            full_path = item.parent().text(0) + '/' + full_path
            item = item.parent()
        return full_path

    def files_to_dict(self, paths):
        split_paths = []
        for path in paths:
            split_paths.append(path.split('/'))
        d = {}
        for path in split_paths:
            current_level = d
            for part in path:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        return d

    def fill_item(self, item, value):
        QtCore.QCoreApplication.instance().processEvents()
        mod_color = QtGui.QColor(255, 255, 141)
        item.setExpanded(True)
        if type(value) is dict:
            child_highlighted = False
            for key, val in sorted(value.items()):
                child = QtWidgets.QTreeWidgetItem()
                child.setText(0, key)
                item.addChild(child)
                self.fill_item(child, val)
                full_path = self.getFullSarcPath(child)
                child.setToolTip(0, full_path)
                if '.' in full_path:
                    try:
                        size = self.open_sarc.get_file_size(full_path)
                        str_size = format_bytes(size)
                        child.setText(1, str_size)
                        child.setToolTip(1, f'{size} bytes')
                        if '.msbt' in full_path:
                            continue
                    except (IndexError, KeyError):
                        pass
                    data = self.open_sarc.get_file_data(full_path).tobytes()
                    canon = full_path.replace('.s', '.')
                    if data[0:4] == b'Yaz0':
                        data = wszst_yaz0.decompress(data)
                    try:
                        mod_hash = xxhash.xxh32(data).hexdigest()
                        stock_hash = self.game_hashes[canon]
                        if mod_hash != stock_hash:
                            child.setBackgroundColor(0, mod_color)
                            child_highlighted = True
                    except (IndexError, KeyError):
                        pass
                    ext = os.path.splitext(canon)[1]
                    rstb_size = self.rstb_calc.calculate_file_size_with_ext(
                        data,
                        True,
                        ext
                    )
                    estimated = False
                    if rstb_size == 0:
                        if ext == '.bfres':
                            rstb_size = guess_bfres_size(data, os.path.basename(canon))
                            estimated = True
                        elif ext in AAMP_EXTS:
                            rstb_size = guess_aamp_size(data, ext)
                            estimated = True
                    child.setText(2, str(rstb_size))
                    if rstb_size == 0:
                        child.setText(2, '')
                        child.setToolTip(2, 'RSTB value could not be calculated')
                    elif estimated:
                        child.setBackgroundColor(2, QtGui.QColor(255, 171, 64))
                        child.setToolTip(2, 'Estimated value')
            if child_highlighted:
                item.setBackgroundColor(0, mod_color)
            QtCore.QCoreApplication.instance().processEvents()
        elif type(value) is list:
            for val in value:
                child = QtWidgets.QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:      
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, val)
                child.setExpanded(True)
        else:
            child = QtWidgets.QTreeWidgetItem()
            child.setText(0, value)
            item.addChild(child)

    def ExtractSarc_Clicked(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open SARC Archive', '',
            f"SARC Packs ({'; '.join(SARC_EXTS)});;All Files (*)")[0]
        if file_name:
            folder = QFileDialog.getExistingDirectory(self, 'Select Extract Folder')
            with open(file_name, 'rb') as rf:
                ex_sarc = sarc.read_file_and_make_sarc(rf)
            if ex_sarc:
                ex_sarc.extract_to_dir(folder)
                if QMessageBox.question(self, 'Extraction Finished',
                    f'Extracting {os.path.basename(file_name)} complete. Do you want to view the extracted contents?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                    if platform.system() == "Windows":
                        subprocess.Popen(["explorer", folder.replace('/','\\')])
                    elif platform.system() == "Darwin":
                        subprocess.Popen(["open", folder])
                    else:
                        subprocess.Popen(["xdg-open", folder])
            else:
                QMessageBox.critical(self, 'Error',
                    'SARC could not be loaded. The file may be invalid, broken, not a SARC, or in use.')

    def CreateSarc_Clicked(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Source Folder for SARC')
        if folder:
            new_sarc = sarc.SARCWriter(QMessageBox.question(self, 'SARC Endianness', 
                'Do you want to create this SARC in big endian (Wii U) format?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
            for item in glob.glob(os.path.join(folder, '*/**'), recursive=True):
                if os.path.isfile(item):
                    canon_path = os.path.relpath(item, folder).replace('\\', '/')
                    with open(item, 'rb') as rf:
                        new_sarc.add_file(canon_path, rf.read())
            should_compress = (QMessageBox.question(self, 'Compress SARC',
                'Do you want to yaz0 compress the new SARC?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
            file_name = QFileDialog.getSaveFileName(self, 'Save SARC')[0]
            if file_name:
                with open(file_name, 'wb') as wf:
                    save_bytes = new_sarc.get_bytes()
                    if should_compress: save_bytes = wszst_yaz0.compress(save_bytes)
                    wf.write(save_bytes)
                QMessageBox.information(self, 'Creation Finished', f'Creating SARC {os.path.split(file_name)[1]} complete!')
                new_sarc = None

    def getSelectedEntries(self):
        file_names = []
        for item in self.tblRstb.selectionModel().selectedRows():
            file_names.append(self.tblRstb.item(item.row(), 0).text().strip())
        return file_names

    def OpenRstb_Clicked(self):
        self.rstb_hashes.clear()
        with open(os.path.join(EXEC_DIR, 'name_hashes'), 'r') as hf:
            for line in hf.readlines():
                parsed = line.split(',')
                self.rstb_hashes[int(parsed[0], 16)] = parsed[1]
        file_name = QFileDialog.getOpenFileName(self, "Open RSTB File", "",
            "Resource Size Table Files (*.rsizetable, *.srsizetable);;All Files (*)")[0]
        if file_name:
            self.open_rstb = util.read_rstb(file_name, False)
            if self.open_rstb.is_in_table('System/Resource/ResourceSizeTable.product.rsizetable'):
                self.open_rstb_path = file_name
                self.rstb_vals = {}
                self.LoadRstb()
            else:
                self.open_rstb = util.read_rstb(file_name, True)
                if self.open_rstb.is_in_table('System/Resource/ResourceSizeTable.product.rsizetable'):
                    self.open_rstb_path = file_name
                    self.chkBeRstb.setChecked(True)
                    self.rstb_vals = {}
                    self.LoadRstb()
                else:
                    corrupt_reply = (QMessageBox.question(self, 'Invalid RSTB?', 
                        'A standard RSTB entry was not found in this file. It could be corrupt. Do you want to continue?', 
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
                    if corrupt_reply:
                        self.open_rstb_path = file_name
                        self.rstb_vals = {}
                        self.LoadRstb()
            if self.open_rstb:
                self.btnAddRstb.setEnabled(True)
                self.btnUpdateRstb.setEnabled(True)
                self.btnDeleteRstb.setEnabled(True)
                self.btnSaveRstb.setEnabled(True)
                self.btnSaveAsRstb.setEnabled(True)
                self.TabWidget_Changed()

    def AddRstb_Clicked(self):
        dlg = AddRstbDialog(self.chkBeRstb.isChecked())
        result = dlg.getResult()
        if result is not False:
            self.open_rstb.set_size(result['entry'], result['size'])
            hash = zlib.crc32(result['entry'].encode('utf8'))
            self.rstb_hashes[hash] = result['entry']
            with open(os.path.join(EXEC_DIR, './wildbits/name_hashes'), 'a') as hf:
                hf.write(f'{hash},{result["entry"]}')
            self.LoadRstb()

    def UpdateRstb_Clicked(self):
        for entry in self.getSelectedEntries():    
            dlg = UpdateRstbDialog(entry, self.chkBeRstb.isChecked())
            size = dlg.getSizeResult()
            if size is not False:
                self.open_rstb.set_size(entry, size)
        self.LoadRstb()

    def DeleteRstb_Clicked(self):
        file_names = self.getSelectedEntries()
        item_or_items = 'entries' if len(file_names) > 1 else 'entry'
        entries = '\n'
        do_delete = (QMessageBox.question(self, 'Confirm Delete',
            f'Are you sure you want to remove the following {item_or_items} from the RSTB?\n\n{entries.join(file_names)}',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
        if not do_delete: return
        for file_name in file_names:
            self.open_rstb.delete_entry(file_name)
        self.LoadRstb()

    def SaveRstb_Clicked(self):
        util.write_rstb(self.open_rstb, self.open_rstb_path, self.chkBeRstb.isChecked())

    def SaveAsRstb_Clicked(self):
        file_name = QFileDialog.getSaveFileName(self,"Save RSTB As","",
            "Resource Size Table Files (*.rsizetable, *.srsizetable);;All Files (*)")[0]
        if file_name:
            util.write_rstb(self.open_rstb, file_name, self.chkBeRstb.isChecked())
            self.open_rstb_path = file_name
    
    def LoadRstb(self):
        self.rstb_vals.clear()
        uki = 1
        for entry in self.open_rstb.crc32_map:
            if entry in self.rstb_hashes:
                name_key = self.rstb_hashes[entry]
            else:
                name_key = f'Unknown file {uki}'
                uki += 1
            self.rstb_vals[name_key] = {
                'hash': f'{entry:#0{10}x}',
                'size': f'{self.open_rstb.crc32_map[entry]} bytes'
            }
        self.tblRstb.setUpdatesEnabled(False)
        self.tblRstb.setRowCount(len(self.rstb_vals))
        for i, entry in enumerate(self.rstb_vals):
            self.tblRstb.setItem(i, 0,  QTableWidgetItem(entry))
            self.tblRstb.setItem(i, 1,  QTableWidgetItem(self.rstb_vals[entry]['hash']))
            self.tblRstb.setItem(i, 2,  QTableWidgetItem(self.rstb_vals[entry]['size']))
        self.tblRstb.setUpdatesEnabled(True)

    def FilterRstb(self):
        filter = self.txtFilterRstb.text()
        if len(filter) < 1:
            if not self.nope: self.LoadRstb()
            self.nope = True
            return
        self.nope = False
        self.tblRstb.setUpdatesEnabled(False)
        filtered_entries = { k: v for k, v in self.rstb_vals.items() if filter.lower() in k.lower() }
        self.tblRstb.setRowCount(len(filtered_entries))
        for i, entry in enumerate(filtered_entries):
            self.tblRstb.setItem(i, 0, QTableWidgetItem(entry))
            self.tblRstb.setItem(i, 1, QTableWidgetItem(self.rstb_vals[entry]['hash']))
            self.tblRstb.setItem(i, 2, QTableWidgetItem(self.rstb_vals[entry]['size']))
        self.tblRstb.setUpdatesEnabled(True)

    def ProgressDone(self):
        if self._progress:
            self._progress.close()
        self._progress = None
        self.TabWidget_Changed()

    def YamlFileOpened(self, open_info: dict):
        if 'error' in open_info:
            QMessageBox.warning(
                self, 'Error', 'You did not select a valid AAMP, BYML, or MSBT file.'
            )
        else:
            self.open_yaml = open_info
            self.yaml_editor.setText(open_info['text'])
            self.yaml_editor.setReadonly(False)
            self.yaml_editor.clearSelection()
            self.act_save.setEnabled(True)
            self.act_saveas.setEnabled(True)
            self.act_find.setEnabled(True)
            self.act_replace.setEnabled(True)
            self.act_undo.setEnabled(True)
            self.act_redo.setEnabled(True)
            if open_info['path'].parts[0] == 'SARC:':
                self.LoadSarc()
        self.ProgressDone()

    def OpenYaml(self):
        aamp_exts = ';'.join([f'*{ext}' for ext in AAMP_EXTS])
        byml_exts = ';'.join([f'*{ext}' for ext in BYML_EXTS])
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open File", "",
            ';;'.join([
                f'AAMP Files ({aamp_exts})',
                f'BYML Files ({byml_exts})',
                'MSBT Files (*.msbt)',
                'All Files (*)'
            ]))[0]
        if file_name:
            file_name = Path(file_name)
            open_thread = OpenFileThread(file_name)
            open_thread.opened.done.connect(self.YamlFileOpened)
            open_thread.start()
            self.ShowProgress(f'Opening {file_name.name}...')

    def SaveYaml(self):
        be = False
        if 'be' in self.open_yaml:
            be = self.open_yaml['be']
        if self.open_yaml['type'] == 'msbt':
            platform, okay = QtWidgets.QInputDialog.getItem(
                self,
                'MSBT Format',
                'Select the format for the MSBT file\n(this cannot be automatically determined)',
                ['Wii U', 'Switch'],
                0,
                False,
                flags=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
            )
            if not okay:
                return
        else:
            platform = ''
        self.ShowProgress(f'Saving {self.open_yaml["path"].name}...')
        save_thread = SaveFileThread(
            self.open_yaml['path'],
            self.yaml_editor.text(),
            self,
            be,
            platform
        )
        save_thread.saved.done.connect(self.YamlFileOpened)
        save_thread.saved.error.connect(lambda error: QMessageBox.warning(self, 'Error', error))
        save_thread.start()

    def SaveAsYaml(self):
        be = False
        if 'be' in self.open_yaml:
            be = self.open_yaml['be']
        if self.open_yaml['type'] == 'msbt':
            platform, okay = QtWidgets.QInputDialog.getItem(
                self,
                'MSBT Format',
                'Select the format for the MSBT file\n(this cannot be automatically determined)',
                ['Wii U', 'Switch'],
                0,
                False,
                flags=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
            )
            if not okay:
                return
        else:
            platform = ''
        aamp_exts = ';'.join([f'*{ext}' for ext in AAMP_EXTS])
        byml_exts = ';'.join([f'*{ext}' for ext in BYML_EXTS])
        if self.open_yaml['type'] == 'aamp':
            exts = f'AAMP Files ({aamp_exts})'
        elif self.open_yaml['type'] == 'byml':
            exts = f'BYML Files ({byml_exts})'
        else:
            exts = 'MSBT Files (*.msbt)'
        file_name = QFileDialog.getSaveFileName(self, 'Save File As', '', exts)[0]
        if file_name:
            save_thread = SaveFileThread(
                Path(file_name),
                self.yaml_editor.text(),
                self,
                be,
                platform
            )
            save_thread.saved.done.connect(self.YamlFileOpened)
            #save_thread.saved.error.connect(lambda error: QMessageBox.warning(self, 'Error', error))
            save_thread.start()
            self.ShowProgress(f'Saving {self.open_yaml["path"].name}...')

    def FindYaml(self):
        find_name, okay = QtWidgets.QInputDialog.getText(
            self,
            'Find Text',
            'Enter the text you want to find',
            QtWidgets.QLineEdit.Normal,
            '',
            flags=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint
        )
        if okay:
            self.yaml_editor.findText(find_name)

    def ReplaceYaml(self):
        result = ReplaceDialog(self).getFindReplace()
        if result:
            self.yaml_editor.replaceAll(result[0], result[1])

    def UndoYaml(self):
        self.yaml_editor.undo()

    def RedoYaml(self):
        self.yaml_editor.redo()


class ReplaceDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent, f=QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle('Find and Replace')
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.lbl_find = QtWidgets.QLabel('Find this:', parent=self)
        self.vlayout.addWidget(self.lbl_find)
        self.txt_find = QtWidgets.QLineEdit('', parent=self)
        self.vlayout.addWidget(self.txt_find)
        self.lbl_replace = QtWidgets.QLabel('Replace with:', parent=self)
        self.vlayout.addWidget(self.lbl_replace)
        self.txt_replace = QtWidgets.QLineEdit('', parent=self)
        self.vlayout.addWidget(self.txt_replace)
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.vlayout.addWidget(self.button_box)
        self.setLayout(self.vlayout)

        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("rejected()"), self.reject)

    def getFindReplace(self) -> (str, str):
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return self.txt_find.text(), self.txt_replace.text()
        else:
            return None


class OpenFileThread(threading.Thread, QtCore.QObject):

    def __init__(self, file: Path, open_sarc: sarc.SARC = None):
        threading.Thread.__init__(self)
        self._file = file
        self._sarc = open_sarc
        self.opened = ThreadSignal()

    def run(self):
        if self._file.parts[0] == 'SARC:':
            file = Path(*self._file.parts[1:])
        if self._file.suffix in AAMP_EXTS:
            self.opened.done.emit({
                'path': self._file,
                'type': 'aamp',
                'text': open_aamp(self._file) if not self._sarc \
                        else open_aamp(
                            self._sarc.get_file_data(file.as_posix()).tobytes()
                        )
            })
        elif self._file.suffix in BYML_EXTS:
            text, be = open_byml(self._file) if not self._sarc \
                       else open_byml(
                           self._sarc.get_file_data(file.as_posix()).tobytes()
                        )
            self.opened.done.emit({
                'path': self._file,
                'type': 'byml',
                'be': be,
                'text': text
            })
        elif self._file.suffix.lower() == '.msbt':
            self.opened.done.emit({
                'path': self._file,
                'type': 'msbt',
                'text': open_msbt(self._file) if not self._sarc \
                        else open_msbt(
                            self._sarc.get_file_data(file.as_posix()).tobytes()
                        )
            })
        else:
            self.opened.done.emit({
                'error': f'{self._file.name} is not a BYML, AAMP, or MSBT file.'
            })


class SaveFileThread(threading.Thread, QtCore.QObject):

    def __init__(self, file: Path, contents: str, parent, byml_big_endian: bool = True,
                 msbt_platform: str = ''):
        threading.Thread.__init__(self)
        self._file = file
        self._contents = contents
        self._be = byml_big_endian
        self._parent: MainWindow = parent
        self._platform = msbt_platform
        self.saved = ThreadSignal()

    def update_sarc(self, data: bytes):
        file = Path(*self._file.parts[1:]).as_posix()
        new_sarc = sarc.make_writer_from_sarc(self._parent.open_sarc)
        new_sarc.delete_file(file)
        new_sarc.add_file(file, data)
        self._parent.open_sarc = sarc.SARC(new_sarc.get_bytes())
        del new_sarc

    def run(self):
        if self._file.suffix in AAMP_EXTS:
            try:
                save_bytes = save_aamp(self._contents)
                if self._file.suffix.startswith('s'):
                    save_bytes = libyaz0.compress(self._file, level=10)
                if self._file.parts[0] != 'SARC:':
                    self._file.write_bytes(save_bytes)
                else:
                    self.update_sarc(save_bytes)
                self.saved.done.emit({
                    'path': self._file,
                    'type': 'aamp',
                    'text': self._contents.replace('\\', '\\\\')
                })
            except:
                self.saved.error.emit(
                    f'There was an error saving {self._file.name} as an AAMP file. Error details: '
                    f'\n\n{traceback.format_exc(limit=-4)}'
                )
        elif self._file.suffix in BYML_EXTS:
            try:
                save_bytes = save_byml(self._contents)
                if self._file.suffix.startswith('s'):
                    save_bytes = libyaz0.compress(self._file, level=10)
                if self._file.parts[0] != 'SARC:':
                    self._file.write_bytes(save_bytes)
                else:
                    self.update_sarc(save_bytes)
                self.saved.done.emit({
                    'path': self._file,
                    'type': 'byml',
                    'be': self._be,
                    'text': self._contents.replace('\\','\\\\')
                })
            except:
                self.saved.error.emit(
                    f'There was an error saving {self._file.name} as a BYML file. Error details: '
                    f'\n\n{traceback.format_exc(limit=-4)}'
                )
        elif self._file.suffix.lower() == '.msbt':
            try:
                if self._file.parts[0] != 'SARC:':
                    save_msbt(
                        self._contents,
                        self._file,
                        platform=self._platform.replace(' ', '').lower()
                    )
                else:
                    tmp = tempfile.NamedTemporaryFile('r', suffix='.msbt', delete=False)
                    tmp_path = Path(tmp.name)
                    tmp.close()
                    tmp_path.unlink()
                    save_msbt(
                        self._contents,
                        tmp_path,
                        platform=self._platform.replace(' ', '').lower()
                    )
                    tmp_bytes = tmp_path.read_bytes()
                    self.update_sarc(tmp_bytes)
                self.saved.done.emit({
                    'path': self._file,
                    'type': 'msbt',
                    'text': self._contents.replace('\\', '\\\\')
                })
            except:
                self.saved.error.emit(
                    f'There was an error saving {self._file.name} as an MSBT file. Error details: '
                    f'\n\n{traceback.format_exc(limit=-4)}'
                )


class ThreadSignal(QtCore.QObject):
    done = QtCore.Signal(dict)
    error = QtCore.Signal(str)


def guess_bfres_size(file: Union[Path, bytes], name: str = '') -> int:
    """
    Attempts to estimate a proper RSTB value for a BFRES file
    :param file: The file to estimate, either as a path or bytes
    :type file: Union[:class:`pathlib.Path`, bytes]
    :param name: The name of the file, needed when passing as bytes, defaults to ''
    :type name: str, optional
    :return: Returns an estimated RSTB value
    :rtype: int
    """
    real_bytes = file if isinstance(file, bytes) else file.read_bytes()
    if real_bytes[0:4] == b'Yaz0':
        real_bytes = wszst_yaz0.decompress(real_bytes)
    real_size = len(real_bytes)
    del real_bytes
    if name == '':
        if isinstance(file, Path):
            name = file.name
        else:
            raise ValueError('BFRES name must not be blank if passing file as bytes.')
    if '.Tex' in name:
        if real_size < 100:
            return real_size * 9
        elif 100 < real_size <= 2000:
            return real_size * 7
        elif 2000 < real_size <= 3000:
            return real_size * 5
        elif 3000 < real_size <= 4000:
            return real_size * 4
        elif 4000 < real_size <= 8500:
            return real_size * 3
        elif 8500 < real_size <= 12000:
            return real_size * 2
        elif 12000 < real_size <= 17000:
            return int(real_size * 1.75)
        elif 17000 < real_size <= 30000:
            return int(real_size * 1.5)
        elif 30000 < real_size <= 45000:
            return int(real_size * 1.3)
        elif 45000 < real_size <= 100000:
            return int(real_size * 1.2)
        elif 100000 < real_size <= 150000:
            return int(real_size * 1.1)
        elif 150000 < real_size <= 200000:
            return int(real_size * 1.07)
        elif 200000 < real_size <= 250000:
            return int(real_size * 1.045)
        elif 250000 < real_size <= 300000:
            return int(real_size * 1.035)
        elif 300000 < real_size <= 600000:
            return int(real_size * 1.03)
        elif 600000 < real_size <= 1000000:
            return int(real_size * 1.015)
        elif 1000000 < real_size <= 1800000:
            return int(real_size * 1.009)
        elif 1800000 < real_size <= 4500000:
            return int(real_size * 1.005)
        elif 4500000 < real_size <= 6000000:
            return int(real_size * 1.002)
        else:
            return int(real_size * 1.0015)
    else:
        if real_size < 500:
            return real_size * 7
        elif 500 < real_size <= 750:
            return real_size * 4
        elif 750 < real_size <= 2000:
            return real_size * 3
        elif 2000 < real_size <= 400000:
            return int(real_size * 1.75)
        elif 400000 < real_size <= 600000:
            return int(real_size * 1.7)
        elif 600000 < real_size <= 1500000:
            return int(real_size * 1.6)
        elif 1500000 < real_size <= 3000000:
            return int(real_size * 1.5)
        else:
            return int(real_size * 1.25)


def guess_aamp_size(file: Union[Path, bytes], ext: str = '') -> int:
    """
    Attempts to estimate a proper RSTB value for an AAMP file. Will only attempt for the following
    kinds: .baiprog, .bgparamlist, .bdrop, .bshop, .bxml, .brecipe, otherwise will return 0.
    :param file: The file to estimate, either as a path or bytes
    :type file: Union[:class:`pathlib.Path`, bytes]
    :param name: The name of the file, needed when passing as bytes, defaults to ''
    :type name: str, optional
    :return: Returns an estimated RSTB value
    :rtype: int"""
    real_bytes = file if isinstance(file, bytes) else file.read_bytes()
    if real_bytes[0:4] == b'Yaz0':
        real_bytes = wszst_yaz0.decompress(real_bytes)
    real_size = len(real_bytes)
    del real_bytes
    if ext == '':
        if isinstance(file, Path):
            ext = file.suffix
        else:
            raise ValueError(
                'AAMP extension must not be blank if passing file as bytes.')
    ext = ext.replace('.s', '.')
    if ext == '.baiprog':
        if real_size <= 380:
            return real_size * 7
        elif 380 < real_size <= 400:
            return real_size * 6
        elif 400 < real_size <= 450:
            return int(real_size * 5.5)
        elif 450 < real_size <= 600:
            return real_size * 5
        elif 600 < real_size <= 1000:
            return real_size * 4
        elif 1000 < real_size <= 1750:
            return int(real_size * 3.5)
        else:
            return real_size * 3
    elif ext == '.bgparamlist':
        if real_size <= 100:
            return real_size * 20
        elif 100 < real_size <= 150:
            return real_size * 12
        elif 150 < real_size <= 250:
            return real_size * 10
        elif 250 < real_size <= 350:
            return real_size * 8
        elif 350 < real_size <= 450:
            return real_size * 7
        else:
            return real_size * 6
    elif ext == '.bdrop':
        if real_size < 200:
            return int(real_size * 8.5)
        elif 200 < real_size <= 250:
            return real_size * 7
        elif 250 < real_size <= 350:
            return real_size * 6
        elif 350 < real_size <= 450:
            return int(real_size * 5.25)
        elif 450 < real_size <= 850:
            return int(real_size * 4.5)
        else:
            return real_size * 4
    elif ext == '.bxml':
        if real_size < 350:
            return real_size * 6
        elif 350 < real_size <= 450:
            return real_size * 5
        elif 450 < real_size <= 550:
            return int(real_size * 4.5)
        elif 550 < real_size <= 650:
            return real_size * 4
        elif 650 < real_size <= 800:
            return int(real_size * 3.5)
        else:
            return real_size * 3
    elif ext == '.brecipe':
        if real_size < 100:
            return int(real_size * 12.5)
        elif 100 < real_size <= 160:
            return int(real_size * 8.5)
        elif 160 < real_size <= 200:
            return int(real_size * 7.5)
        elif 200 < real_size <= 215:
            return real_size * 7
        else:
            return int(real_size * 6.5)
    elif ext == '.bshop':
        if real_size < 200:
            return int(real_size * 7.25)
        elif 200 < real_size <= 400:
            return real_size * 6
        elif 400 < real_size <= 500:
            return real_size * 5
        else:
            return int(real_size * 4.05)
    elif ext == '.bas':
        if real_size < 100:
            return real_size * 20
        elif 100 < real_size <= 200:
            return int(real_size * 12.5)
        elif 200 < real_size <= 300:
            return real_size * 10
        elif 300 < real_size <= 600:
            return real_size * 8
        elif 600 < real_size <= 1500:
            return real_size * 6
        elif 1500 < real_size <= 2000:
            return int(real_size * 5.5)
        elif 2000 < real_size <= 15000:
            return real_size * 5
        else:
            return int(real_size * 4.5)
    elif ext == '.baslist':
        if real_size < 100:
            return real_size * 15
        elif 100 < real_size <= 200:
            return real_size * 10
        elif 200 < real_size <= 300:
            return real_size * 8
        elif 300 < real_size <= 500:
            return real_size * 6
        elif 500 < real_size <= 800:
            return real_size * 5
        elif 800 < real_size <= 4000:
            return real_size * 4
        else:
            return int(real_size * 3.5)
    else:
        return 0


def main():
    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()