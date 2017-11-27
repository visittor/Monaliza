from PyQt4 import QtCore, QtGui
from demo import Ui_MainWindow

from image_processing import ImageProcessing
from factory import filter_factory

import cv2
import numpy as np
from matplotlib import pyplot as plt

import time
import threading
import ConfigParser

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

	def __init__(self,MainWindow, file_cfg):
		super(mainWin, self).__init__(parent = None)
		self.setupUi(MainWindow)
		self.get_config(file_cfg)
		self.setup_filter()
		self.set_menu_bar()
		self.__start_flag = threading.Event()
		self.__is_arrayFile = threading.Event()
		self.__start_flag.clear()
		self.__is_arrayFile.clear()
		self.__ImageProcessing_thread = None
		self.__filter_manager_factory = None
		self.__tween_factory = lambda x:None
		self.Lock = threading.Lock()
		self.__roi = None
		self.__calib_h = None
		self.__calib_w = None
		self.__camera_mtx = None
		self.__dist_coeff = None
		self.__rvec = None
		self.__tvec = None

	def get_config(self, file_cfg):
		self.__config = ConfigParser.ConfigParser()
		self.__config.read(file_cfg)

	def load_camera_matrix(self, matrix_filename):
		with np.load( matrix_filename ) as matrixes:
			self.__calib_h, self.__calib_w = matrixes['shape']
			self.__camera_mtx = matrixes['camera_matrix']
			self.__dist_coeff = matrixes['distortion_ceff']
			planar_index = matrixes['planar_index'][0]
			self.__rvec = matrixes['rotation_vector'][planar_index]
			self.__tvec = matrixes['translation_vector'][planar_index]

	def select_camera_matrix_file(self):
		filename = str( QtGui.QFileDialog.getOpenFileName(self, 'Open File') )
		self.load_camera_matrix(filename)

	def setup_filter(self):
		num_sec = 1
		y = 50
		while 1==1:
			if self.__config.has_section(str(num_sec)):
				name = self.__config.get(str(num_sec), 'filter_name')
				setattr(self, "is_"+name, QtGui.QCheckBox(self.scrollAreaWidgetContents))
				getattr(self, "is_"+name).setObjectName(_fromUtf8("is_"+name))
				getattr(self, "is_"+name).setGeometry(QtCore.QRect(10, y, 150, 20))
				getattr(self, "is_"+name).setText(_translate("MainWindow", name, None))

				num_param = 1
				x = 200
				while self.__config.has_option(str(num_sec), "parameter"+str(num_param)+"_name"):
					dial_name = name + "_" + self.__config.get(str(num_sec), "parameter" + str(num_param) + "_name")
					setattr(self, dial_name, QtGui.QDial(self.tab1_scroll))
					getattr(self, dial_name).setGeometry(QtCore.QRect(x, y-30, 50, 60))
					getattr(self, dial_name).setObjectName(_fromUtf8(dial_name))
					getattr(self, dial_name).setMaximum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_max") )
					getattr(self, dial_name).setMinimum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_min") )

					spin_name = dial_name + "_spin"
					setattr(self, spin_name, QtGui.QSpinBox(self.tab1_scroll))
					getattr(self, spin_name).setGeometry(QtCore.QRect(x+50, y-10, 50, 20))
					getattr(self, spin_name).setObjectName(_fromUtf8(spin_name))
					getattr(self, spin_name).setMaximum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_max") )
					getattr(self, spin_name).setMinimum( self.__config.getint(str(num_sec), "parameter" + str(num_param) + "_min") )

					label_name = dial_name + "_label"
					setattr(self, label_name, QtGui.QLabel(self.tab1_scroll))
					getattr(self, label_name).setGeometry(QtCore.QRect(x, y+20, 46, 13))
					getattr(self, label_name).setObjectName(_fromUtf8(label_name))
					getattr(self, label_name).setText(_translate("MainWindow",  self.__config.get(str(num_sec), "parameter" + str(num_param) + "_name"), None))

					QtCore.QObject.connect(getattr(self, spin_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, dial_name).setValue)
					QtCore.QObject.connect(getattr(self, dial_name), QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), getattr(self, spin_name).setValue)

					x += 200
					num_param += 1
			else:
				break
			num_sec += 1
			y += 75

	def set_menu_bar(self):
		self.actionUse_local_file.triggered.connect(self.create_project_from_local_file)
		self.actionUse_local_file.setShortcut("Ctrl+N")

		self.actionSave_cnt.setEnabled(False)
		self.actionSave_cnt.triggered.connect(self.save_contour)
		self.actionSave_cnt.setShortcut("Ctrl+S")

		self.actionLoad_cnt.triggered.connect(self.create_project_from_npz)
		self.actionLoad_cnt.setShortcut("Ctrl+L")

		self.milestone2.stateChanged.connect(self.milestone2statechange)
		self.milestone2maxpolygon.setEnabled(False)
		self.milestone2maxlenght.setEnabled(False)

		self.milestone3.clicked.connect(self.milestone3_clicked)

		self.capture_img.clicked.connect(self.capture)

		self.select_roi.clicked.connect(self.load_roi)

		self.select_camera_matrix.clicked.connect(self.select_camera_matrix_file)

		self.retr_tree.clicked.connect( lambda x:self.retr_external.setChecked(False) )
		self.retr_external.clicked.connect( lambda x:self.retr_tree.setChecked(False) )

	def set_filter_manager_factory(self, filter_manager_factory):
		self.__filter_manager_factory = filter_manager_factory

	def set_tween_factory(self, tween_factory):
		self.__tween_factory = tween_factory

	def create_project_from_local_file(self):
		file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		self.__create_ImageProcessing_thread_from_image( str(file_name) )

	def create_project_from_npz(self):
		file_name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
		self.__create_ImageProcessing_thread_from_contour( str(file_name) )

	def save_contour(self):
		file_name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
		if self.__ImageProcessing_thread.is_alive():
			self.__ImageProcessing_thread.save_contour( str(file_name) )

	def __create_ImageProcessing_thread_from_contour(self, file_name):
		self.__create_ImageProcessing_thread()
		self.__ImageProcessing_thread.recieve_contour_from_filename(file_name)
		self.__start_flag.set()
		self.__is_arrayFile.set()
		self.__ImageProcessing_thread.start()
		time.sleep(1)
		if self.__ImageProcessing_thread.is_alive():
			self.actionSave_cnt.setEnabled(True)

	def __create_ImageProcessing_thread_from_image(self, file_name):
		self.__create_ImageProcessing_thread()
		self.__ImageProcessing_thread.recieve_image_from_filename(file_name)
		self.__start_flag.set()
		self.__ImageProcessing_thread.start()
		time.sleep(1)
		if self.__ImageProcessing_thread.is_alive():
			self.actionSave_cnt.setEnabled(True)
		print self.__ImageProcessing_thread

	def __create_ImageProcessing_thread(self):
		self.clear_flag()
		if self.__ImageProcessing_thread is not None and self.__ImageProcessing_thread.is_alive():
			print "wait ..."
			self.__ImageProcessing_thread.join()
		del self.__ImageProcessing_thread
		time.sleep(1)
		self.__ImageProcessing_thread = ImageProcessing(start_flag = self.__start_flag, is_arrayFile = self.__is_arrayFile, ui = self, config = self.__config)
		filter_manager = self.__filter_manager_factory(self)
		tween = self.__tween_factory
		self.__ImageProcessing_thread.attach_filter( filter_manager )
		self.__ImageProcessing_thread.attach_tween( tween )

	def milestone2statechange(self):
		if self.milestone2.isChecked():
			self.milestone2maxpolygon.setEnabled(True)
			self.milestone2maxlenght.setEnabled(True)
		else:
			self.milestone2maxpolygon.setEnabled(False)
			self.milestone2maxlenght.setEnabled(False)

	def milestone3_clicked(self):
		if self.__ImageProcessing_thread is not None:
			self.__ImageProcessing_thread.identify_color()

	def closeEvent(self, event):
		print "closing"
		self.__start_flag.clear()
		if self.__ImageProcessing_thread is not None:
			self.__ImageProcessing_thread.join()

	def clear_flag(self):
		self.__is_arrayFile.clear()
		self.__start_flag.clear()

	def load_roi(self):
		file_name = str( QtGui.QFileDialog.getOpenFileName(self, 'Open File') )
		print "loading ..."
		roi = cv2.imread(file_name, 0)
		# roi = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY) 
		# self.__roi = np.zeros((roi.shape[0],roi.shape[1],3), np.uint8)
		# self.__roi[:,:,0] = roi
		# self.__roi[:,:,1] = roi
		# self.__roi[:,:,2] = roi
		if self.__ImageProcessing_thread is not None and self.__ImageProcessing_thread.is_alive():
			self.__ImageProcessing_thread.set_roi(roi)
		print "Done!!"

	def capture(self):
		cap = cv2.VideoCapture(int(self.camera_ID_spinbox.value()))
		print "Capturing."
		for i in range(100):
			ret,img = cap.read()
			time.sleep(0.01)
		ret,img = cap.read()
		if ret:
			if self.__camera_mtx is not None and self.__dist_coeff is not None:
				img = cv2.undistort(img, self.__camera_mtx, self.__dist_coeff)
				print "Undistort"
			# if self.__roi is not None:
			# 	shape0 = self.__roi.shape[0] if self.__roi.shape[0] < img.shape[0] else img.shape[0]
			# 	shape1 = self.__roi.shape[1] if self.__roi.shape[1] < img.shape[1] else img.shape[1]
			# 	img[:shape0, :shape1] = ((img[:shape0,:shape1].astype(np.uint16) * self.__roi[:shape0,:shape1].astype(np.uint16))/255).astype(np.uint8)
			# 	print "Use roi"
			img_rgb = img
			plt.imshow(img_rgb)
			plt.show()
			filename = str( QtGui.QFileDialog.getSaveFileName(self, 'Save File') )
			if filename:
				try:
					cv2.imwrite( filename, img)
				except cv2.error as e:
					filename += ".png"
					cv2.imwrite( filename, img)
				finally:
					cap.release
		else:
			print "Cannot Found Camera."
			cap.release()


if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	MainWindow = QtGui.QMainWindow()
	ui = mainWin(MainWindow, "development.cfg")
	ui.set_filter_manager_factory(filter_factory)

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
	# dilated = cv2.dilate(image, kernel)
	# ui.set_tween_factory( lambda x:cv2.morphologyEx(x, cv2.MORPH_OPEN, kernel))
	ui.set_tween_factory( lambda x:cv2.dilate(x, kernel))
	MainWindow.show()
	sys.exit(app.exec_())