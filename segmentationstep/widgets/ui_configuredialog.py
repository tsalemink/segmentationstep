# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/configuredialog.ui'
#
# Created: Fri Jun 14 15:10:39 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ConfigureDialog(object):
    def setupUi(self, ConfigureDialog):
        ConfigureDialog.setObjectName("ConfigureDialog")
        ConfigureDialog.resize(526, 216)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ConfigureDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtGui.QGroupBox(ConfigureDialog)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.identifierLineEdit = QtGui.QLineEdit(self.groupBox)
        self.identifierLineEdit.setObjectName("identifierLineEdit")
        self.horizontalLayout.addWidget(self.identifierLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(ConfigureDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.label.setBuddy(self.identifierLineEdit)

        self.retranslateUi(ConfigureDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ConfigureDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ConfigureDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigureDialog)

    def retranslateUi(self, ConfigureDialog):
        ConfigureDialog.setWindowTitle(QtGui.QApplication.translate("ConfigureDialog", "Configure - Point Cloud Store", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ConfigureDialog", "Identifier:", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
