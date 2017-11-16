import cv2
import numpy as np
from matplotlib import pyplot as plt

import time
from PyQt4 import QtCore, QtGui
from serial_ui import Ui_MainWindow
from serial_thread import Serilal_sender
import ConfigParser

import sys
import glob
import serial
import time
import threading

from Queue import Queue

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

def find_line_trajectory_coeff(point1, point2, t):
	R = np.linalg.norm(point2 - point1)
	deltaX = point2[0] - point1[0]
	deltaY = point2[1] - point1[1]
	theta = np.arctan2(deltaY, deltaX)
	M = np.array([	[      0,      0,      0,      0,      0,      1],
					[      0,      0,      0,      0,      1,      0],
					[      0,      0,      0,      2,      0,      0],
					[   t**5,   t**4,   t**3,   t**2,      t,      1],
					[ 5*t**4, 4*t**3, 3*t**2,    2*t,      1,      0],
					[20*t**3,12*t**2,    6*t,      2,      0,      0],])
	rMat = np.array([0, 0, 0, R, 0, 0]).reshape(-1,1)
	invM = np.linalg.inv(M)
	coeffs = np.dot(invM, rMat).reshape(-1)

class XY_ui_interface(Ui_MainWindow):
	axis_dict = {'x':9, 'y':10, 'z':11}
	direction = {'CCW':0, 'CW':1, 'up':0, 'down':1}
	gripper_action = {'active':1, 'release':0}

	def __init__(self, MainWindow, file_cfg):
		super(XY_ui_interface, self).__init__()
		self.setupUi(MainWindow)
		self.get_config(file_cfg)
		self.set_ui_signal()
		self.serial = serial.Serial()
		self.start_flag = threading.Event()
		self.sender_thread = None
		self.sending_buffer = Queue()
		self.recieving_buffer = Queue()

	def get_config(self, file_cfg):
		self.__config = ConfigParser.ConfigParser()
		self.__config.read(file_cfg)

	def set_ui_signal(self):
		self.set_list_serial_port()
		self.Circle_button.clicked.connect(self.Command_circle)
		self.Line_button.clicked.connect(self.Command_line)
		self.Go_to_position_button.clicked.connect(self.Command_goto_position)
		self.Grap_pen_button.clicked.connect(self.Command_Grap_pen)
		self.Get_position_button.clicked.connect(self.Command_get_position)
		self.Reset_button.clicked.connect(self.Command_reset)
		self.Connect_button.clicked.connect(self.Connect_SerialPort)
		self.Send_Package_button.clicked.connect(self.send_custom_package)
		# self.Serial_port_combo.activated.connect(self.set_list_serial_port)
		self.Go_to_position_free.clicked.connect(self.Free_position)
		self.Grap_pen_free.clicked.connect(self.Free_Grap_pen)
		self.moveX_CW.clicked.connect( lambda x:self.Command_move('x', 'CW'))
		self.moveX_CCW.clicked.connect( lambda x:self.Command_move('x', 'CCW'))
		self.breakX.clicked.connect( lambda x:self.Command_break('x'))
		self.moveY_CW.clicked.connect( lambda x:self.Command_move('y', 'CW'))
		self.moveY_CCW.clicked.connect( lambda x:self.Command_move('y', 'CCW'))
		self.breakY.clicked.connect( lambda x:self.Command_break('y'))
		self.moveZ_up.clicked.connect( lambda x:self.Command_move('z', 'up'))
		self.moveZ_down.clicked.connect( lambda x:self.Command_move('z', 'down'))
		self.breakZ.clicked.connect( lambda x:self.Command_break('z'))
		self.breakAll.clicked.connect( self.Command_breakAll )
		self.active_gripper.clicked.connect( lambda x:self.Command_gripper('active') )
		self.release_gripper.clicked.connect( lambda x:self.Command_gripper('release') )

	def connect_serial_port(self):
		self.set_list_serial_port()
		self.start_flag.clear()
		if self.sender_thread is not None and self.sender_thread.is_alive():
			print "waiting..."
			self.sender_thread.join()
		del self.sender_thread
		with self.sending_buffer.mutex:
			self.sending_buffer.queue.clear()
		with self.recieving_buffer.mutex:
			self.recieving_buffer.queue.clear()
		self.serial.port = str( self.Serial_port_combo.currentText() )
		self.serial.setDTR(False)
		self.serial.setRTS(False)
		self.serial.baudrate = 115200
		self.serial.open()

		self.sender_thread = Serilal_sender(self.serial, "Serial Thread", self.sending_buffer, self.recieving_buffer, flag=self.start_flag)
		self.sender_thread.start()
		self.start_flag.set()

		if self.serial.is_open:
			self.Connect_button.setText(_translate("MainWindow", "Disconnect", None))
			print "Connect,",self.serial.is_open
		else:
			print "Fail to connect."
	def disconnect_serial_port(self):
		self.start_flag.clear()
		if self.sender_thread is not None and self.sender_thread.is_alive():
			print "waiting..."
			self.sender_thread.join()
		with self.sending_buffer.mutex:
			self.sending_buffer.queue.clear()
		with self.recieving_buffer.mutex:
			self.recieving_buffer.queue.clear()
		self.sender_thread = None
		self.serial.close()
		self.set_list_serial_port()
		if not self.serial.is_open:
			self.Connect_button.setText(_translate("MainWindow", "Connect", None))
			print "Disconnect,",self.serial.is_open
		else:
			print "Fail to disconnect."

	def Connect_SerialPort(self):
		if self.serial is None:
			self.serial = serial.Serial()
		if self.serial.is_open:
			self.disconnect_serial_port()
		else:
			self.connect_serial_port()
	
	def set_list_serial_port(self):
		comport_list = self.find_comport()
		self.Serial_port_combo.clear()
		self.Serial_port_combo.addItems(comport_list)
		print 'fuck yeah'

	def find_comport(self):
		'''Lists serial port names

		:raises EnvironmentError:
			On unsupported or unknown platforms
		:returns:
			A list of the serial ports available on the system
		'''
		if sys.platform.startswith('win'):
			ports = ['COM%s' % (i + 1) for i in range(256)]
		elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
			# this excludes your current terminal "/dev/tty"
			ports = glob.glob('/dev/tty[A-Za-z]*')
		elif sys.platform.startswith('darwin'):
			ports = glob.glob('/dev/tty.*')
		else:
			raise EnvironmentError('Unsupported platform')

		result = []
		for port in ports:
			try:
				s = serial.Serial(port)
				s.close()
				result.append(port)
			except (OSError, serial.SerialException):
				pass
		return result
	
	def WriteData(self,INSTRUCTION_PACKET):
		self.sending_buffer.put(INSTRUCTION_PACKET)

	def Command_circle(self):
		x = self.Circle_X.value()
		y = self.Circle_Y.value()
		r = self.Circle_radius.value()
		H_X, L_X = divmod(x, 256)
		H_Y, L_Y = divmod(y, 256)
		H_R, L_R = divmod(r, 256)
		ID = 1
		PACKAGE = [255, 255, ID, 1, H_R, L_R, H_X, L_X, H_Y, L_Y]
		self.WriteData(PACKAGE)
		
	def Command_line(self):
		H_X1, L_X1 = divmod(self.Line_X1.value(), 256)
		H_Y1, L_Y1 = divmod(self.Line_Y1.value(), 256)
		H_X2, L_X2 = divmod(self.Line_X2.value(), 256)
		H_Y2, L_Y2 = divmod(self.Line_Y2.value(), 256)
		ID = 1
		PACKAGE = [255, 255, ID, 5, H_X1, L_X1, H_Y1, L_Y1, H_X2, L_X2, H_Y2, L_Y2]
		self.WriteData(PACKAGE)
		
	def __Command_goto_position(self, X, Y):
		H_X, L_X = divmod(X, 256)
		H_Y, L_Y = divmod(Y, 256)
		ID = 1
		PACKAGE = [255, 255, ID, 7, H_X, L_X, H_Y, L_Y]
		self.WriteData(PACKAGE)

	def __Command_Grap_pen(self, X, Y):
		H_X, L_X = divmod(X, 256)
		H_Y, L_Y = divmod(Y, 256)
		ID = 1
		PACKAGE = [255, 255, ID, 6, H_X, L_X, H_Y, L_Y]
		self.WriteData(PACKAGE)

	def Command_goto_position(self):
		self.__Command_goto_position(self.Position_X.value(), self.Position_Y.value())
		
	def Command_Grap_pen(self):
		self.__Command_Grap_pen(self.Grap_pen_X.value(), self.Grap_pen_Y.value())
		
	def Command_get_position(self):
		ID = 1
		PACKAGE = [255, 255, ID, 8]
		self.WriteData(PACKAGE)
		
	def Command_reset(self):
		ID = 1
		PACKAGE = [255, 255, ID, 0]
		self.WriteData(PACKAGE)
		
	def send_custom_package(self):
		PACKAGE = []
		for i in range(1,13):
			value = getattr(self, "Byte"+str( i )).value()
			if value == -1:
				break
			PACKAGE.append(value)
		self.WriteData(PACKAGE)
		
	def Free_position(self):
		img = np.zeros((1080, 1080), dtype = np.uint8) + 255
		ax = plt.gca()
		fig = plt.gcf()
		implot  = ax.imshow(img, cmap = 'gray')
		def onclick(event):
			print "click", int(event.xdata), int(event.ydata)
			self.__Command_goto_position(int(event.xdata), int(event.ydata))
		cid = fig.canvas.mpl_connect('button_press_event', onclick)
		plt.show()

	def Free_Grap_pen(self):
		img = np.zeros((1080, 1080), dtype = np.uint8) + 255
		ax = plt.gca()
		fig = plt.gcf()
		implot  = ax.imshow(img, cmap = 'gray')
		def onclick(event):
			print "click", int(event.xdata), int(event.ydata)
			self.__Command_Grap_pen(int(event.xdata), int(event.ydata))
			time.sleep(0.1)
		cid = fig.canvas.mpl_connect('button_press_event', onclick)
		plt.show()

	def Command_move(self, axis, direction):
		print "Moving",axis,direction
		motor_axis = self.axis_dict[axis]
		motor_direction = self.direction[direction]
		ID = 1
		PACKAGE = [255,255,ID,motor_axis,2,0,motor_direction]
		self.WriteData(PACKAGE)

	def Command_break(self, axis):
		print "Break",axis
		motor_axis = self.axis_dict[axis]
		ID = 1
		PACKAGE = [255,255,ID,12,motor_axis]
		self.WriteData(PACKAGE)

	def Command_breakAll(self):
		self.Command_break('x')
		time.sleep(0.1)
		self.Command_break('y')
		time.sleep(0.1)
		self.Command_break('z')
		time.sleep(0.1)

	def Command_gripper(self, action):
		print "gripper", action


if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	MainWindow = QtGui.QMainWindow()
	ui = XY_ui_interface(MainWindow, "development.cfg")
	MainWindow.show()
	sys.exit(app.exec_())