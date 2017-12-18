from serial_thread import *
import numpy as np
import cv2
import time
from Queue import Queue, Full, Empty
from Coor2Dto3Dtransformation import Project2Dto3D, getPsuedoInvPMatAndCpoint, Project2Dto3D_, Project3Dto2D
from FSM_sender import BasicPattern, GripperPattern

class ContourSender(GripperPattern, BasicPattern, FSM_sender):

	def __init__(self, sending_buffer, recieving_buffer, contour_holder, flag = None, CntIndx = 0, PtIndx = 0):
		super(ContourSender, self).__init__("ContourSender", sending_buffer, recieving_buffer, None, flag = flag)
		self.get_contour(contour_holder)
		self.prepare_contour()
		self.CntIndx = CntIndx
		self.PtIndx = PtIndx
		self.stateEnum = StateEnum()

	def get_contour(self, contour_holder):
		self.contour_shape = contour_holder.shape 
		self.contour = contour_holder.contour

	def prepare_contour(self):
		ratio = 260.0/float(self.contour_shape[0]) if self.contour_shape[0]>self.contour_shape[1] else 260.0/float(self.contour_shape[1])
		self.contour = [(c*ratio).astype(int) + 20 for c in self.contour]
		# self.contour = [cv2.approxPolyDP(c,0.001*cv2.arcLength(c,True),True) for c in self.contour]

	def verify(self):
		l = 0
		for c in self.contour:
			l += c.shape[0]
		print "total contour =",len(self.contour)
		print "total point =",l
		# print max(self.contour)
		img = np.zeros((300,300), dtype = np.uint8)
		cv2.drawContours(img, self.contour, -1, 255, 1)
		cv2.imshow("img", img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		self.contour = [c.reshape(-1,2) for c in self.contour]

	def get_traj_coeff(self, cnt, pt_indx, p1):
		p2 = cnt[(pt_indx+1)%cnt.shape[0]]
		R = np.linalg.norm(p2 - p1)
		print "R", R
		theta = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])
		return [R,theta,0]

	def get_realPos(self, data):
		print "data",data
		x = (data[1]*256) + data[2]
		y = (data[3]*256) + data[4]
		return np.array([x,y], dtype = int)

	def initialize(self):
		super(ContourSender, self).initialize()

	def run(self):
		self.verify()
		self.initialize()
		self.flag.wait()
		firstPoint = True
		state = self.stateEnum.pull
		cnt = self.contour[self.CntIndx]
		realPosition = np.array([0,0], dtype = int)
		coeff = None
		while self.flag.is_set():
			if self.PtIndx >= cnt.shape[0]:
				self.PtIndx = 0
				self.CntIndx += 1
				if self.CntIndx >= len(self.contour):
					print "Finish ..."
					break
				cnt = self.contour[self.CntIndx]
				firstPoint = True
				state = self.stateEnum.pull
			if firstPoint:
				if state == self.stateEnum.pull:
					ret,_ = self.pull_Gripper()
					time.sleep(7)
					self.initialize()
					state = self.stateEnum.reset
				elif state == self.stateEnum.reset:
					ret,_ = self.reset_position()
					if ret:
						self.initialize()
						state = self.stateEnum.pid
				elif state == self.stateEnum.pid:
					ret,data = self.go_to_position(cnt[self.PtIndx][0], cnt[self.PtIndx][1])
					if ret:
						realPosition = self.get_realPos(data)
						self.initialize()
						state = self.stateEnum.push
				elif state == self.stateEnum.push:
					ret,_ = self.push_Gripper()
					time.sleep(7)
					self.initialize()
					firstPoint = False
					state = self.stateEnum.draw_line
					coeff = self.get_traj_coeff(cnt, self.PtIndx, realPosition)
					# print "Drawing", self.CntIndx, self.PtIndx
			elif not firstPoint:
				if state == self.stateEnum.draw_line:
					ret,data = self.draw_line(*coeff)
					if ret:
						realPosition = self.get_realPos(data)
						self.initialize()
						print "Drawing", self.CntIndx, self.PtIndx
						self.PtIndx += 1
						if self.PtIndx < cnt.shape[0]:
							coeff = self.get_traj_coeff(cnt,self.PtIndx, realPosition)
						
		print "Leaving thread",self.thread_name