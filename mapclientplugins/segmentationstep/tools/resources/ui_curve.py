# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'curve.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PropertiesWidget(object):
    def setupUi(self, PropertiesWidget):
        if not PropertiesWidget.objectName():
            PropertiesWidget.setObjectName(u"PropertiesWidget")
        PropertiesWidget.resize(330, 420)
        self.verticalLayout = QVBoxLayout(PropertiesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(PropertiesWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self._doubleSpinBoxPointSize = QDoubleSpinBox(self.groupBox)
        self._doubleSpinBoxPointSize.setObjectName(u"_doubleSpinBoxPointSize")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._doubleSpinBoxPointSize.sizePolicy().hasHeightForWidth())
        self._doubleSpinBoxPointSize.setSizePolicy(sizePolicy)
        self._doubleSpinBoxPointSize.setMinimum(0.010000000000000)
        self._doubleSpinBoxPointSize.setMaximum(999999.989999999990687)
        self._doubleSpinBoxPointSize.setValue(45.000000000000000)

        self.verticalLayout_2.addWidget(self._doubleSpinBoxPointSize)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_8 = QGroupBox(PropertiesWidget)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_8)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self._spinBoxInterpolationCount = QSpinBox(self.groupBox_8)
        self._spinBoxInterpolationCount.setObjectName(u"_spinBoxInterpolationCount")

        self.verticalLayout_11.addWidget(self._spinBoxInterpolationCount)


        self.verticalLayout.addWidget(self.groupBox_8)

        self.groupBox_10 = QGroupBox(PropertiesWidget)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_10)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_10 = QLabel(self.groupBox_10)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_2.addWidget(self.label_10)

        self._doubleSpinBoxStepSize = QDoubleSpinBox(self.groupBox_10)
        self._doubleSpinBoxStepSize.setObjectName(u"_doubleSpinBoxStepSize")
        self._doubleSpinBoxStepSize.setValue(1.000000000000000)

        self.horizontalLayout_2.addWidget(self._doubleSpinBoxStepSize)


        self.verticalLayout_7.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self._pushButtonPushDown = QPushButton(self.groupBox_10)
        self._pushButtonPushDown.setObjectName(u"_pushButtonPushDown")
        self._pushButtonPushDown.setMinimumSize(QSize(99, 0))

        self.horizontalLayout_6.addWidget(self._pushButtonPushDown)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)

        self._pushButtonPullUp = QPushButton(self.groupBox_10)
        self._pushButtonPullUp.setObjectName(u"_pushButtonPullUp")
        self._pushButtonPullUp.setMinimumSize(QSize(99, 0))

        self.horizontalLayout_6.addWidget(self._pushButtonPullUp)


        self.verticalLayout_7.addLayout(self.horizontalLayout_6)


        self.verticalLayout.addWidget(self.groupBox_10)

        self.groupBox_11 = QGroupBox(PropertiesWidget)
        self.groupBox_11.setObjectName(u"groupBox_11")
        self.verticalLayout_14 = QVBoxLayout(self.groupBox_11)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self._pushButtonDelete = QPushButton(self.groupBox_11)
        self._pushButtonDelete.setObjectName(u"_pushButtonDelete")

        self.horizontalLayout_5.addWidget(self._pushButtonDelete)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)


        self.verticalLayout_14.addLayout(self.horizontalLayout_5)


        self.verticalLayout.addWidget(self.groupBox_11)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(PropertiesWidget)

        QMetaObject.connectSlotsByName(PropertiesWidget)
    # setupUi

    def retranslateUi(self, PropertiesWidget):
        PropertiesWidget.setWindowTitle(QCoreApplication.translate("PropertiesWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("PropertiesWidget", u"Point Size", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("PropertiesWidget", u"Interpolation Point Count", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("PropertiesWidget", u"Push/Pull", None))
        self.label_10.setText(QCoreApplication.translate("PropertiesWidget", u"Step size:", None))
#if QT_CONFIG(tooltip)
        self._doubleSpinBoxStepSize.setToolTip(QCoreApplication.translate("PropertiesWidget", u"Set the depth for pushing/pulling segmentation points down/up a layer", None))
#endif // QT_CONFIG(tooltip)
        self._pushButtonPushDown.setText(QCoreApplication.translate("PropertiesWidget", u"Push Down", None))
        self._pushButtonPullUp.setText(QCoreApplication.translate("PropertiesWidget", u"Pull Up", None))
        self.groupBox_11.setTitle(QCoreApplication.translate("PropertiesWidget", u"Edit", None))
#if QT_CONFIG(tooltip)
        self._pushButtonDelete.setToolTip(QCoreApplication.translate("PropertiesWidget", u"Remove selected segmentation points", None))
#endif // QT_CONFIG(tooltip)
        self._pushButtonDelete.setText(QCoreApplication.translate("PropertiesWidget", u"Delete", None))
    # retranslateUi

