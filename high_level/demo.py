# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'demo.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(907, 831)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 901, 801))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.verticalLayoutWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tab1_scroll = QtGui.QScrollArea(self.tab)
        self.tab1_scroll.setGeometry(QtCore.QRect(0, 0, 901, 771))
        self.tab1_scroll.setWidgetResizable(True)
        self.tab1_scroll.setObjectName(_fromUtf8("tab1_scroll"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 899, 769))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.tab1_scroll.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.lower_thr_edges = QtGui.QSlider(self.tab_2)
        self.lower_thr_edges.setGeometry(QtCore.QRect(20, 20, 661, 20))
        self.lower_thr_edges.setOrientation(QtCore.Qt.Horizontal)
        self.lower_thr_edges.setObjectName(_fromUtf8("lower_thr_edges"))
        self.lower_thr_edges_spin = QtGui.QSpinBox(self.tab_2)
        self.lower_thr_edges_spin.setGeometry(QtCore.QRect(700, 20, 70, 20))
        self.lower_thr_edges_spin.setObjectName(_fromUtf8("lower_thr_edges_spin"))
        self.label_2 = QtGui.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(790, 20, 61, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.upper_thr_edges = QtGui.QSlider(self.tab_2)
        self.upper_thr_edges.setGeometry(QtCore.QRect(20, 120, 661, 20))
        self.upper_thr_edges.setOrientation(QtCore.Qt.Horizontal)
        self.upper_thr_edges.setObjectName(_fromUtf8("upper_thr_edges"))
        self.upper_thr_edges_spin = QtGui.QSpinBox(self.tab_2)
        self.upper_thr_edges_spin.setGeometry(QtCore.QRect(700, 120, 70, 20))
        self.upper_thr_edges_spin.setObjectName(_fromUtf8("upper_thr_edges_spin"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(790, 120, 61, 20))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cnt_step = QtGui.QSlider(self.tab_2)
        self.cnt_step.setGeometry(QtCore.QRect(20, 220, 661, 20))
        self.cnt_step.setOrientation(QtCore.Qt.Horizontal)
        self.cnt_step.setObjectName(_fromUtf8("cnt_step"))
        self.cnt_step_spin = QtGui.QSpinBox(self.tab_2)
        self.cnt_step_spin.setGeometry(QtCore.QRect(700, 220, 70, 20))
        self.cnt_step_spin.setObjectName(_fromUtf8("cnt_step_spin"))
        self.label_4 = QtGui.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(790, 220, 61, 20))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 907, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionSave_as = QtGui.QAction(MainWindow)
        self.actionSave_as.setObjectName(_fromUtf8("actionSave_as"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setCheckable(True)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionUse_camera = QtGui.QAction(MainWindow)
        self.actionUse_camera.setObjectName(_fromUtf8("actionUse_camera"))
        self.actionUse_local_file = QtGui.QAction(MainWindow)
        self.actionUse_local_file.setObjectName(_fromUtf8("actionUse_local_file"))
        self.actionSave_cnt = QtGui.QAction(MainWindow)
        self.actionSave_cnt.setObjectName(_fromUtf8("actionSave_cnt"))
        self.actionLoad_cnt = QtGui.QAction(MainWindow)
        self.actionLoad_cnt.setObjectName(_fromUtf8("actionLoad_cnt"))
        self.menuMenu.addAction(self.actionUse_camera)
        self.menuMenu.addAction(self.actionUse_local_file)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionSave_cnt)
        self.menuMenu.addAction(self.actionLoad_cnt)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QObject.connect(self.lower_thr_edges, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.lower_thr_edges_spin.setValue)
        QtCore.QObject.connect(self.lower_thr_edges_spin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.lower_thr_edges.setValue)
        QtCore.QObject.connect(self.upper_thr_edges, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.upper_thr_edges_spin.setValue)
        QtCore.QObject.connect(self.upper_thr_edges_spin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.upper_thr_edges.setValue)
        QtCore.QObject.connect(self.cnt_step, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.cnt_step_spin.setValue)
        QtCore.QObject.connect(self.cnt_step_spin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.cnt_step.setValue)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1", None))
        self.label_2.setText(_translate("MainWindow", "Lower Thr", None))
        self.label_3.setText(_translate("MainWindow", "upper Thr", None))
        self.label_4.setText(_translate("MainWindow", "cnt step", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2", None))
        self.menuMenu.setTitle(_translate("MainWindow", "menu", None))
        self.actionNew.setText(_translate("MainWindow", "&new", None))
        self.actionSave_as.setText(_translate("MainWindow", "&save as", None))
        self.actionSave.setText(_translate("MainWindow", "&save", None))
        self.actionOpen.setText(_translate("MainWindow", "&open", None))
        self.actionExit.setText(_translate("MainWindow", "&exit", None))
        self.actionUse_camera.setText(_translate("MainWindow", "use_camera", None))
        self.actionUse_local_file.setText(_translate("MainWindow", "use_local_file", None))
        self.actionSave_cnt.setText(_translate("MainWindow", "save_cnt", None))
        self.actionLoad_cnt.setText(_translate("MainWindow", "load_cnt", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
