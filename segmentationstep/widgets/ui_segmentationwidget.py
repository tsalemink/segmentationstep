# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/segmentationwidget.ui'
#
# Created: Thu Mar 21 17:42:27 2013
#      by: PySide UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SegmentationWidget(object):
    def setupUi(self, SegmentationWidget):
        SegmentationWidget.setObjectName(_fromUtf8("SegmentationWidget"))
        SegmentationWidget.resize(448, 352)
        self.verticalLayout = QtGui.QVBoxLayout(SegmentationWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(SegmentationWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.isoValueSlider = QtGui.QSlider(self.groupBox)
        self.isoValueSlider.setMaximum(99)
        self.isoValueSlider.setOrientation(QtCore.Qt.Vertical)
        self.isoValueSlider.setObjectName(_fromUtf8("isoValueSlider"))
        self.horizontalLayout_2.addWidget(self.isoValueSlider)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.compComboBox = QtGui.QComboBox(self.groupBox)
        self.compComboBox.setObjectName(_fromUtf8("compComboBox"))
        self.compComboBox.addItem(_fromUtf8(""))
        self.compComboBox.addItem(_fromUtf8(""))
        self.compComboBox.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.compComboBox)
        self.actionButton = QtGui.QPushButton(self.groupBox)
        self.actionButton.setObjectName(_fromUtf8("actionButton"))
        self.verticalLayout_2.addWidget(self.actionButton)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.context = ZincScene(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.context.sizePolicy().hasHeightForWidth())
        self.context.setSizePolicy(sizePolicy)
        self.context.setObjectName(_fromUtf8("context"))
        self.horizontalLayout_3.addWidget(self.context)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.doneButton = QtGui.QPushButton(SegmentationWidget)
        self.doneButton.setObjectName(_fromUtf8("doneButton"))
        self.horizontalLayout.addWidget(self.doneButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SegmentationWidget)
        QtCore.QMetaObject.connectSlotsByName(SegmentationWidget)

    def retranslateUi(self, SegmentationWidget):
        SegmentationWidget.setWindowTitle(_translate("SegmentationWidget", "Form", None))
        self.groupBox.setTitle(_translate("SegmentationWidget", "Digitiser", None))
        self.compComboBox.setItemText(0, _translate("SegmentationWidget", "comp. x", None))
        self.compComboBox.setItemText(1, _translate("SegmentationWidget", "comp. y", None))
        self.compComboBox.setItemText(2, _translate("SegmentationWidget", "comp. z", None))
        self.actionButton.setText(_translate("SegmentationWidget", "Add Node(s)", None))
        self.doneButton.setText(_translate("SegmentationWidget", "&Done", None))

from segmentationstep.widgets.zincscene import ZincScene
