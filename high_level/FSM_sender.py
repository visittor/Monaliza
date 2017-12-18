from serial_thread import *
import numpy as np
import cv2
import time
from Queue import Queue, Full, Empty
from Coor2Dto3Dtransformation import Project2Dto3D, getPsuedoInvPMatAndCpoint, Project2Dto3D_, Project3Dto2D
from send_trajectory import finding_line
from test_infill import infill_polygon

class BasicPattern(FSM_sender):

	def __init__(self, Name, sending_buffer, recieving_buffer, pen_position, flag = None):
		super(BasicPattern, self).__init__(Name, sending_buffer, recieving_buffer, pen_position, flag = flag)
		self.__error = 0x00
		self.__dataByte = 0x00
		self.__status_packet = []
		self.__packageLenght = 0x00
		self.__dataBytes = []

	def Command_Grap_pen(self, pen_indx):
		H_X, L_X = divmod(self.pen_position[pen_indx][0], 256)
		H_Y, L_Y = divmod(self.pen_position[pen_indx][1], 256)
		ID = 1
		PACKAGE = [255, 255, ID, 6, H_X, L_X, H_Y, L_Y]
		return PACKAGE

	def Command_Go_to_position(self, x, y):
		H_X, L_X = divmod(x, 256)
		H_Y, L_Y = divmod(y, 256)
		ID = 1
		PACKAGE = [255, 255, ID, 1, H_X, L_X, H_Y, L_Y]
		return PACKAGE

	def Command_Draw_line(self, R, theta, T):
		ID = 1
		H_R,L_R = divmod( int(R),256)
		sign = 0x00
		cosTheta = np.cos(theta)*100
		sinTheta = np.sin(theta)*100
		print theta, cosTheta, sinTheta
		if cosTheta < 0 :
			cosTheta = -1*cosTheta
			sign += 1
		if sinTheta < 0 :
			sinTheta = -1*sinTheta
			sign += 2
		H_T, L_T = divmod(int(T),256)
		PACKET = [255, 255, 1, 4, H_R, L_R, sign, int(sinTheta), int(cosTheta)]
		return PACKET

	def Command_Draw_circle(self, R, theta, T):
		ID = 1
		H_R,L_R = divmod( int(R),256)
		sign = 0x00
		H_theta, L_theta = divmod( int(theta), 256 )
		H_T, L_T = divmod(int(T),256)
		PACKET = [255, 255, 1, 5, H_R, L_R, H_theta, L_theta]
		return PACKET

	def Command_Reset(self):
		PACKET = [255,255,1,3]
		return PACKET

	def go_to_position(self, x, y):
		return super(BasicPattern, self).state_handler(int(x),int(y),Command_handler=self.Command_Go_to_position,instruction = 1)
		# if self.STATE.currentState == self.STATE.SENDING:
		# 	print "Send Command Go To Position."
		# 	self.STATE.currentState = self.STATE.RECIEVE
		# 	package = self.Command_Go_to_position(x,y)
		# 	self.sending_buffer.put(package)
		# elif self.STATE.currentState == self.STATE.RECIEVE:
		# 	ret, data = self.recieving_handler()
		# 	if ret and len(data)>=2:
		# 		if data[0] == 7:
		# 			if data[1] & 0x83 != 0x00:
		# 				self.STATE.currentState = self.STATE.ERROR
		# 				return False, data
		# 			else:
		# 				return True, data
		# 		else:
		# 			pass
		# elif self.STATE.currentState == self.STATE.ERROR:
		# 	print "ERROR:"
		# 	self.STATE.currentState = self.STATE.SENDING
		# return False, []

	def grap_penState(self, indx):
		return super(BasicPattern, self).state_handler(x,y,Command_handler=self.Command_Grap_pen,instruction = 6)
		# if self.STATE.currentState == self.STATE.SENDING:
		# 	print "Sending Command Grappen Index:", indx
		# 	self.STATE.currentState = self.STATE.RECIEVE
		# 	package = self.Command_Grap_pen(indx)
		# 	self.sending_buffer.put(package)

		# elif self.STATE.currentState == self.STATE.RECIEVE:
		# 	ret,data = self.recieving_handler()
		# 	if ret and len(data) >= 2:
		# 		if data[0] == 6:
		# 			if data[1] & 0x83 != 0x00:
		# 				self.STATE.currentState = self.STATE.ERROR
		# 				return False, data
		# 			else:
		# 				return True, data
		# 		else:
		# 			pass
		# elif self.STATE.currentState == self.STATE.ERROR:
		# 	print "ERROR:"
		# 	self.STATE.currentState = self.STATE.SENDING
		# return False,[]

	def draw_line(self, R, theta, T):
		return super(BasicPattern, self).state_handler(int(R), theta, int(T), Command_handler=self.Command_Draw_line,instruction = 1)
		# if self.STATE.currentState == self.STATE.SENDING:
		# 	print "Sending Command Draw Line:"
		# 	self.STATE.currentState = self.STATE.RECIEVE
		# 	package = self.Command_Draw_line(R, theta, T)
		# 	self.sending_buffer.put(package)

		# elif self.STATE.currentState == self.STATE.RECIEVE:
		# 	ret, data = self.recieving_handler()
		# 	if ret and len(data) >= 2:
		# 		if data[0] == 200:
		# 			if data[1] & 0x83 != 0x00:
		# 				self.STATE.currentState = self.STATE.ERROR
		# 				return False, data
		# 			else:
		# 				return True, data
		# elif self.STATE.currentState == self.STATE.ERROR:
		# 	print "ERROR:"
		# 	self.STATE.currentState = self.STATE.SENDING
		# return False, []

	def draw_circle(self, R, theta, T):
		return super(BasicPattern, self).state_handler(int(R), theta, int(T),Command_handler=self.Command_Draw_circle,instruction = 1)
		# if self.STATE.currentState == self.STATE.SENDING:
		# 	print "Sending Command Draw Circle:"
		# 	self.STATE.currentState = self.STATE.RECIEVE
		# 	package = self.Command_Draw_circle(R, theta, T)
		# 	self.sending_buffer.put(package)

		# elif self.STATE.currentState == self.STATE.RECIEVE:
		# 	ret, data = self.recieving_handler()
		# 	if ret and len(data) >= 2:
		# 		if data[0] == 250:
		# 			if data[1] & 0x83 != 0x00:
		# 				self.STATE.currentState = self.STATE.ERROR
		# 				return False, data
		# 			else:
		# 				return True, data
		# elif self.STATE.currentState == self.STATE.ERROR:
		# 	print "ERROR:"
		# 	self.STATE.currentState = self.STATE.SENDING
		# return False, []

	def reset_position(self):
		return super(BasicPattern, self).state_handler(Command_handler=self.Command_Reset,instruction = 2)

	def initialize(self):
		super(BasicPattern, self).initialize()
		self.__dataByte = 0x00
		self.__status_packet = []
		self.__error = 0x00
		self.__packageLenght = 0x00
		self.__dataBytes = []

	def run(self):
		self.initialize()
		flag = False
		x = 100
		y = 100
		self.flag.wait()
		while self.flag.is_set():
			if not flag:
				flag,_ = self.go_to_position(x + 100,y + 100)
				if flag:
					print flag
					self.initialize()
					x = (x+100)%300
					y = (y+100)%300
					flag = False
			else:
				print "Complete..."
				break
		print "Leave Thread"

class GripperPattern(FSM_sender):
	def __init__(self, Name, sending_buffer, recieving_buffer, pen_position, flag = None):
		super(GripperPattern, self).__init__(Name, sending_buffer, recieving_buffer, pen_position, flag = flag)
		# self.__error = 0x00
		# self.__dataByte = 0x00
		# self.__status_packet = []
		# self.__packageLenght = 0x00
		# self.__dataBytes = []

	def Command_Pull(self):
		packet = [255,255,2,3]
		return packet

	def Command_Push(self):
		packet = [255,255,2,5]
		return packet

	def Command_Grap(self):
		packet = [255,255,2,4]
		return packet

	def Command_Degrap(self):
		packet = [255,255,2,7]
		return packet

	def pull_Gripper(self):
		return super(GripperPattern, self).state_handler(Command_handler=self.Command_Pull,instruction = 2, id = 0x02)

	def push_Gripper(self):
		return super(GripperPattern, self).state_handler(Command_handler=self.Command_Push,instruction = 3, id = 0x02)

	def grap_Gripper(self):
		return super(GripperPattern, self).state_handler(Command_handler=self.Command_Grap,instruction = 4, id = 0x02)

	def degrap_Gripper(self):
		return super(GripperPattern, self).state_handler(Command_handler=self.Command_Degrap,instruction = 5, id =0x02)

	def run(self):
		self.initialize()
		flag = 0
		self.flag.wait()
		while self.flag.is_set():
			if flag == 0:
				ret,_ = self.pull_Gripper()
				time.sleep(7)
			elif flag == 1:
				ret,_ = self.push_Gripper()
				time.sleep(7)
			elif flag == 2:
				ret,_ = self.pull_Gripper()
				time.sleep(7)
			elif flag == 3:
				ret,_ = self.grap_Gripper()
				time.sleep(12)
			elif flag == 4:
				ret,_ = self.pull_Gripper()
				time.sleep(7)
			elif flag == 5:
				ret,_ = self.degrap_Gripper()
				time.sleep(12)
			ret = True
			if ret:
				flag = (flag+1)%4
				self.initialize()
		print "Leave Thread"

class Line_sender(GripperPattern,BasicPattern,FSM_sender):
	stateEnum = {"pull":0, "push":1, "to_pos":2, "draw_line":3}
	def __init__(self, sending_buffer, recieving_buffer, camera_matrix_holder, contour_holder, pen_position,flag = None):
		super(Line_sender, self).__init__("Line_sender", sending_buffer, recieving_buffer, pen_position, flag = flag)
		super(Line_sender, self).get_camera_matrix(camera_matrix_holder)
		super(Line_sender, self).get_contour(contour_holder)
		super(Line_sender, self).prepare_contour()
		self.polygon = None
		self.polygon_world_coor = None
		self.trajectory = []
		self.__status_packet = []
		self.__data_byte = 0x00
		self.__error = 0x00
		self.__currentCoeff = None

		self.polyState = self.stateEnum["pull"]

		self.infill_line = None
		self.infill_line_world = None

	def get_line(self):
		self.polygon = finding_line( self.contour )
		self.infill_line = infill_polygon([self.polygon.reshape(-1,1,2).copy()], shape = self.camera_shape, step = 20)[0]
		self.infill_line_world = Project2Dto3D_(self.infill_line.astype(np.float32), self.pseudoInvPMat, self.CPoint)[:,::-1]

	def prepare_coordinate( self ):
		self.polygon_world_coor = Project2Dto3D_(self.polygon.copy(), self.pseudoInvPMat, self.CPoint)
		self.polygon_world_coor = self.polygon_world_coor[:,::-1]

	def prepare_trajectory(self):
		self.trajectory = []
		for i,p1 in enumerate(self.polygon_world_coor):
			p2 = self.polygon_world_coor[(i+1)%len(self.polygon_world_coor)]
			R = np.linalg.norm(p2 - p1)
			theta = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])
			T = (120.0 / 134.0) * R
			self.trajectory.append([R,theta,T])

	def prepare_infill(self):
		self.infillCoeff = []
		for i, p1 in enumerate(self.infill_line_world):
			p2 = self.infill_line_world[(i+1)%len(self.infill_line_world)]
			R = np.linalg.norm(p2 - p1)
			theta = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])
			T = (120.0 / 134.0)*R
			self.infillCoeff.append([R,theta,T])

	def verify_coor( self ):
		point_verify = Project3Dto2D(self.polygon_world_coor.copy(), self.tvec, self.rvec, self.mtx)
		diff = np.abs(point_verify - self.polygon.astype( np.float32 ))
		print "error x,y respect to square size : ",np.mean(diff, axis = 0)
		# img = np.zeros(self.camera_shape, dtype = np.uint8)
		img = cv2.imread("vis.jpg",0)
		for i,p in enumerate(self.polygon):
			cv2.line(img, tuple(p.astype(int)), tuple(self.polygon[(i+1)%len(self.polygon)].astype(int)), 255, 2)
			cv2.putText(img, str(self.polygon_world_coor[i]), tuple(p.astype(int)), cv2.FONT_HERSHEY_PLAIN, 0.75, 255, 1)
			cv2.putText(img, str(self.polygon_world_coor[(i+1)%len(self.polygon)]), tuple(point_verify[(i+1)%len(self.polygon)].astype(int)), cv2.FONT_HERSHEY_PLAIN, 0.75, 255, 1)
		cv2.imshow("img", img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def create_packet_traj(self, coeffs):
		ID = 1
		H_R,L_R = divmod( int(coeffs[0]),256)
		sign = 0x00
		cosTheta = np.cos(coeffs[1])*1000
		Hcos, Lcos = divmod(int(cosTheta), 256)
		if cosTheta < 0 :
			cosTheta = -1*cosTheta
			sign += 1
		sinTheta = np.sin(coeffs[1])*1000
		Hsin, Lsin = divmod(int(sinTheta), 256)
		if sinTheta < 0 :
			sinTheta = -1*sinTheta
			sign += 2
		H_T, L_T = divmod(int(coeffs[2]),256)
		PACKET = [255, 255, 1, 200, H_R, L_R, H_T, L_T, Hcos, Lcos, Hsin, Lsin, sign]
		return PACKET

	def create_packet_PID(self, x,y):
		H_x,L_x = divmod(int(x), 256)
		H_y,L_y = divmod(int(y), 256)
		PACKET = [255,255,1,7, H_x, L_x, H_y, L_y]
		return PACKET

	def initialize(self):
		super(Line_sender, self).initialize()
		self.__status_packet = []
		self.__data_byte = []
		self.__error = []

	def drawPolyState(self):
		if self.polyState == self.stateEnum["pull"]:
			ret,_ = self.pull_Gripper()
			if ret:
				if len(self.trajectory) == 0:
					self.initialize()
					return True
				self.initialize()
				self.polyState = self.stateEnum["to_pos"]
		elif self.polyState == self.stateEnum["push"]:
			ret,_ = self.push_Gripper()
			if ret:
				self.initialize()
				self.polyState = self.stateEnum["draw_line"]
		elif self.polyState == self.stateEnum["to_pos"]:
			ret,_ = self.go_to_position(self.polygon_world_coor[0][0] , self.polygon_world_coor[0][1] - 9)
			if ret:
				self.polyState = self.stateEnum["push"]
				self.initialize()
				self.__currentCoeff = self.trajectory.pop(0)
		elif self.polyState == self.stateEnum["draw_line"]:
			ret,_ = self.draw_line(*self.__currentCoeff)
			if ret:
				if len(self.trajectory) == 0:
					self.polyState = self.stateEnum["pull"]
					self.initialize()
				else:
					self.__currentCoeff = self.trajectory.pop(0)
					self.initialize()
		return False

	def drawInfillState(self):
		if self.polyState == self.stateEnum["pull"]:
			ret,_ = self.pull_Gripper()
			if ret:
				if len(self.infillCoeff) == 0:
					return True
				self.initialize()
				self.polyState = self.stateEnum["to_pos"]
		elif self.polyState == self.stateEnum["push"]:
			ret,_ = self.push_Gripper()
			if ret:
				self.initialize()
				self.polyState = self.stateEnum["draw_line"]
		elif self.polyState == self.stateEnum["to_pos"]:
			ret,_ = self.go_to_position(self.infill_line_world[0][0] , self.infill_line_world[0][1] - 9)
			if ret:
				self.polyState = self.stateEnum["push"]
				self.initialize()
				self.__currentCoeff = self.infillCoeff.pop(0)
		elif self.polyState == self.stateEnum["draw_line"]:
			ret,_ = self.draw_line(*self.__currentCoeff)
			if ret:
				if len(self.infillCoeff) == 0:
					self.polyState = self.stateEnum["pull"]
					self.initialize()
				else:
					self.__currentCoeff = self.infillCoeff.pop(0)
					self.initialize()
		return False

	def run(self):
		self.get_line()
		self.prepare_coordinate()
		self.verify_coor()
		self.prepare_trajectory()
		self.prepare_infill()
		self.initialize()
		# stateEnum = {"pull":0, "push":1, "to_pos":2, "draw_line":3}
		state = False
		self.flag.wait()
		while self.flag.is_set():
			if not state:
				state = self.drawPolyState()
			elif self.drawInfillState():
				break
		print "Stop..."

class Circle_sender(GripperPattern,BasicPattern,FSM_sender):
	stateEnum = {'c':0, 'pll':1, 'psh':2, 'pid':3}
	def __init__(self, sending_buffer, recieving_buffer, camera_matrix_holder, contour_holder, pen_position, flag = None):
		super(Circle_sender, self).__init__("Circle_sender", sending_buffer, recieving_buffer, pen_position, flag = flag)
		super(Circle_sender, self).get_camera_matrix(camera_matrix_holder)
		super(Circle_sender, self).get_contour(contour_holder)
		super(Circle_sender, self).prepare_contour()
		self.polygon_world_coor = None
		self.polygon = None
		self.infill_line = None
		self.infill_line_world = None
		self.R = 0
		self.Center = None
		self.topMost = None
		self.bottomMost = None
		self.RightMost = None
		self.LeftMost = None

		self.circle_state = self.stateEnum['pll']

	def find_infill(self):
		self.infill_line = infill_polygon([self.polygon.reshape(-1,1,2).copy()], shape = self.camera_shape, step = 20)[0]
		self.infill_line_world = Project2Dto3D_(self.infill_line.astype(np.float32), self.pseudoInvPMat, self.CPoint)[:,::-1]
		print self.infill_line_world

	def draw_infill(self, img, infill):
		for i in range(0, len(infill) - 1):
			cv2.line(img, tuple(infill[i]), tuple(infill[i+1]), (0,255,255), 3)

	def prepare_coordinate( self ):
		A = 0
		indx = 0
		for i,cnt in enumerate(self.contour):
			area = cv2.contourArea(cnt)
			if area > A:
				indx = i
				A = area
		self.polygon = self.contour[indx].reshape(-1,2)
		self.find_infill()
		self.polygon_world_coor = Project2Dto3D_(self.polygon.astype(np.float32).copy(), self.pseudoInvPMat, self.CPoint)[:,::-1]
		ArgSortX = np.argsort(self.polygon_world_coor[:,0])
		ArgSortY = np.argsort(self.polygon_world_coor[:,1])
		self.topMost = self.polygon_world_coor[ArgSortY[-1]]
		self.bottomMost = self.polygon_world_coor[ArgSortY[0]]
		self.RightMost = self.polygon_world_coor[ArgSortX[-1]]
		self.LeftMost = self.polygon_world_coor[ArgSortX[0]]
		Dia1 = np.linalg.norm(self.topMost - self.bottomMost)
		Dia2 = np.linalg.norm(self.RightMost - self.LeftMost)
		# center = (self.topMost + self.bottomMost + self.RightMost + self.LeftMost) / 4
		center = np.mean(self.infill_line_world, axis = 0)
		self.RightMost = center
		self.R = (Dia2 + Dia1)/4 - 0
		self.RightMost[0] += self.R
		self.Center = center
		print self.R
		print "center:", center

	def verify_coor( self ):
		center_ver = Project3Dto2D([self.Center[::-1]], self.tvec, self.rvec, self.mtx).astype(int)[0]
		top = Project3Dto2D([self.topMost[::-1]], self.tvec, self.rvec, self.mtx).astype(int)
		bottom = Project3Dto2D([self.bottomMost[::-1]], self.tvec, self.rvec, self.mtx).astype(int)[0]
		right = Project3Dto2D([self.RightMost[::-1]], self.tvec, self.rvec, self.mtx).astype(int)[0]
		left = Project3Dto2D([self.LeftMost[::-1]], self.tvec, self.rvec, self.mtx).astype(int)[0]
		infill_Ver = Project3Dto2D(self.infill_line_world[:,::-1], self.tvec, self.rvec, self.mtx).astype(int)
		dia1 = np.linalg.norm(top - bottom)
		dia2 = np.linalg.norm(right - left)
		r_ver = (dia1 + dia2) / 4
		vis = cv2.imread("test.jpg")
		self.draw_infill(vis, infill_Ver)
		cv2.circle(vis, tuple(center_ver), int(r_ver), (0,255,255), 4)
		cv2.circle(vis, tuple(center_ver), 3, (0,0,255), -1)
		cv2.imshow("vis", vis)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def circle_FSM(self):
		if self.circle_state == self.stateEnum['pll']:
			ret,_ = self.pull_Gripper()
			if ret:
				self.circle_state = self.stateEnum['pid']
				self.initialize()
		elif self.circle_state == self.stateEnum['pid']:
			ret,_ = self.go_to_position(int(self.RightMost[0]), int(self.RightMost[1]))
			if ret:
				self.circle_state = self.stateEnum['psh']
				self.initialize()
		elif self.circle_state == self.stateEnum['psh']:
			ret,_ = self.push_Gripper()
			if ret:
				self.circle_state = self.stateEnum['c']
				self.initialize()
		elif self.circle_state == self.stateEnum['c']:
			ret,_ = self.draw_circle(self.R, 628, (self.R/75.0)*1000)
			if ret:
				self.initialize()
				return True
		return False

	def prepare_trajectory(self):
		self.trajectory = []
		for i,p1 in enumerate(self.infill_line_world[:-1]):
			p2 = self.infill_line_world[(i+1)%len(self.infill_line_world)]
			R = np.linalg.norm(p2 - p1)
			theta = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])
			T = (85.0 / 134.0) * R
			self.trajectory.append([R,theta,T])
		# print self.trajectory

	def infill_state(self, coeff):
			ret,_ = self.draw_line(*coeff)

	def initialize(self):
		super(Circle_sender, self).initialize()

	def run(self):
		self.prepare_coordinate()
		self.verify_coor()
		self.prepare_trajectory()
		self.initialize()
		self.circle_state = self.stateEnum['pll']
		firstInfill = True
		drawInfill = False
		push = True
		coeff = None
		self.flag.wait()
		while self.flag.is_set():
			if not drawInfill:
				drawInfill = self.circle_FSM()
			elif drawInfill:
				if not push:
					ret,_ = self.push_Gripper()
					if ret:
						push = True
						self.initialize()
					continue
				if firstInfill:
					ret,_ = self.go_to_position(int(self.infill_line_world[0][0]), int(self.infill_line_world[0][1]))
					if ret:
						self.initialize()
						push =False
						firstInfill = False
						coeff = self.trajectory.pop()
						with self.sending_buffer.mutex:
							self.sending_buffer.queue.clear()
						with self.recieving_buffer.mutex:
							self.recieving_buffer.queue.clear()
						print "coeff:",coeff
				else:
					ret,_ = self.draw_line(*coeff)
					if ret:
						if len(self.trajectory) == 0:
							self.initialize()
							break
						coeff = self.trajectory.pop()
						self.initialize()
		while self.flag.is_set():
			ret,_ = self.pull_Gripper()
			if ret:
				break
		print "Stop ..."