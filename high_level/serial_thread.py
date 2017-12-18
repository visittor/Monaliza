import threading
import sys
import glob
import serial
import time

import numpy as np
import cv2
from Queue import Queue, Full, Empty
from Coor2Dto3Dtransformation import Project2Dto3D, getPsuedoInvPMatAndCpoint, Project2Dto3D_, Project3Dto2D
from send_trajectory import finding_line

def read_data(serial, Lock = None):
	if serial is None:
		return []
	STATUS_PACKET = []
	try:
		# ser.port = str( self.Serial_port_combo.currentText() )
		if not serial.is_open:
			print "Serial port is not open."
		elif serial.is_open:
			# if Lock is not None:
			# 	Lock.acquire()
			while serial.inWaiting():
				STATUS_PACKET.append(ord(serial.read()))
			# if Lock is not None:
			# 	Lock.release()
			if len(STATUS_PACKET) > 0:
				print "RECIEVE<< ",STATUS_PACKET
	except Exception as e:
		print e
	finally:
		return STATUS_PACKET

def write_data(serial, INSTRUCTION_PACKET, Lock = None):
	if serial is None:
		return
	try: 
		if not serial.is_open:
			print "Serial port is not open."
		elif serial.is_open and len(INSTRUCTION_PACKET) > 0:
			INSTRUCTION_PACKET.insert(4, len(INSTRUCTION_PACKET)-3)
			CHKSUM = 0
			for i in range(2, len(INSTRUCTION_PACKET)):
				CHKSUM += INSTRUCTION_PACKET[i]
			CHKSUM %= 256
			INSTRUCTION_PACKET.append(255-CHKSUM)
			# if Lock is not None:
			# 	Lock.acquire()
			serial.write(INSTRUCTION_PACKET)
			# if Lock is not None:
			# 	Lock.release()
			print "SEND>> ",INSTRUCTION_PACKET
	except Exception as e:
		print e
		print "Fail to send ", INSTRUCTION_PACKET

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
					[20*t**3,12*t**2,    6*t,      2,      0,      0],]).astype( np.float32 )
	rMat = np.array([0, 0, 0, R, 0, 0]).reshape(-1,1)
	invM = np.linalg.inv(M)
	coeffs = np.dot(invM, rMat.astype( np.float32 )).reshape(-1)
	return coeffs

class Serilal_sender(threading.Thread):

	def __init__(self, serial, thread_name, sending_buffer, recieving_buffer,flag = None,threadLock = None):
		super(Serilal_sender, self).__init__()
		self.serial = serial
		self.thread_name = thread_name
		self.flag  = flag
		self.sending_buffer = sending_buffer
		self.recieving_buffer = recieving_buffer
		self.threadLock = threadLock

	def ReadData(self):
		Reading_packet = read_data(self.serial, Lock = self.threadLock)
		if len(Reading_packet) == 0:
			return
		try:
			self.recieving_buffer.put(Reading_packet)
		except Full as e:
			print e

	def WriteData(self):
		try:
			if self.sending_buffer.empty():
				return
			Sending_packet = self.sending_buffer.get()
			write_data(self.serial, Sending_packet, Lock = self.threadLock)
			self.sending_buffer.task_done()
		except Empty as e:
			print e
		
	def run(self):
		print "running"
		self.flag.wait()
		while self.flag is not None and self.flag.is_set():
			self.WriteData()
			time.sleep(0.05)
			self.ReadData()
			time.sleep(0.05)
		print "ending"

class FSM_sender(threading.Thread):
	class STATE_ENUM(object):
		SENDING = 0
		RECIEVE = 1
		ERROR = 2

		HEADER1 = 100
		HEADER2 = 101
		ID = 102
		LENGHT = 103
		INST = 104
		DATA_BYTE = 105
		ERROR_BYTE = 106
		CHECKSUM = 107

		def __init__(self):
			self.__currentState = self.SENDING
			self.__currentStateMax = 3
			self.__packetState = self.HEADER1
			self.__packetStateMax = 7

		def Add_currentState(self, State_name):
			setattr(self, State_name, self.__currentStateMax)
			self.__currentStateMax += 1

		def Add_packetState(self, State_name):
			setattr(self, State_name, 100+self.__packetStateMax)
			self.__packetStateMax += 1

		@property
		def currentState(self):
			return self.__currentState
		@currentState.setter
		def currentState(self, x):
			if x > 99:
				pass
			else:
				self.__currentState = x
		@property
		def packetState(self):
			return self.__packetState
		@packetState.setter
		def packetState(self, x):
			if x < 100:
				pass
			else:
				self.__packetState = x

	def __init__(self, thread_name, sending_buffer, recieving_buffer, pen_position,flag = None):
		super(FSM_sender, self).__init__()
		self.thread_name = thread_name
		self.sending_buffer = sending_buffer
		self.recieving_buffer = recieving_buffer
		self.flag = flag
		self.mtx = None
		self.dist = None
		self.rvec = None
		self.tvec = None
		self.camera_shape = None
		self.pseudoInvPMat = None
		self.CPoint = None

		self.contour = None
		self.color = None
		self.contour_shape = None

		self.STATE = FSM_sender.STATE_ENUM()
		self.STATE.currentState = self.STATE.SENDING
		self.STATE.packetState = self.STATE.HEADER1

		self.pen_position = pen_position

		self.__status_packet = []
		self.__dataByte = 0x00
		self.__dataBytes = []
		self.__packageLenght = 0

	def recieving_handler(self, id = 0x01):
		try:
			message = self.recieving_buffer.get(timeout = 1)
		except Empty as e:
			message = []
		self.__status_packet.extend(message)
		# print "recieve packet", self.__status_packet
		while len(self.__status_packet) > 0 :
			self.__dataByte = self.__status_packet.pop(0)
			# print "RECIEVE:", self.__dataByte
			if self.STATE.packetState == self.STATE.HEADER1:
				if self.__dataByte == 0xFF:
					# print "To HEADER2"
					self.STATE.packetState = self.STATE.HEADER2
				else:
					self.STATE.packetState = self.STATE.HEADER1

			elif self.STATE.packetState == self.STATE.HEADER2:
				if self.__dataByte == 0xFF:
					# print "To ID"
					self.STATE.packetState = self.STATE.ID
				else:
					self.STATE.packetState = self.STATE.HEADER1

			elif self.STATE.packetState == self.STATE.ID:
				if self.__dataByte == id:
					# print "To LENGHT"
					self.STATE.packetState = self.STATE.INST
				else:
					self.STATE.packetState = self.STATE.HEADER1

			elif self.STATE.packetState == self.STATE.INST:
				self.__dataBytes.append(self.__dataByte)
				self.STATE.packetState = self.STATE.LENGHT

			elif self.STATE.packetState == self.STATE.LENGHT:
				self.__packageLenght = self.__dataByte
				# print "LENGHT = ",self.__packageLenght
				self.STATE.packetState = self.STATE.DATA_BYTE
			
			elif self.STATE.packetState == self.STATE.DATA_BYTE:
				self.__dataBytes.append(self.__dataByte)
				self.__packageLenght -= 1
				print self.__packageLenght, "REMAIN"
				if self.__packageLenght == 0:
					return True, self.__dataBytes
		return False, []

	# def state_handler(self, *arg, Command_handler = lambda *x:list(x), recieving_handler = self.recieving_handler, instruction = 200, error = 0x83, id = 0x01):
	def state_handler(self, *arg, **kwarg):
		Command_handler = kwarg.get('Command_handler', lambda *x:list(x))
		recieving_handler = kwarg.get('recieving_handler', self.recieving_handler)
		instruction = kwarg.get('instruction', 200)
		error = kwarg.get('error', 0x83)
		id = kwarg.get('id', 0x01)
		if self.STATE.currentState == self.STATE.SENDING:
			self.STATE.currentState = self.STATE.RECIEVE
			package = Command_handler(*arg)
			# print "Sending Command:", package
			self.sending_buffer.put(package)

		elif self.STATE.currentState == self.STATE.RECIEVE:
			ret, data = recieving_handler(id = id)
			if ret:
				if data[0] == instruction:
					# if data[1] & error != 0x00:
					# 	self.STATE.currentState = self.STATE.ERROR
					# 	return False, data
					# else:
					# 	return True, data
					time.sleep(1)
					return True, data
		elif self.STATE.currentState == self.STATE.ERROR:
			print "ERROR:"
			self.STATE.currentState = self.STATE.SENDING
		time.sleep(0.1)
		return False, []

	def get_camera_matrix(self, camera_matrix_holder):
		self.mtx = camera_matrix_holder.mtx
		self.dist = camera_matrix_holder.dist
		self.camera_shape = camera_matrix_holder.shape
		self.tvec = camera_matrix_holder.tvec
		self.rvec = camera_matrix_holder.rvec
		self.pseudoInvPMat, self.CPoint = getPsuedoInvPMatAndCpoint(self.tvec, self.rvec, self.mtx)

	def get_contour(self, contour_holder):
		self.contour_shape = contour_holder.shape
		self.color = contour_holder.color
		self.contour = [ c.reshape(-1,2) for c in contour_holder.contour]

	def prepare_contour(self):
		if self.contour is None or self.camera_shape is None or self.contour_shape is None:
			return
		elif (self.camera_shape == self.contour_shape).all():
			return

		for i in range(len(self.contour)):
			self.contour[i][:,0] = (self.contour[i][:,0].astype(float) * (self.camera_shape[1].astype(float) / self.contour_shape[1].astype(float))).astype(int)
			self.contour[i][:,1] = (self.contour[i][:,1].astype(float) * (self.camera_shape[0].astype(float) / self.contour_shape[0].astype(float))).astype(int)

	def initialize(self):
		self.STATE.currentState = self.STATE.SENDING
		self.STATE.packetState = self.STATE.HEADER1
		self.__status_packet = []
		self.__dataByte = 0x00
		self.__dataBytes = []
		self.__packageLenght = 0

	def run(self):
		''' Override this function pleaseeeeee'''
		self.flag.wait()
		while self.flag is None or self.flag.is_set():
			pass

class StateEnum(object):
	stateEnum = {'pid':0, 'reset':1, 'pull':2, 'push':3, 'draw_line':4, 'draw_circle':5}
	def __init__(self):
		for name,val in self.stateEnum.items():
			setattr(self, name, val)