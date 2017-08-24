from PyQt4 import QtCore, QtGui
from demo import Ui_MainWindow
from to_edge import process_image
import cv2
import time
import thread

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

class mainWin(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self,MainWindow, filter_setting, edge_setting, parent = None):
        super(mainWin, self).__init__(parent = None)
        self.setupUi(MainWindow)
        self.setupButton()
        self.setup_filter_ui(filter_setting)
        self.setup_edge_ui(edge_setting)

    def setup_filter_ui(self,filter_setting):
        y = 50
        for filt_name,parameter in filter_setting.items():
            name = "radioFilter_"+filt_name
            setattr(self, name, QtGui.QCheckBox(self.tab))
            getattr(self, name).setObjectName(_fromUtf8(name))
            getattr(self, name).setGeometry(QtCore.QRect(10, y, 150, 20))
            getattr(self, name).setText(_translate("MainWindow", filt_name, None))
            x = 200
            for para, value in parameter.items():
                dial_name = "dial_"+filt_name+"_"+para
                print filter_setting, y
                setattr(self, dial_name, QtGui.QDial(self.tab))
                getattr(self, dial_name).setGeometry(QtCore.QRect(x, y-30, 50, 60))
                getattr(self, dial_name).setObjectName(_fromUtf8(dial_name))
                getattr(self, dial_name).setMaximum(value[1])
                getattr(self, dial_name).setMinimum(value[0])

                lebel_name = "lebel_"+filt_name+"_"+para
                setattr(self, lebel_name, QtGui.QLabel(self.tab))
                getattr(self, lebel_name).setGeometry(QtCore.QRect(x, y+20, 46, 13))
                getattr(self, lebel_name).setObjectName(_fromUtf8("label"))
                getattr(self, lebel_name).setText(_translate("MainWindow", para, None))

                spin_name = "spinBox_"+filt_name+"_"+para
                setattr(self, spin_name, QtGui.QSpinBox(self.tab))
                getattr(self, spin_name).setGeometry(QtCore.QRect(x+50, y-10, 50, 20))
                getattr(self, spin_name).setObjectName(_fromUtf8(spin_name))
                getattr(self, spin_name).setMaximum(value[1])
                getattr(self, spin_name).setMinimum(value[0])
                QtCore.QObject.connect(getattr(self, spin_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, dial_name).setValue)
                QtCore.QObject.connect(getattr(self, dial_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, spin_name).setValue)
                x += 200
            y += 75

    def setup_edge_ui(self, edge_setting):
        y = 20
        for para_name, value in edge_setting.items():
            name = "slider_"+para_name
            setattr(self, name, QtGui.QSlider(self.tab_2))
            getattr(self, name).setGeometry(QtCore.QRect(20, y, 280, 20))
            getattr(self, name).setOrientation(QtCore.Qt.Horizontal)
            getattr(self, name).setObjectName(_fromUtf8(name))
            getattr(self, name).setMaximum(value[1])
            getattr(self, name).setMinimum(value[0])

            lebel_name = "lebel_"+para_name
            setattr(self, lebel_name, QtGui.QLabel(self.tab_2))
            getattr(self, lebel_name).setGeometry(QtCore.QRect(420, y, 46, 20))
            getattr(self, lebel_name).setObjectName(_fromUtf8("label"))
            getattr(self, lebel_name).setText(_translate("MainWindow", para_name, None))

            spin_name = "spin_"+para_name
            setattr(self, spin_name, QtGui.QSpinBox(self.tab_2))
            getattr(self, spin_name).setGeometry(QtCore.QRect(340, y, 50, 20))
            getattr(self, spin_name).setObjectName(_fromUtf8(spin_name))
            getattr(self, spin_name).setMaximum(value[1])
            getattr(self, spin_name).setMinimum(value[0])

            QtCore.QObject.connect(getattr(self, spin_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, name).setValue)
            QtCore.QObject.connect(getattr(self, name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, spin_name).setValue)
            y += 75

            
    def setupButton(self):
        self.actionOpen.triggered.connect(self.file_open)

    def file_open(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        print name 

if __name__ == "__main__":
    import sys
    filter_argument = {"GaussianBlur":{"kSizeG":(1,11)}, "detailEnhance":{"sigmaM":(0,100),"sigmaS":(0,200)}, "bilateralFilter":{"time":(1,10)}, "Laplacian":{"threshold":(0,255)}, }
    edge_argument = {"lowerThr":(0,500), "upperThr":(0,500), "contourStep":(1,15), "dilateEdgeIter":(0,10)}

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = mainWin(MainWindow, filter_argument, edge_argument)

    try:
        thread.start_new_thread( process_image, ("geometry.png", ui) )
    except Exception as e:
        print "Error: unable to start thread",e

    MainWindow.show()
    sys.exit(app.exec_())
    while 1:
        pass
