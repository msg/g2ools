# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nm2g2g.ui'
#
# Created: Tue Feb 20 15:22:01 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_NM2G2G(object):
    def setupUi(self, NM2G2G):
        NM2G2G.setObjectName("NM2G2G")
        NM2G2G.resize(QtCore.QSize(QtCore.QRect(0,0,658,589).size()).expandedTo(NM2G2G.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(NM2G2G)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(0)
        self.vboxlayout.setObjectName("vboxlayout")

        self.splitter = QtGui.QSplitter(self.centralwidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.treeView = QtGui.QTreeView(self.splitter)
        self.treeView.setObjectName("treeView")

        self.textEdit = QtGui.QTextEdit(self.splitter)
        self.textEdit.setObjectName("textEdit")
        self.vboxlayout.addWidget(self.splitter)
        NM2G2G.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(NM2G2G)
        self.menubar.setGeometry(QtCore.QRect(0,0,658,29))
        self.menubar.setObjectName("menubar")

        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        NM2G2G.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(NM2G2G)
        self.statusbar.setObjectName("statusbar")
        NM2G2G.setStatusBar(self.statusbar)

        self.action_Quit = QtGui.QAction(NM2G2G)
        self.action_Quit.setObjectName("action_Quit")

        self.action_Run = QtGui.QAction(NM2G2G)
        self.action_Run.setObjectName("action_Run")
        self.menu_File.addAction(self.action_Run)
        self.menu_File.addAction(self.action_Quit)
        self.menubar.addAction(self.menu_File.menuAction())

        self.retranslateUi(NM2G2G)
        QtCore.QObject.connect(self.action_Quit,QtCore.SIGNAL("activated()"),NM2G2G.close)
        QtCore.QMetaObject.connectSlotsByName(NM2G2G)

    def retranslateUi(self, NM2G2G):
        NM2G2G.setWindowTitle(QtGui.QApplication.translate("NM2G2G", "NM2G2G NM1 To G2 Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("NM2G2G", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setText(QtGui.QApplication.translate("NM2G2G", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setShortcut(QtGui.QApplication.translate("NM2G2G", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Run.setText(QtGui.QApplication.translate("NM2G2G", "&Run", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Run.setShortcut(QtGui.QApplication.translate("NM2G2G", "Ctrl+R", None, QtGui.QApplication.UnicodeUTF8))

