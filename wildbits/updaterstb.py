# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\updaterstb.ui',
# licensing of '.\updaterstb.ui' applies.
#
# Created: Mon Jun 10 06:09:30 2019
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_dlgUpdateRstb(object):
    def setupUi(self, dlgUpdateRstb):
        dlgUpdateRstb.setObjectName("dlgUpdateRstb")
        dlgUpdateRstb.resize(400, 137)
        self.gridLayout = QtWidgets.QGridLayout(dlgUpdateRstb)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(dlgUpdateRstb)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(dlgUpdateRstb)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(dlgUpdateRstb)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.spnResBytes = QtWidgets.QSpinBox(dlgUpdateRstb)
        self.spnResBytes.setMaximum(999999999)
        self.spnResBytes.setObjectName("spnResBytes")
        self.horizontalLayout.addWidget(self.spnResBytes)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(dlgUpdateRstb)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.txtRstbFile = QtWidgets.QLineEdit(dlgUpdateRstb)
        self.txtRstbFile.setReadOnly(True)
        self.txtRstbFile.setObjectName("txtRstbFile")
        self.horizontalLayout_2.addWidget(self.txtRstbFile)
        self.btnBrowseRstbFile = QtWidgets.QPushButton(dlgUpdateRstb)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBrowseRstbFile.sizePolicy().hasHeightForWidth())
        self.btnBrowseRstbFile.setSizePolicy(sizePolicy)
        self.btnBrowseRstbFile.setStyleSheet("padding: 2 8")
        self.btnBrowseRstbFile.setObjectName("btnBrowseRstbFile")
        self.horizontalLayout_2.addWidget(self.btnBrowseRstbFile)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgUpdateRstb)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlgUpdateRstb)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dlgUpdateRstb.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dlgUpdateRstb.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgUpdateRstb)

    def retranslateUi(self, dlgUpdateRstb):
        dlgUpdateRstb.setWindowTitle(QtWidgets.QApplication.translate("dlgUpdateRstb", "Update RSTB Entry", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("dlgUpdateRstb", "Enter the new resource size for the following entry:", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("dlgUpdateRstb", "{entry}", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("dlgUpdateRstb", "Size in Bytes: ", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("dlgUpdateRstb", "Detect size from file:", None, -1))
        self.btnBrowseRstbFile.setText(QtWidgets.QApplication.translate("dlgUpdateRstb", "Browse...", None, -1))

