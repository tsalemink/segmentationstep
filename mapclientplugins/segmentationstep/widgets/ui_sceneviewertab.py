# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/sceneviewertab.ui'
#
# Created: Thu Jul  3 12:11:43 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SceneviewerTab(object):
    def setupUi(self, SceneviewerTab, shared_context):
        SceneviewerTab.setObjectName("SceneviewerTab")
        SceneviewerTab.resize(400, 300)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SceneviewerTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self._tabToolBar = TabToolBar(SceneviewerTab)
        self._tabToolBar.setMinimumSize(QtCore.QSize(0, 15))
        self._tabToolBar.setObjectName("_tabToolBar")
        self.verticalLayout_2.addWidget(self._tabToolBar)
        self._reparentableWidget = QtGui.QWidget(SceneviewerTab)
        self._reparentableWidget.setObjectName("_reparentableWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self._reparentableWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self._zincwidget = ZincWidgetState(self._reparentableWidget, shared_context)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self._zincwidget.sizePolicy().hasHeightForWidth())
        self._zincwidget.setSizePolicy(sizePolicy)
        self._zincwidget.setMinimumSize(QtCore.QSize(100, 200))
        self._zincwidget.setObjectName("_zincwidget")
        self.verticalLayout.addWidget(self._zincwidget)
        self.verticalLayout_2.addWidget(self._reparentableWidget)

        self.retranslateUi(SceneviewerTab)
        QtCore.QMetaObject.connectSlotsByName(SceneviewerTab)

    def retranslateUi(self, SceneviewerTab):
        SceneviewerTab.setWindowTitle(QtGui.QApplication.translate("SceneviewerTab", "Form", None, QtGui.QApplication.UnicodeUTF8))

from mapclientplugins.segmentationstep.widgets.zincwidgetstate import ZincWidgetState
from mapclientplugins.segmentationstep.widgets.tabtoolbar import TabToolBar
