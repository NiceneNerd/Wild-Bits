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

from wildbits.addrstb import Ui_dlgAddRstb
from wildbits.maingui import Ui_MainWindow
from wildbits.updaterstb import Ui_dlgUpdateRstb

rstb_hashes = {}
game_hashes = {}
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))

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
    def __init__(self, wiiu, *args, **kwargs):
        super(AddRstbDialog, self).__init__()
        self.setupUi(self)
        self.wiiu = wiiu
        self.btnBrowseRstbAdd.clicked.connect(self.BrowseRstbAdd_Clicked)

    def BrowseRstbAdd_Clicked(self):
        file_name = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")[0]
        if file_name:
            self.txtAddRstbFile.setText(file_name)
            size = rstb.SizeCalculator().calculate_file_size(file_name, self.wiiu, False)
            if size == 0:
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
    def __init__(self, entry, wiiu, *args, **kwargs):
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
            if size == 0:
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

    open_sarc_path = False
    open_rstb_path = False
    open_yaml_path = False

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.open_sarc: sarc.SARC = None
        self.rstb_calc = rstb.SizeCalculator()
        self.tblRstb.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.treeSarc.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

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

        self.btnNewYaml.clicked.connect(self.NewYaml_Clicked)
        self.btnOpenYaml.clicked.connect(self.OpenYaml_Clicked)
        self.btnYamlEditor.clicked.connect(self.YamlEditor_Clicked)
        self.btnExportYaml.clicked.connect(self.ExportYaml_Clicked)
        self.btnSaveYaml.clicked.connect(self.SaveYaml_Clicked)
        self.btnSaveAsYaml.clicked.connect(self.SaveAsYaml_Clicked)

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
        self._progress = QtWidgets.QProgressDialog(title, 'Cancel', 0, 0, self)
        self._progress.show()

    def TabWidget_Changed(self):
        if self.tabWidget.currentIndex() == 0:
            self.lblOpen.setText(self.open_sarc_path if self.open_sarc_path else 'No SARC open')
            try: self.statusbar.removeWidget(self.lblYaml)
            except: pass
        elif self.tabWidget.currentIndex() == 1:
            self.lblOpen.setText(self.open_rstb_path if self.open_rstb_path else 'No RSTB open')
            self.lblYaml.setText('')
            try: self.statusbar.removeWidget(self.lblYaml)
            except: pass
        else:
            self.lblOpen.setText(self.open_yaml_path if self.open_yaml_path \
                                 else 'No AAMP or BYAML open')
            self.statusbar.addWidget(self.lblYaml)
            if hasattr(self, 'open_yaml'): self.lblYaml.setText(self.open_yaml.upper())

    def EnableSarcButtons(self):
        self.btnAddSarc.setEnabled(True)
        self.btnUpdateSarc.setEnabled(True)
        self.btnSaveSarc.setEnabled(True)
        self.btnSaveAsSarc.setEnabled(True)
        self.btnDeleteSarc.setEnabled(True)
        self.btnExtSarc.setEnabled(True)

    def OpenSarc_Clicked(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open RSTB File", "",
            f"SARC Packs ({'; '.join(self.SARC_EXTS)});;All Files (*)"
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
                self.chkBeSarc.setChecked(self.open_sarc._be)
            if not self.open_sarc:
                QMessageBox.critical(
                    self,
                    'Error',
                    'SARC could not be loaded. The file may be invalid, broken, not a SARC, '
                    'or in use.'
                )
                return
            else:
                if self.open_sarc._be and not game_hashes:
                    with open(os.path.join(EXEC_DIR, 'hashtable_wiiu'), 'r') as hf:
                        for line in hf.readlines()[1:]:
                            parsed = line.split(',')
                            game_hashes[parsed[0]] = parsed[1].strip()
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
        self._progress.close()
        self._progress = None

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
                    except (IndexError, KeyError):
                        pass
                    data = self.open_sarc.get_file_data(full_path).tobytes()
                    canon = full_path.replace('.s', '.')
                    if data[0:4] == b'Yaz0':
                        data = wszst_yaz0.decompress(data)
                    try:
                        mod_hash = xxhash.xxh32(data).hexdigest()
                        stock_hash = game_hashes[canon]
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
                        elif ext in self.AAMP_EXTS:
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
            f"SARC Packs ({'; '.join(self.SARC_EXTS)});;All Files (*)")[0]
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
        rstb_hashes.clear()
        with open(os.path.join(EXEC_DIR, 'name_hashes'), 'r') as hf:
            for line in hf.readlines():
                parsed = line.split(',')
                rstb_hashes[int(parsed[0], 16)] = parsed[1]
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
            rstb_hashes[hash] = result['entry']
            with open(os.path.join(EXEC_DIR,'./wildbits/name_hashes'), 'a') as hf:
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
            if entry in rstb_hashes:
                name_key = rstb_hashes[entry]
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
            self.tblRstb.setItem(i, 0,  QTableWidgetItem(entry))
            self.tblRstb.setItem(i, 1,  QTableWidgetItem(self.rstb_vals[entry]['hash']))
            self.tblRstb.setItem(i, 2,  QTableWidgetItem(self.rstb_vals[entry]['size']))
        self.tblRstb.setUpdatesEnabled(True)

    def EnableYamlButtons(self):
        self.btnYamlEditor.setEnabled(True)
        self.btnExportYaml.setEnabled(True)
        self.btnSaveYaml.setEnabled(True)
        self.btnSaveAsYaml.setEnabled(True)
        self.txtRstbYaml.setEnabled(True)
        self.txtYaml.setEnabled(True)

    def NewYaml_Clicked(self):
        self.open_yaml = ''
        self.open_yaml_path = ''
        self.txtYaml.setText('')
        self.EnableYamlButtons()

    def OpenYaml_Clicked(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open BYAML or AAMP File')[0]
        if file_name:
            self.open_yaml_path = file_name
            with open(file_name, 'rb') as rf:
                input_data = rf.read()
            if input_data[0:4] == b'Yaz0':
                input_data = wszst_yaz0.decompress(input_data)
                self.yaml_compressed = True
            if input_data[0:8] == b'AAMP\x02\x00\x00\x00':
                self.txtYaml.setText(aamp.converters.aamp_to_yml(input_data).decode('utf-8'))
                self.open_yaml = 'aamp'
                self.EnableYamlButtons()
                self.chkBeYaml.setEnabled(False)
            elif input_data[0:2] == b'BY' or input_data[0:2] == b'YB':
                open_byml = byml.Byml(input_data)
                self.chkBeYaml.setChecked(open_byml._be)
                dumper = yaml.CDumper
                byml.yaml_util.add_representers(dumper)
                self.open_yaml = 'byml'
                dumped = yaml.dump(open_byml.parse(), Dumper=dumper, allow_unicode=True, encoding='utf-8').decode('utf-8')
                self.txtYaml.setText(dumped)
                self.txtRstbYaml.setText(str(self.rstb_calc.calculate_file_size(file_name, open_byml._be, False)))
                self.EnableYamlButtons()
                self.TabWidget_Changed()
    
    def YamlEditor_Clicked(self):
        import tempfile
        with tempfile.NamedTemporaryFile('w',suffix='.yml',encoding='utf-8',delete=False) as temp:
            self.temp_yaml = temp.name
            temp.write(self.txtYaml.toPlainText())
        self.temp_watcher = QtCore.QFileSystemWatcher([self.temp_yaml])
        self.temp_watcher.fileChanged.connect(self.TempFile_Changed)
        import webbrowser
        webbrowser.open(self.temp_yaml)

    def TempFile_Changed(self):
        with open(self.temp_yaml, 'r') as temp:
            self.txtYaml.setText(temp.read())
        if self.open_yaml == 'byml':
            self.save_yaml_file(self.temp_yaml + '.byaml', False)
            self.txtRstbYaml.setText(str(self.rstb_calc.calculate_file_size(self.temp_yaml + '.byaml', self.chkBeYaml.isChecked(), False)))

    def ExportYaml_Clicked(self):
        file_name = QFileDialog.getSaveFileName(self, 'Export YAML', '' ,'YAML File (*.yml; *.yaml);;All Files (*)')[0]
        if file_name:
            with open(file_name, 'w') as sf:
                sf.write(self.txtYaml.toPlainText())

    def SaveYaml_Clicked(self):
        if self.open_yaml_path == '' or self.open_yaml == '':
            self.SaveAsYaml_Clicked()
        if self.open_yaml == 'aamp':
            with open(self.open_yaml_path, 'wb') as sf:
                sf.write(aamp.converters.yml_to_aamp(self.txtYaml.toPlainText().encode('utf-8')))
        elif self.open_yaml == 'byml':
            self.save_yaml_file(self.open_yaml_path, self.yaml_compressed)
            self.txtRstbYaml.setText(str(self.rstb_calc.calculate_file_size(self.open_yaml_path, 
                self.chkBeYaml.isChecked(), False)))

    def SaveAsYaml_Clicked(self):
        qbox = QMessageBox()
        qbox.setWindowTitle('Choose Save Format')
        qbox.setText('Do you want to save this YAML document as an AAMP or a BYAML file?')
        btnAamp = qbox.addButton('AAMP', QMessageBox.YesRole)
        btnByml = qbox.addButton('BYAML', QMessageBox.NoRole)
        qbox.setIcon(QMessageBox.Question)
        qbox.exec_()
        
        file_name = QFileDialog.getSaveFileName(self, 'Save File As')[0]
        if file_name:
            if qbox.clickedButton() == btnAamp:
                with open(file_name, 'wb') as sf:
                    sf.write(aamp.converters.yml_to_aamp(self.txtYaml.toPlainText().encode('utf-8')))
                self.open_yaml = 'aamp'
            else:
                should_compress = (QMessageBox.question(self, 'Compress SARC',
                    'Do you want to yaz0 compress this BYAML file?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes)
                self.save_yaml_file(file_name, should_compress)
                self.open_yaml = 'byml'
                self.yaml_compressed = should_compress
            self.open_yaml_path = file_name

    def save_yaml_file(self, path, compress):
        loader = yaml.CSafeLoader
        byml.yaml_util.add_constructors(loader)
        root = yaml.load(self.txtYaml.toPlainText(), Loader=loader)
        buf = io.BytesIO()
        byml.Writer(root, self.chkBeYaml.isChecked()).write(buf)
        buf.seek(0)
        if compress:
            buf = io.BytesIO(wszst_yaz0.compress(buf.read()))
        with open(path, 'wb') as sf:
            shutil.copyfileobj(buf, sf)


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