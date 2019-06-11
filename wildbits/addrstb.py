# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\addrstb.ui',
# licensing of '.\addrstb.ui' applies.
#
# Created: Mon Jun 10 06:08:28 2019
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_dlgAddRstb(object):
    def setupUi(self, dlgAddRstb):
        dlgAddRstb.setObjectName("dlgAddRstb")
        dlgAddRstb.resize(400, 163)
        self.gridLayout = QtWidgets.QGridLayout(dlgAddRstb)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(dlgAddRstb)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.txtAddRstbRes = QtWidgets.QLineEdit(dlgAddRstb)
        self.txtAddRstbRes.setObjectName("txtAddRstbRes")
        self.verticalLayout.addWidget(self.txtAddRstbRes)
        self.label = QtWidgets.QLabel(dlgAddRstb)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(dlgAddRstb)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.spnAddResBytes = QtWidgets.QSpinBox(dlgAddRstb)
        self.spnAddResBytes.setMaximum(999999999)
        self.spnAddResBytes.setObjectName("spnAddResBytes")
        self.horizontalLayout.addWidget(self.spnAddResBytes)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(dlgAddRstb)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.txtAddRstbFile = QtWidgets.QLineEdit(dlgAddRstb)
        self.txtAddRstbFile.setReadOnly(True)
        self.txtAddRstbFile.setObjectName("txtAddRstbFile")
        self.horizontalLayout_2.addWidget(self.txtAddRstbFile)
        self.btnBrowseRstbAdd = QtWidgets.QPushButton(dlgAddRstb)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowseRstbAdd.sizePolicy().hasHeightForWidth())
        self.btnBrowseRstbAdd.setSizePolicy(sizePolicy)
        self.btnBrowseRstbAdd.setStyleSheet("padding: 2 8")
        self.btnBrowseRstbAdd.setObjectName("btnBrowseRstbAdd")
        self.horizontalLayout_2.addWidget(self.btnBrowseRstbAdd)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgAddRstb)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlgAddRstb)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dlgAddRstb.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dlgAddRstb.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgAddRstb)

    def retranslateUi(self, dlgAddRstb):
        dlgAddRstb.setWindowTitle(QtWidgets.QApplication.translate("dlgAddRstb", "Add RSTB Entry", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("dlgAddRstb", "Enter the canonical path of the new resource:", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("dlgAddRstb", "Enter size for the new resource entry:", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("dlgAddRstb", "Size in Bytes: ", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("dlgAddRstb", "Detect size from file:", None, -1))
        self.btnBrowseRstbAdd.setText(QtWidgets.QApplication.translate("dlgAddRstb", "Browse...", None, -1))

