# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/segmentationwidget.ui'
#
# Created: Thu Sep 11 13:15:31 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SegmentationWidget(object):
    def setupUi(self, SegmentationWidget):
        SegmentationWidget.setObjectName("SegmentationWidget")
        SegmentationWidget.resize(1012, 881)
        self.verticalLayout = QtGui.QVBoxLayout(SegmentationWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitterToolBox = QtGui.QSplitter(SegmentationWidget)
        self.splitterToolBox.setOrientation(QtCore.Qt.Horizontal)
        self.splitterToolBox.setObjectName("splitterToolBox")
        self.groupBox = QtGui.QGroupBox(self.splitterToolBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(250, 0))
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self._toolTab = QtGui.QToolBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._toolTab.sizePolicy().hasHeightForWidth())
        self._toolTab.setSizePolicy(sizePolicy)
        self._toolTab.setObjectName("_toolTab")
        self.file = QtGui.QWidget()
        self.file.setGeometry(QtCore.QRect(0, 0, 838, 745))
        self.file.setMinimumSize(QtCore.QSize(0, 0))
        self.file.setObjectName("file")
        self.verticalLayout_16 = QtGui.QVBoxLayout(self.file)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.groupBox_12 = QtGui.QGroupBox(self.file)
        self.groupBox_12.setTitle("")
        self.groupBox_12.setObjectName("groupBox_12")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_12)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self._pushButtonSave = QtGui.QPushButton(self.groupBox_12)
        self._pushButtonSave.setObjectName("_pushButtonSave")
        self.horizontalLayout_2.addWidget(self._pushButtonSave)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self._pushButtonLoad = QtGui.QPushButton(self.groupBox_12)
        self._pushButtonLoad.setObjectName("_pushButtonLoad")
        self.horizontalLayout_3.addWidget(self._pushButtonLoad)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem2 = QtGui.QSpacerItem(20, 60, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.doneButton = QtGui.QPushButton(self.groupBox_12)
        self.doneButton.setObjectName("doneButton")
        self.horizontalLayout_4.addWidget(self.doneButton)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_16.addWidget(self.groupBox_12)
        spacerItem4 = QtGui.QSpacerItem(17, 527, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_16.addItem(spacerItem4)
        self._toolTab.addItem(self.file, "")
        self.view = QtGui.QWidget()
        self.view.setGeometry(QtCore.QRect(0, 0, 838, 745))
        self.view.setObjectName("view")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.view)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_7 = QtGui.QGroupBox(self.view)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self._checkBoxImagePlane = QtGui.QCheckBox(self.groupBox_7)
        self._checkBoxImagePlane.setChecked(True)
        self._checkBoxImagePlane.setObjectName("_checkBoxImagePlane")
        self.verticalLayout_10.addWidget(self._checkBoxImagePlane)
        self._checkBoxImageOutline = QtGui.QCheckBox(self.groupBox_7)
        self._checkBoxImageOutline.setChecked(True)
        self._checkBoxImageOutline.setObjectName("_checkBoxImageOutline")
        self.verticalLayout_10.addWidget(self._checkBoxImageOutline)
        self._checkBoxCoordinateLabels = QtGui.QCheckBox(self.groupBox_7)
        self._checkBoxCoordinateLabels.setChecked(False)
        self._checkBoxCoordinateLabels.setObjectName("_checkBoxCoordinateLabels")
        self.verticalLayout_10.addWidget(self._checkBoxCoordinateLabels)
        self.verticalLayout_3.addWidget(self.groupBox_7)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem5)
        self._toolTab.addItem(self.view, "")
        self.image = QtGui.QWidget()
        self.image.setGeometry(QtCore.QRect(0, 0, 838, 745))
        self.image.setObjectName("image")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.image)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_4 = QtGui.QGroupBox(self.image)
        self.groupBox_4.setObjectName("groupBox_4")
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_4)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtGui.QLabel(self.groupBox_4)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self._labelmageWidth = QtGui.QLabel(self.groupBox_4)
        self._labelmageWidth.setText("")
        self._labelmageWidth.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._labelmageWidth.setObjectName("_labelmageWidth")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self._labelmageWidth)
        self.label_2 = QtGui.QLabel(self.groupBox_4)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self._labelmageHeight = QtGui.QLabel(self.groupBox_4)
        self._labelmageHeight.setText("")
        self._labelmageHeight.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._labelmageHeight.setObjectName("_labelmageHeight")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self._labelmageHeight)
        self.label_3 = QtGui.QLabel(self.groupBox_4)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self._labelmageDepth = QtGui.QLabel(self.groupBox_4)
        self._labelmageDepth.setText("")
        self._labelmageDepth.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._labelmageDepth.setObjectName("_labelmageDepth")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self._labelmageDepth)
        self.verticalLayout_4.addWidget(self.groupBox_4)
        self.groupBox_5 = QtGui.QGroupBox(self.image)
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout = QtGui.QFormLayout(self.groupBox_5)
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtGui.QLabel(self.groupBox_5)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_4)
        self._lineEditWidthScale = QtGui.QLineEdit(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lineEditWidthScale.sizePolicy().hasHeightForWidth())
        self._lineEditWidthScale.setSizePolicy(sizePolicy)
        self._lineEditWidthScale.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._lineEditWidthScale.setObjectName("_lineEditWidthScale")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self._lineEditWidthScale)
        self.label_5 = QtGui.QLabel(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_5)
        self._lineEditHeightScale = QtGui.QLineEdit(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lineEditHeightScale.sizePolicy().hasHeightForWidth())
        self._lineEditHeightScale.setSizePolicy(sizePolicy)
        self._lineEditHeightScale.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._lineEditHeightScale.setObjectName("_lineEditHeightScale")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self._lineEditHeightScale)
        self.label_6 = QtGui.QLabel(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_6)
        self._lineEditDepthScale = QtGui.QLineEdit(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lineEditDepthScale.sizePolicy().hasHeightForWidth())
        self._lineEditDepthScale.setSizePolicy(sizePolicy)
        self._lineEditDepthScale.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._lineEditDepthScale.setObjectName("_lineEditDepthScale")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self._lineEditDepthScale)
        self.verticalLayout_4.addWidget(self.groupBox_5)
        self.groupBox_6 = QtGui.QGroupBox(self.image)
        self.groupBox_6.setObjectName("groupBox_6")
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_6)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_7 = QtGui.QLabel(self.groupBox_6)
        self.label_7.setObjectName("label_7")
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_7)
        self._lineEditXOffset = QtGui.QLineEdit(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lineEditXOffset.sizePolicy().hasHeightForWidth())
        self._lineEditXOffset.setSizePolicy(sizePolicy)
        self._lineEditXOffset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._lineEditXOffset.setObjectName("_lineEditXOffset")
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self._lineEditXOffset)
        self.label_8 = QtGui.QLabel(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_8)
        self._lineEditYOffset = QtGui.QLineEdit(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lineEditYOffset.sizePolicy().hasHeightForWidth())
        self._lineEditYOffset.setSizePolicy(sizePolicy)
        self._lineEditYOffset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._lineEditYOffset.setObjectName("_lineEditYOffset")
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self._lineEditYOffset)
        self.label_9 = QtGui.QLabel(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setObjectName("label_9")
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_9)
        self._lineEditZOffset = QtGui.QLineEdit(self.groupBox_6)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._lineEditZOffset.sizePolicy().hasHeightForWidth())
        self._lineEditZOffset.setSizePolicy(sizePolicy)
        self._lineEditZOffset.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self._lineEditZOffset.setObjectName("_lineEditZOffset")
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self._lineEditZOffset)
        self.verticalLayout_4.addWidget(self.groupBox_6)
        spacerItem6 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem6)
        self._toolTab.addItem(self.image, "")
        self.horizontalLayout.addWidget(self._toolTab)
        self.splitterSceneviewers = QtGui.QSplitter(self.splitterToolBox)
        self.splitterSceneviewers.setOrientation(QtCore.Qt.Horizontal)
        self.splitterSceneviewers.setObjectName("splitterSceneviewers")
        self._tabWidgetLeft = SegmentationTabWidget(self.splitterSceneviewers)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._tabWidgetLeft.sizePolicy().hasHeightForWidth())
        self._tabWidgetLeft.setSizePolicy(sizePolicy)
        self._tabWidgetLeft.setStyleSheet("border-right: 10 px blue")
        self._tabWidgetLeft.setMovable(False)
        self._tabWidgetLeft.setObjectName("_tabWidgetLeft")
        self._tabWidgetRight = SegmentationTabWidget(self.splitterSceneviewers)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._tabWidgetRight.sizePolicy().hasHeightForWidth())
        self._tabWidgetRight.setSizePolicy(sizePolicy)
        self._tabWidgetRight.setMinimumSize(QtCore.QSize(0, 0))
        self._tabWidgetRight.setMaximumSize(QtCore.QSize(1, 16777215))
        self._tabWidgetRight.setObjectName("_tabWidgetRight")
        self.verticalLayout.addWidget(self.splitterToolBox)

        self.retranslateUi(SegmentationWidget)
        self._toolTab.setCurrentIndex(0)
        self._tabWidgetLeft.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(SegmentationWidget)

    def retranslateUi(self, SegmentationWidget):
        SegmentationWidget.setWindowTitle(QtGui.QApplication.translate("SegmentationWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("SegmentationWidget", "Digitiser", None, QtGui.QApplication.UnicodeUTF8))
        self._pushButtonSave.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Serialize the current state", None, QtGui.QApplication.UnicodeUTF8))
        self._pushButtonSave.setText(QtGui.QApplication.translate("SegmentationWidget", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self._pushButtonLoad.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Reinstate a previous state ", None, QtGui.QApplication.UnicodeUTF8))
        self._pushButtonLoad.setText(QtGui.QApplication.translate("SegmentationWidget", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.doneButton.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Signal the end of this step to the workflow manager", None, QtGui.QApplication.UnicodeUTF8))
        self.doneButton.setText(QtGui.QApplication.translate("SegmentationWidget", "&Done", None, QtGui.QApplication.UnicodeUTF8))
        self._toolTab.setItemText(self._toolTab.indexOf(self.file), QtGui.QApplication.translate("SegmentationWidget", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setTitle(QtGui.QApplication.translate("SegmentationWidget", "Graphic Visibility", None, QtGui.QApplication.UnicodeUTF8))
        self._checkBoxImagePlane.setText(QtGui.QApplication.translate("SegmentationWidget", "Image plane", None, QtGui.QApplication.UnicodeUTF8))
        self._checkBoxImageOutline.setText(QtGui.QApplication.translate("SegmentationWidget", "Image stack outline", None, QtGui.QApplication.UnicodeUTF8))
        self._checkBoxCoordinateLabels.setText(QtGui.QApplication.translate("SegmentationWidget", "Coordinate labels", None, QtGui.QApplication.UnicodeUTF8))
        self._toolTab.setItemText(self._toolTab.indexOf(self.view), QtGui.QApplication.translate("SegmentationWidget", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("SegmentationWidget", "Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SegmentationWidget", "Width : ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SegmentationWidget", "Height : ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("SegmentationWidget", "Depth : ", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("SegmentationWidget", "Scale", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("SegmentationWidget", "Width : ", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditWidthScale.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Set the width scale", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditWidthScale.setText(QtGui.QApplication.translate("SegmentationWidget", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("SegmentationWidget", "Height : ", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditHeightScale.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Set the height scale", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditHeightScale.setText(QtGui.QApplication.translate("SegmentationWidget", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("SegmentationWidget", "Depth : ", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditDepthScale.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Set the depth scale", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditDepthScale.setText(QtGui.QApplication.translate("SegmentationWidget", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_6.setTitle(QtGui.QApplication.translate("SegmentationWidget", "Offset", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("SegmentationWidget", "X :", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditXOffset.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Set the width scale", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditXOffset.setText(QtGui.QApplication.translate("SegmentationWidget", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("SegmentationWidget", "Y :", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditYOffset.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Set the height scale", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditYOffset.setText(QtGui.QApplication.translate("SegmentationWidget", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("SegmentationWidget", "Z :", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditZOffset.setToolTip(QtGui.QApplication.translate("SegmentationWidget", "Set the depth scale", None, QtGui.QApplication.UnicodeUTF8))
        self._lineEditZOffset.setText(QtGui.QApplication.translate("SegmentationWidget", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self._toolTab.setItemText(self._toolTab.indexOf(self.image), QtGui.QApplication.translate("SegmentationWidget", "Image", None, QtGui.QApplication.UnicodeUTF8))

from mapclientplugins.segmentationstep.widgets.segmentationtabwidget import SegmentationTabWidget
