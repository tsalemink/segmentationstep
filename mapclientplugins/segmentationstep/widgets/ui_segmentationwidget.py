# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'segmentationwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QToolBox,
    QVBoxLayout, QWidget)

from mapclientplugins.segmentationstep.widgets.segmentationtabwidget import SegmentationTabWidget
from  . import resources_rc

class Ui_SegmentationWidget(object):
    def setupUi(self, SegmentationWidget):
        if not SegmentationWidget.objectName():
            SegmentationWidget.setObjectName(u"SegmentationWidget")
        SegmentationWidget.resize(1012, 881)
        self.verticalLayout = QVBoxLayout(SegmentationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitterToolBox = QSplitter(SegmentationWidget)
        self.splitterToolBox.setObjectName(u"splitterToolBox")
        self.splitterToolBox.setOrientation(Qt.Horizontal)
        self.groupBox = QGroupBox(self.splitterToolBox)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(250, 0))
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self._toolTab = QToolBox(self.groupBox)
        self._toolTab.setObjectName(u"_toolTab")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self._toolTab.sizePolicy().hasHeightForWidth())
        self._toolTab.setSizePolicy(sizePolicy1)
        self.file = QWidget()
        self.file.setObjectName(u"file")
        self.file.setGeometry(QRect(0, 0, 838, 745))
        self.file.setMinimumSize(QSize(0, 0))
        self.verticalLayout_16 = QVBoxLayout(self.file)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.groupBox_12 = QGroupBox(self.file)
        self.groupBox_12.setObjectName(u"groupBox_12")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_12)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self._pushButtonSave = QPushButton(self.groupBox_12)
        self._pushButtonSave.setObjectName(u"_pushButtonSave")

        self.horizontalLayout_2.addWidget(self._pushButtonSave)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self._pushButtonLoad = QPushButton(self.groupBox_12)
        self._pushButtonLoad.setObjectName(u"_pushButtonLoad")

        self.horizontalLayout_3.addWidget(self._pushButtonLoad)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.doneButton = QPushButton(self.groupBox_12)
        self.doneButton.setObjectName(u"doneButton")

        self.horizontalLayout_4.addWidget(self.doneButton)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.verticalLayout_16.addWidget(self.groupBox_12)

        self.verticalSpacer_4 = QSpacerItem(17, 527, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_4)

        self._toolTab.addItem(self.file, u"File")
        self.view = QWidget()
        self.view.setObjectName(u"view")
        self.view.setGeometry(QRect(0, 0, 838, 745))
        self.verticalLayout_3 = QVBoxLayout(self.view)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_7 = QGroupBox(self.view)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self._checkBoxImagePlane = QCheckBox(self.groupBox_7)
        self._checkBoxImagePlane.setObjectName(u"_checkBoxImagePlane")
        self._checkBoxImagePlane.setChecked(True)

        self.verticalLayout_10.addWidget(self._checkBoxImagePlane)

        self._checkBoxImageOutline = QCheckBox(self.groupBox_7)
        self._checkBoxImageOutline.setObjectName(u"_checkBoxImageOutline")
        self._checkBoxImageOutline.setChecked(True)

        self.verticalLayout_10.addWidget(self._checkBoxImageOutline)

        self._checkBoxCoordinateLabels = QCheckBox(self.groupBox_7)
        self._checkBoxCoordinateLabels.setObjectName(u"_checkBoxCoordinateLabels")
        self._checkBoxCoordinateLabels.setChecked(False)

        self.verticalLayout_10.addWidget(self._checkBoxCoordinateLabels)


        self.verticalLayout_3.addWidget(self.groupBox_7)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self._toolTab.addItem(self.view, u"View")
        self.image = QWidget()
        self.image.setObjectName(u"image")
        self.image.setGeometry(QRect(0, 0, 838, 745))
        self.verticalLayout_4 = QVBoxLayout(self.image)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_4 = QGroupBox(self.image)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.formLayout_2 = QFormLayout(self.groupBox_4)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label)

        self._labelmageWidth = QLabel(self.groupBox_4)
        self._labelmageWidth.setObjectName(u"_labelmageWidth")
        self._labelmageWidth.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self._labelmageWidth)

        self.label_2 = QLabel(self.groupBox_4)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self._labelmageHeight = QLabel(self.groupBox_4)
        self._labelmageHeight.setObjectName(u"_labelmageHeight")
        self._labelmageHeight.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self._labelmageHeight)

        self.label_3 = QLabel(self.groupBox_4)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self._labelmageDepth = QLabel(self.groupBox_4)
        self._labelmageDepth.setObjectName(u"_labelmageDepth")
        self._labelmageDepth.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self._labelmageDepth)


        self.verticalLayout_4.addWidget(self.groupBox_4)

        self.groupBox_5 = QGroupBox(self.image)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.formLayout = QFormLayout(self.groupBox_5)
        self.formLayout.setObjectName(u"formLayout")
        self.label_4 = QLabel(self.groupBox_5)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self._lineEditWidthScale = QLineEdit(self.groupBox_5)
        self._lineEditWidthScale.setObjectName(u"_lineEditWidthScale")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self._lineEditWidthScale.sizePolicy().hasHeightForWidth())
        self._lineEditWidthScale.setSizePolicy(sizePolicy2)
        self._lineEditWidthScale.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self._lineEditWidthScale)

        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy3)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self._lineEditHeightScale = QLineEdit(self.groupBox_5)
        self._lineEditHeightScale.setObjectName(u"_lineEditHeightScale")
        sizePolicy2.setHeightForWidth(self._lineEditHeightScale.sizePolicy().hasHeightForWidth())
        self._lineEditHeightScale.setSizePolicy(sizePolicy2)
        self._lineEditHeightScale.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self._lineEditHeightScale)

        self.label_6 = QLabel(self.groupBox_5)
        self.label_6.setObjectName(u"label_6")
        sizePolicy3.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy3)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_6)

        self._lineEditDepthScale = QLineEdit(self.groupBox_5)
        self._lineEditDepthScale.setObjectName(u"_lineEditDepthScale")
        sizePolicy2.setHeightForWidth(self._lineEditDepthScale.sizePolicy().hasHeightForWidth())
        self._lineEditDepthScale.setSizePolicy(sizePolicy2)
        self._lineEditDepthScale.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self._lineEditDepthScale)


        self.verticalLayout_4.addWidget(self.groupBox_5)

        self.groupBox_6 = QGroupBox(self.image)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.formLayout_3 = QFormLayout(self.groupBox_6)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.label_7 = QLabel(self.groupBox_6)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_7)

        self._lineEditXOffset = QLineEdit(self.groupBox_6)
        self._lineEditXOffset.setObjectName(u"_lineEditXOffset")
        sizePolicy2.setHeightForWidth(self._lineEditXOffset.sizePolicy().hasHeightForWidth())
        self._lineEditXOffset.setSizePolicy(sizePolicy2)
        self._lineEditXOffset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self._lineEditXOffset)

        self.label_8 = QLabel(self.groupBox_6)
        self.label_8.setObjectName(u"label_8")
        sizePolicy3.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy3)

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_8)

        self._lineEditYOffset = QLineEdit(self.groupBox_6)
        self._lineEditYOffset.setObjectName(u"_lineEditYOffset")
        sizePolicy2.setHeightForWidth(self._lineEditYOffset.sizePolicy().hasHeightForWidth())
        self._lineEditYOffset.setSizePolicy(sizePolicy2)
        self._lineEditYOffset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self._lineEditYOffset)

        self.label_9 = QLabel(self.groupBox_6)
        self.label_9.setObjectName(u"label_9")
        sizePolicy3.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy3)

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.label_9)

        self._lineEditZOffset = QLineEdit(self.groupBox_6)
        self._lineEditZOffset.setObjectName(u"_lineEditZOffset")
        sizePolicy2.setHeightForWidth(self._lineEditZOffset.sizePolicy().hasHeightForWidth())
        self._lineEditZOffset.setSizePolicy(sizePolicy2)
        self._lineEditZOffset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self._lineEditZOffset)


        self.verticalLayout_4.addWidget(self.groupBox_6)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_3)

        self._toolTab.addItem(self.image, u"Image")

        self.horizontalLayout.addWidget(self._toolTab)

        self.splitterToolBox.addWidget(self.groupBox)
        self.splitterSceneviewers = QSplitter(self.splitterToolBox)
        self.splitterSceneviewers.setObjectName(u"splitterSceneviewers")
        self.splitterSceneviewers.setOrientation(Qt.Horizontal)
        self._tabWidgetLeft = SegmentationTabWidget(self.splitterSceneviewers)
        self._tabWidgetLeft.setObjectName(u"_tabWidgetLeft")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(2)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self._tabWidgetLeft.sizePolicy().hasHeightForWidth())
        self._tabWidgetLeft.setSizePolicy(sizePolicy4)
        self._tabWidgetLeft.setStyleSheet(u"border-right: 10 px blue")
        self._tabWidgetLeft.setMovable(False)
        self.splitterSceneviewers.addWidget(self._tabWidgetLeft)
        self._tabWidgetRight = SegmentationTabWidget(self.splitterSceneviewers)
        self._tabWidgetRight.setObjectName(u"_tabWidgetRight")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(4)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self._tabWidgetRight.sizePolicy().hasHeightForWidth())
        self._tabWidgetRight.setSizePolicy(sizePolicy5)
        self._tabWidgetRight.setMinimumSize(QSize(0, 0))
        self._tabWidgetRight.setMaximumSize(QSize(1, 16777215))
        self.splitterSceneviewers.addWidget(self._tabWidgetRight)
        self.splitterToolBox.addWidget(self.splitterSceneviewers)

        self.verticalLayout.addWidget(self.splitterToolBox)


        self.retranslateUi(SegmentationWidget)

        self._toolTab.setCurrentIndex(0)
        self._tabWidgetLeft.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(SegmentationWidget)
    # setupUi

    def retranslateUi(self, SegmentationWidget):
        SegmentationWidget.setWindowTitle(QCoreApplication.translate("SegmentationWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("SegmentationWidget", u"Digitiser", None))
        self.groupBox_12.setTitle("")
#if QT_CONFIG(tooltip)
        self._pushButtonSave.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Serialize the current state", None))
#endif // QT_CONFIG(tooltip)
        self._pushButtonSave.setText(QCoreApplication.translate("SegmentationWidget", u"Save", None))
#if QT_CONFIG(tooltip)
        self._pushButtonLoad.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Reinstate a previous state ", None))
#endif // QT_CONFIG(tooltip)
        self._pushButtonLoad.setText(QCoreApplication.translate("SegmentationWidget", u"Load", None))
#if QT_CONFIG(tooltip)
        self.doneButton.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Signal the end of this step to the workflow manager", None))
#endif // QT_CONFIG(tooltip)
        self.doneButton.setText(QCoreApplication.translate("SegmentationWidget", u"&Done", None))
        self._toolTab.setItemText(self._toolTab.indexOf(self.file), QCoreApplication.translate("SegmentationWidget", u"File", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("SegmentationWidget", u"Graphic Visibility", None))
        self._checkBoxImagePlane.setText(QCoreApplication.translate("SegmentationWidget", u"Image plane", None))
        self._checkBoxImageOutline.setText(QCoreApplication.translate("SegmentationWidget", u"Image stack outline", None))
        self._checkBoxCoordinateLabels.setText(QCoreApplication.translate("SegmentationWidget", u"Coordinate labels", None))
        self._toolTab.setItemText(self._toolTab.indexOf(self.view), QCoreApplication.translate("SegmentationWidget", u"View", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("SegmentationWidget", u"Properties", None))
        self.label.setText(QCoreApplication.translate("SegmentationWidget", u"Width : ", None))
        self._labelmageWidth.setText("")
        self.label_2.setText(QCoreApplication.translate("SegmentationWidget", u"Height : ", None))
        self._labelmageHeight.setText("")
        self.label_3.setText(QCoreApplication.translate("SegmentationWidget", u"Depth : ", None))
        self._labelmageDepth.setText("")
        self.groupBox_5.setTitle(QCoreApplication.translate("SegmentationWidget", u"Scale", None))
        self.label_4.setText(QCoreApplication.translate("SegmentationWidget", u"Width : ", None))
#if QT_CONFIG(tooltip)
        self._lineEditWidthScale.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Set the width scale", None))
#endif // QT_CONFIG(tooltip)
        self._lineEditWidthScale.setText(QCoreApplication.translate("SegmentationWidget", u"1.0", None))
        self.label_5.setText(QCoreApplication.translate("SegmentationWidget", u"Height : ", None))
#if QT_CONFIG(tooltip)
        self._lineEditHeightScale.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Set the height scale", None))
#endif // QT_CONFIG(tooltip)
        self._lineEditHeightScale.setText(QCoreApplication.translate("SegmentationWidget", u"1.0", None))
        self.label_6.setText(QCoreApplication.translate("SegmentationWidget", u"Depth : ", None))
#if QT_CONFIG(tooltip)
        self._lineEditDepthScale.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Set the depth scale", None))
#endif // QT_CONFIG(tooltip)
        self._lineEditDepthScale.setText(QCoreApplication.translate("SegmentationWidget", u"1.0", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("SegmentationWidget", u"Offset", None))
        self.label_7.setText(QCoreApplication.translate("SegmentationWidget", u"X :", None))
#if QT_CONFIG(tooltip)
        self._lineEditXOffset.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Set the width scale", None))
#endif // QT_CONFIG(tooltip)
        self._lineEditXOffset.setText(QCoreApplication.translate("SegmentationWidget", u"1.0", None))
        self.label_8.setText(QCoreApplication.translate("SegmentationWidget", u"Y :", None))
#if QT_CONFIG(tooltip)
        self._lineEditYOffset.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Set the height scale", None))
#endif // QT_CONFIG(tooltip)
        self._lineEditYOffset.setText(QCoreApplication.translate("SegmentationWidget", u"1.0", None))
        self.label_9.setText(QCoreApplication.translate("SegmentationWidget", u"Z :", None))
#if QT_CONFIG(tooltip)
        self._lineEditZOffset.setToolTip(QCoreApplication.translate("SegmentationWidget", u"Set the depth scale", None))
#endif // QT_CONFIG(tooltip)
        self._lineEditZOffset.setText(QCoreApplication.translate("SegmentationWidget", u"1.0", None))
        self._toolTab.setItemText(self._toolTab.indexOf(self.image), QCoreApplication.translate("SegmentationWidget", u"Image", None))
    # retranslateUi

