import cv2
import numpy as np
from matplotlib import pyplot as plt

import time
from PyQt4 import QtCore, QtGui
from serial_ui import Ui_MainWindow
from serial_thread import Serilal_sender
from FSM_sender import Line_sender, Circle_sender,BasicPattern,GripperPattern
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

class XY_ui_interface(QtGui.QMainWindow, Ui_MainWindow):
	axis_dict = {'x':9, 'y':10, 'z':11}
	direction = {'CCW':0, 'CW':1, 'up':0, 'down':1}
	gripper_action = {'pull':2, 'push':3,'grap':4, 'degrap':5}

	class Camera_matrix_holder(object):
		def __init__(self, shape, mtx, dist, rvec, tvec):
			self._shape = shape
			self._mtx = mtx
			self._dist = dist
			self._rvec = rvec
			self._tvec = tvec

		def reinitial(self, shape, mtx, dist, rvec, tvec):
			self._shape = shape
			self._mtx = mtx
			self._dist = dist
			self._rvec = rvec
			self._tvec = tvec

		@property
		def shape(self):
			return self._shape.copy()
		@property
		def mtx(self):
			return self._mtx.copy()
		@property
		def dist(self):
			self._dist.copy()
		@property
		def rvec(self):
			return self._rvec.copy()
		@property
		def tvec(self):
			return self._tvec.copy()

	class Contour_Holder(object):
		def __init__(self, contour, hierarchy, shape, color):
			self._contour = contour
			self._shape = shape
			self._color = color

		def reinitial(self, contour, hierarchy, shape, color):
			self._contour = contour
			self._shape = shape
			self._color = color
		
		@property
		def contour(self):
			return self._contour.copy()
		@property
		def shape(self):
			return self._shape.copy()
		@property
		def color(self):
			return self._color.copy()

	def __init__(self, MainWindow, file_cfg):
		super(XY_ui_interface, self).__init__()
		self.setupUi(MainWindow)
		self.Pen_position = {}
		self.get_config(file_cfg)
		self.set_ui_signal()
		self.serial = serial.Serial(rtscts=False,dsrdtr=False)
		self.start_flag = threading.Event()
		self.FSM_start_flag = threading.Event()
		self.sender_thread = None
		self.FSM_sender = None
		self.sending_buffer = Queue()
		self.recieving_buffer = Queue()
		self.camera_matrix_holder = XY_ui_interface.Camera_matrix_holder(None, None, None, None, None)
		self.contour_holder = XY_ui_interface.Contour_Holder(None, None, None, None)

	def get_config(self, file_cfg):
		self.__config = ConfigParser.ConfigParser()
		self.__config.read(file_cfg)
		for value in self.__config.items("color_index"):
			indx = int(value[1])
			pos = eval(self.__config.get("color_position", value[0]))
			self.Pen_position[indx] = pos

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

		self.pullButton.clicked.connect( lambda x:self.Command_gripper('pull') )
		self.pushButton.clicked.connect( lambda x:self.Command_gripper('push') )
		self.grapButton.clicked.connect( lambda x:self.Command_gripper('grap') )
		self.degrapButton.clicked.connect( lambda x:self.Command_gripper('degrap') )

		self.TunePID_button.clicked.connect(self.Command_tune_PID)
		self.TuneTrajX_button.clicked.connect(self.Command_tune_TrajX)
		self.TuneTrajY_button.clicked.connect(self.Command_tune_TrajY)
		self.TuneCircle_buttonX.clicked.connect(self.Command_tune_CirX)
		self.TuneCircle_buttonY.clicked.connect(self.Command_tune_CirY)

		self.Load_camera_matrix_button.clicked.connect( self.Load_camera_matrix)
		self.Load_contour_button.clicked.connect(self.Load_contour)
		self.start_button.clicked.connect(self.START)
		self.kill_button.clicked.connect(self.KILL)
		self.threadLock = threading.Lock()

	def connect_serial_port(self):
		self.start_flag.clear()
		self.FSM_start_flag.clear()
		if self.sender_thread is not None and self.sender_thread.is_alive():
			print "waiting..."
			self.sender_thread.join()
		with self.sending_buffer.mutex:
			self.sending_buffer.queue.clear()
		with self.recieving_buffer.mutex:
			self.recieving_buffer.queue.clear()
		self.serial.port = str( self.Serial_port_combo.currentText() )
		print self.serial.port
		# self.serial.port = str( 'COM5' )
		self.serial.baudrate = 115200
		self.serial.setDTR(False)
		self.serial.setRTS(False)
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
		self.FSM_start_flag.clear()
		if self.sender_thread is not None and self.sender_thread.is_alive():
			print "waiting..."
			self.sender_thread.join()
		with self.sending_buffer.mutex:
			self.sending_buffer.queue.clear()
		with self.recieving_buffer.mutex:
			self.recieving_buffer.queue.clear()
		self.serial.setDTR(False)
		self.serial.setRTS(False)
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
				s = serial.Serial(port,rtscts=False,dsrdtr=False)
				s.setDTR(False)
				s.setRTS(False)
				s.close()
				result.append(port)
			except (OSError, serial.SerialException):
				pass
		return result
	
	def WriteData(self,INSTRUCTION_PACKET):
		self.sending_buffer.put(INSTRUCTION_PACKET)

	def Command_circle(self):
		R = self.Circle_R.value()
		theta = self.Circle_theta.value()
		T = self.Circle_T.value()
		ID = 1
		H_R,L_R = divmod( int(R),256)
		sign = 0x00
		H_theta, L_theta = divmod( int(theta), 256 )
		H_T, L_T = divmod(int(T),256)
		PACKET = [255, 255, 1, 250, H_R, L_R, H_T, L_T, H_theta, L_theta, sign]
		self.WriteData(PACKET)
		
	def Command_line(self):
		R = self.Line_R.value()
		theta = float(self.Line_theta.value()) / 100.0
		T = self.Line_T.value()
		H_R,L_R = divmod( int(R),256)
		sign = 0x00
		cosTheta = np.cos(theta)*100
		if cosTheta < 0 :
			cosTheta = -1*cosTheta
			sign += 1
		sinTheta = np.sin(theta)*100
		if sinTheta < 0 :
			sinTheta = -1*sinTheta
			sign += 2

		H_T, L_T = divmod(int(T),256)
		print "sin:", sinTheta, "cos:",cosTheta
		PACKAGE = [255, 255, 1, 200, H_R, L_R, H_T, L_T, int(cosTheta), int(sinTheta),sign]
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
		img = np.zeros((350, 350), dtype = np.uint8) + 255
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
		PACKAGE = [255,255,ID,motor_axis,0x09,0xC4,motor_direction]
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

	def __Command_tune_PID(self, axis, kp, ki, kd):
		kp_H, kp_L = divmod(kp, 100)
		ki_H, ki_L = divmod(ki, 100)
		kd_H, kd_L = divmod(kd, 100)
		PACKAGE = [255, 255, 0x01, 55, axis, kp_H, kp_L, ki_H, ki_L, kd_H, kd_L]
		self.WriteData(PACKAGE)

	def Command_tune_PID(self):
		if self.PID_Yaxis.isChecked():
			self.__Command_tune_PID(1, self.PID_Kp.value(), self.PID_Ki.value(), self.PID_Kd.value())
		else:
			self.__Command_tune_PID(0, self.PID_Kp.value(), self.PID_Ki.value(), self.PID_Kd.value())

	def __Command_tune_Traj(self, Ins, axis, a, kp, kd, ki):
		a_H, a_L = divmod(a, 256)
		kp_H, kp_L = divmod(kp, 256)
		kd_H, kd_L = divmod(kd, 256)
		PACKAGE = [255,255,0x01,Ins,axis,a_H,a_L,kp_H,kp_L,kd_H,kd_L,ki]
		self.WriteData(PACKAGE)

	def Command_tune_TrajX(self):
		# axis = 1 if self.Traj_Yaxis.isChecked() else 0
		# ins = 57 if self.Traj_Circle.isChecked() else 56
		self.__Command_tune_Traj(56, 0, self.TrajX_a.value(), self.TrajX_Kp.value(), self.TrajX_Kd.value(), self.TrajX_Ki.value())

	def Command_tune_TrajY(self):
		self.__Command_tune_Traj(56, 1, self.TrajY_a.value(), self.TrajY_Kp.value(), self.TrajY_Kd.value(), self.TrajY_Ki.value())

	def Command_tune_CirX(self):
		self.__Command_tune_Traj(57, 0, self.TrajCirX_a.value(), self.TrajCirX_Kp.value(), self.TrajCirX_Kd.value(), self.TrajCirX_Ki.value())

	def Command_tune_CirY(self):
		self.__Command_tune_Traj(57, 1, self.TrajCirY_a.value(), self.TrajCirY_Kp.value(), self.TrajCirY_Kd.value(), self.TrajCirY_Ki.value())

	def Command_gripper(self, action):
		PACKAGE = [255, 255, 2, self.gripper_action[action]]
		self.WriteData(PACKAGE)

	def Load_camera_matrix(self):
		filename = str( QtGui.QFileDialog.getOpenFileName(self, 'Open File') )
		with np.load( filename ) as data:
			shape = data['shape']
			mtx = data['camera_matrix']
			dist = data['distortion_ceff']
			rvecs = data['rotation_vector']
			tvecs = data['translation_vector']
			planar_index = data['planar_index']
			rvec = rvecs[planar_index[0]]
			tvec = tvecs[planar_index[0]]
			print "Load successful"
		self.camera_matrix_holder.reinitial(shape, mtx, dist, rvec, tvec)

	def Load_contour(self):
		filename = str( QtGui.QFileDialog.getOpenFileName(self, 'Open File') )
		with np.load( filename ) as data:
			contour = data['contour']
			hierarchy = data['hierarchy'].copy()
			shape = data['shape']
			try:
				color = data['color']
				print "Load successful"
			except Exception as e:
				color = np.zeros(len(contour))
				print e
		self.contour_holder.reinitial(contour, hierarchy, shape, color)

	def START(self):
		if self.sender_thread is None or not self.sender_thread.is_alive():
			print "sender thread is not alive please connect serial port."
			return
		elif not self.serial.is_open:
			print "Serial port is not open."
			return
		self.FSM_start_flag.clear()
		if self.FSM_sender is not None and self.FSM_sender.is_alive():
			self.FSM_sender.join()
		with self.sending_buffer.mutex:
			self.sending_buffer.queue.clear()
		with self.recieving_buffer.mutex:
			self.recieving_buffer.queue.clear()
		self.FSM_sender = None
		if self.Line_option.isChecked():
			self.FSM_sender = Line_sender( self.sending_buffer, self.recieving_buffer, self.camera_matrix_holder, self.contour_holder, self.Pen_position, flag = self.FSM_start_flag)
		elif self.Circle_option.isChecked():
			self.FSM_sender = Circle_sender(self.sending_buffer, self.recieving_buffer, self.camera_matrix_holder, self.contour_holder, self.Pen_position, flag = self.FSM_start_flag)
		elif self.Test_option.isChecked():
			self.FSM_sender = BasicPattern("Testing Thread", self.sending_buffer, self.recieving_buffer, self.Pen_position, flag = self.FSM_start_flag)
		elif self.TestGripper_option.isChecked():
			self.FSM_sender = GripperPattern("Test Gripper Thread", self.sending_buffer, self.recieving_buffer, self.Pen_position, flag = self.FSM_start_flag)
		elif self.Circle_option.isChecked():
			self.FSM_sender = Circle_sender(self.sending_buffer, self.recieving_buffer, self.camera_matrix_holder, self.contour_holder, self.Pen_position, flag = self.FSM_start_flag)

		if self.FSM_sender is not None:
			self.FSM_sender.start()
			self.FSM_start_flag.set()

	def KILL(self):
		self.FSM_start_flag.clear()
		if self.FSM_sender is not None and self.FSM_sender.is_alive():
			self.FSM_sender.join()
		with self.sending_buffer.mutex:
			self.sending_buffer.queue.clear()
		with self.recieving_buffer.mutex:
			self.recieving_buffer.queue.clear()
		self.FSM_sender = None

if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	MainWindow = QtGui.QMainWindow()
	ui = XY_ui_interface(MainWindow, "development.cfg")
	MainWindow.show()
	sys.exit(app.exec_())