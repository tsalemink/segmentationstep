# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/sceneviewertab.ui'
#
# Created: Fri May 30 21:10:08 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SceneviewerTab(object):
    def setupUi(self, SceneviewerTab, shared_context):
        SceneviewerTab.setObjectName("SceneviewerTab")
        SceneviewerTab.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(SceneviewerTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self._tabToolBar = TabToolBar(SceneviewerTab)
        self._tabToolBar.setMinimumSize(QtCore.QSize(0, 15))
        self._tabToolBar.setObjectName("_tabToolBar")
        self.verticalLayout.addWidget(self._tabToolBar)
        self._zincwidget = ZincWidgetState(SceneviewerTab, shared_context)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self._zincwidget.sizePolicy().hasHeightForWidth())
        self._zincwidget.setSizePolicy(sizePolicy)
        self._zincwidget.setMinimumSize(QtCore.QSize(100, 200))
        self._zincwidget.setObjectName("_zincwidget")
        self.verticalLayout.addWidget(self._zincwidget)

        self.retranslateUi(SceneviewerTab)
        QtCore.QMetaObject.connectSlotsByName(SceneviewerTab)

    def retranslateUi(self, SceneviewerTab):
        SceneviewerTab.setWindowTitle(QtGui.QApplication.translate("SceneviewerTab", "Form", None, QtGui.QApplication.UnicodeUTF8))

from mapclientplugins.segmentationstep.widgets.tabtoolbar import TabToolBar
from mapclientplugins.segmentationstep.widgets.zincwidgetstate import ZincWidgetState
