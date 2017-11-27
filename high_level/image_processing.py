import cv2
import numpy as np 
import threading
from matplotlib import pyplot as plt

class ImageProcessing(threading.Thread):
	
	__filter_manager = None
	
	def __init__(self, start_flag = None, is_arrayFile = None, ui = None, config = None):
		threading.Thread.__init__(self)
		self.ui = ui
		self.__edges_detection_module = Edge_detection(ui, config = config)
		self.__contour_point = np.array([])
		self.__hierarchy = np.array([])
		self.__image = np.zeros([480,640])
		self.__tween = None
		self.__start_flag = start_flag
		self.__is_arrayFile = is_arrayFile
		self.__configure(config)

	def __configure(self, config):
		self.__config = config

	def clear_image(self):
		self.__image = np.zeros([480,640])

	def set_roi(self, roi):
		self.__edges_detection_module.set_roi(roi)

	def recieve_image(self, img):

		self.__image = img

	def recieve_image_from_filename(self, file_name):
		with self.ui.Lock:
			img = cv2.imread(file_name)
			self.recieve_image(img)
			plt.subplot(311)
			plt.hist(img[:,:,0].ravel(),256,[0,256])
			plt.subplot(312)
			plt.hist(img[:,:,1].ravel(),256,[0,256])
			plt.subplot(313)
			plt.hist(img[:,:,2].ravel(),256,[0,256])
			plt.show()

	def recieve_contour_from_filename(self, file_name):
		shape = self.__edges_detection_module.load_countour(file_name)
		self.__image = np.zeros(shape, dtype = np.uint8)

	def attach_tween(self, funtion_):
		self.__edges_detection_module.attach_tween(funtion_)

	def attach_filter(self, filter_manager):
		self.__filter_manager = filter_manager

	def apply_filter(self, img):
		return self.__filter_manager.apply(img)

	def save_contour(self, path):
		self.__edges_detection_module.save_contour(path, self.__image.shape)

	def show_contour(self):
		img = np.zeros([self.__image.shape[0], self.__image.shape[1]], dtype = np.uint8)
		cnts = self.__edges_detection_module.contour
		if self.ui.milestone2.isChecked():
			self.__edges_detection_module.identify_polygons(cnts, img)
		if self.ui.MileStone3Show_lebels.isChecked():
			self.__edges_detection_module.lebel_color(img)
		cv2.drawContours(img, cnts, -1, 255, 1)
		cv2.imshow("contour", img)

	def show_img(self, img):
		cv2.imshow("image", img)

	def identify_color(self):
		self.__edges_detection_module.identify_color(self.__image)


	def save_image(self, image):
		img = np.zeros([self.__image.shape[0], self.__image.shape[1]], dtype = np.uint8)
		cnts = self.__edges_detection_module.contour
		if self.ui.milestone2.isChecked():
			self.__edges_detection_module.identify_polygons(cnts, img)
		if self.ui.MileStone3Show_lebels.isChecked():
			self.__edges_detection_module.lebel_color(img)
		cv2.drawContours(img, cnts, -1, 255, 1)
		cv2.imwrite("out_im.jpg", image)
		cv2.imwrite("out_edge.jpg", img)

	def run(self):
		if self.__start_flag is None:
			self.__start_flag = self.artificial_flag()
		if self.__is_arrayFile is None:
			self.__is_arrayFile = self.artificial_flag()
		self.__start_flag.wait()
		print 'start loop'
		while self.__start_flag is None or self.__start_flag.is_set():
			if self.__is_arrayFile.is_set() == False:
				img = self.__image.copy()
				img = self.apply_filter(img)
				self.__edges_detection_module.update_img(img)
				self.show_img(img)

			self.show_contour()
			if cv2.waitKey(1)&0xFF == 27:
				break
			elif cv2.waitKey(1)&0xFF == ord('s'):
				print "s"
				self.save_image(img)
				
		cv2.destroyWindow("image")
		cv2.destroyWindow("contour")
		print "Leave thread"
		cv2.waitKey(10)
		return 0

	class artificial_flag(object):

		def __init__(self):
			pass

		def is_set(self):
			return False

		def wait(self):
			pass

class Filter(object):
	def __init__(self, name, ui = None, config = None):
		self.__name = name
		self.ui = ui

	@property
	def name(self):
		return name

	def apply(img):
		pass

	def set_ui(self, ui):
		self.__ui = ui

class Filter_manager(object):

	def __init__(self, config = None):
		self.__filters = []

	def append_filter(self, filter_):
		self.__filters.append(filter_)

	def swap_filter_position(self, filter_name, pos):
		index = 0
		for i in range(len(self.__filters)):
			if self.__filters[i].name == filter_name:
				index = i
				break
		else:
			filter_ = self.__filters.pop(index)
			self.__filters = self.__filters[:pos] + [filter_] + self.__filters[pos:]

	def apply(self, img):
		for filter_ in self.__filters:
			img = filter_.apply(img)
		return img

class Edge_detection(object):

	class __color (object):
		def __init__(self, value, name = "Unknown"):
			self.__value = value
			self.__name = name
		def findDistanceRGB (self, value):
			return numpy.linalg.norm(self.__value - self.value)
		def findDistanceLAB (self, value):
			return numpy.linalg.norm(self.__value - self.value)
		def findDistanceHSV (self, value):
			value = self.RGB2HSV(value)
			return np.abs(value[0] - self.__value[0]) if np.abs(value[0] - self.__value[0]) < 90 else np.abs(180 - np.abs(value[0] - self.__value[0]))
		@staticmethod
		def RGB2HSV(value):
			hsv = cv2.cvtColor(np.uint8([[value]]), cv2.COLOR_BGR2HSV)[0][0]
			# val = value/max(value)
			# v = max(val)
			# s = (v - min(val))/v if v != 0 else 0
			# h = 60*(val[1] - val[0])/(v - min(val)) if v == val[2] else 120 + 60*(val[0]-val[2])/(v-min(val)) if v == val[1] else 240 + 60*(val[2]-val[1])/(v-min(val))
			# h = h+360 if h < 0 else h
			# return (h/2,255*s,255*v,0)
			return hsv
		@property
		def value(self):
			return self.__value
		@property
		def name(self):
			return self.__name

	def __init__(self, ui, config = None):
		self.__ui = ui
		self.__edges = np.zeros( (480, 640), dtype = np.uint8)
		self.__contour_points = np.array([])
		self.__hierarchy = np.array([])
		self.__color_array = np.array([])
		self.__color_array_border = np.array([])
		self.__color_dict = {-1:self.__color([1000,1000,1000])}
		self.__tween = None
		self.__configuration(config)
		self.__roi = np.zeros((640, 480), dtype = np.uint8) + 255

	def __configuration(self, config):
		self.__config = config
		if self.__config is not None:
			for n,value in enumerate (self.__config.items("color")):
				indx = self.__config.getint("color_index", value[0])
				self.__color_dict[indx] = self.__color (eval(value[1]), name = value[0])
		else:
			self.__color_dict[0] = self.__color ([0,0,0])

	def set_roi(self, roi):
		self.__roi = roi.copy()

	def update_img(self, img):
		self.__edges = cv2.Canny(img.copy(), self.__ui.lower_thr_edges.value(), self.__ui.upper_thr_edges.value(), apertureSize = 3, L2gradient =True)
		self.__find_contour()

	def attach_tween(self, tween):
		self.__tween = tween

	def __find_contour(self):
		if self.__roi is not None:
			shape0 = self.__roi.shape[0] if self.__roi.shape[0] < self.__edges.shape[0] else self.__edges.shape[0]
			shape1 = self.__roi.shape[1] if self.__roi.shape[1] < self.__edges.shape[1] else self.__edges.shape[1]
			self.__edges[:shape0, :shape1] = cv2.bitwise_and(self.__edges[:shape0,:shape1], self.__roi[:shape0,:shape1])
			# self.__edges[:shape0, :shape1] = ((self.__edges[:shape0,:shape1].astype(np.uint16) * self.__roi[:shape0,:shape1].astype(np.uint16))/255).astype(np.uint8)
		self.__edges = self.__tween(self.__edges) if callable(self.__tween) else self.__edges
		if self.__ui.retr_external.isChecked():
			retrieval_mode = cv2.RETR_EXTERNAL
		else:
			retrieval_mode = cv2.RETR_TREE
		c = cv2.findContours( self.__edges, retrieval_mode, cv2.CHAIN_APPROX_SIMPLE)
		cnts_filtered = self.__filter_contour(c[1])
		if self.__ui.is_arc_lenght.isChecked():
			for i in range(len(cnts_filtered)):
				epsilon = float((self.__ui.epsilon.value())*cv2.arcLength(cnts_filtered[i],True))/1000.0
				cnts_filtered[i] = cv2.approxPolyDP(cnts_filtered[i],epsilon,True)
			self.__contour_points = cnts_filtered
		elif self.__ui.is_cnt_step.isChecked():
			self.__contour_points = [ np.array(i[::self.__ui.cnt_step.value()]) for i in cnts_filtered if len(i[::self.__ui.cnt_step.value()]) > 1]
			# print self.__contour_points[0].shape
			# print self.__contour_points[0].reshape(-1,2).shape
		else:
			self.__contour_points = cnts_filtered
		self.__hierarchy = c[2]

	def __filter_contour(self, cnts):
		return [ np.array(i) for i in cnts if self.__ui.cnt_max_lenght.value()>= len(i) >= self.__ui.cnt_min_lenght.value()]

	def identify_polygons(self, cnts, img):
		for cnt in cnts:
			self.__identify_polygon(cnt, img)

	def __identify_polygon(self, cnt, img):
		i = 0
		indx_list = range(0, len(cnt))
		while i < len(indx_list):
			j = i+1
			while j < len(indx_list):
				if np.linalg.norm(cnt[indx_list[i]] - cnt[indx_list[j]]) <= self.__ui.milestone2maxlenght.value():
					indx_list.pop(j)
				else:
					j += 1
			i += 1
		n = str(len(indx_list)) if len(indx_list) <= self.__ui.milestone2maxpolygon.value() else "circle"
		M = cv2.moments(cnt)
		cx = int(M['m10']/M['m00']) if M['m00'] != 0 else 0
		cy = int(M['m01']/M['m00']) if M['m00'] != 0 else 0
		cv2.putText(img, n+"("+str(cx)+","+str(cy)+")",(cx,cy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5,255,1,cv2.LINE_AA)

	# def identify_color(self, img):
	# 	self.__color_array = np.zeros(len(self.__contour_points)) - 1
	# 	for i in range(0,len(self.__contour_points)):
	# 		mask = np.zeros(img.shape[:2], np.uint8) 
	# 		cv2.drawContours(mask, self.__contour_points, i, 255, -1)
	# 		mean = cv2.mean(img, mask = mask)
	# 		min_dist = 300
	# 		min_index = -1
	# 		for j,k in self.__color_dict.items():
	# 			m = k.findDistanceHSV(np.array(mean).astype(np.uint8))
	# 			if min_dist > m:
	# 				min_dist = m
	# 				min_index = j
	# 		print min_dist, min_index, self.__color.RGB2HSV(np.array(mean)), i
	# 		self.__color_array[i] = min_index
	# 	print self.__color_array
	# 	print "finish"

	def identify_color(self, img):
		self.__color_array = np.zeros(len(self.__contour_points)) - 1
		self.__color_array_border = np.zeros(len(self.__contour_points)) - 1
		for i in range(0,len(self.__contour_points)):
			mask = np.zeros(img.shape[:2], np.uint8) 
			border = np.zeros(img.shape[:2], np.uint8)
			cv2.drawContours(mask, self.__contour_points, i, 255, -1)
			cv2.drawContours(border, self.__contour_points, i, 255, 2)
			mean = cv2.mean(img, mask = mask)
			mean_border = cv2.mean(img, mask = border)
			min_dist = 300
			min_index = -1
			for j,k in self.__color_dict.items():
				m = k.findDistanceHSV(np.array(mean).astype(np.uint8))
				if min_dist > m:
					min_dist = m
					min_index = j
			min_dist_border = 300
			min_index_border = -1
			for j,k in self.__color_dict.items():
				m = k.findDistanceHSV(np.array(mean_border).astype(np.uint8))
				if min_dist_border > m:
					min_dist_border = m
					min_index_border = j
			print min_index, min_index_border, self.__color.RGB2HSV(np.array(mean_border)), i
			self.__color_array[i] = min_index
			self.__color_array_border[i] = min_index_border
		print self.__color_array
		print "finish"

	def lebel_color(self, img):
		if len(self.__color_array) == len(self.__contour_points):
			for i,cnt in enumerate(self.__contour_points):
				M = cv2.moments(cnt)
				cx = int(M['m10']/M['m00']) if M['m00'] != 0 else 0
				cy = int(M['m01']/M['m00']) if M['m00'] != 0 else 0
				color = self.__color_dict[self.__color_array[i]].name 
				color_boder = self.__color_dict[self.__color_array_border[i]].name
				cv2.putText(img, color+" "+color_boder+" "+str(i), (cx,cy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, 255, 1, cv2.LINE_AA)

	def set_contour(self, contour, hierarchy, color, border_color):
		self.__contour_points = contour
		self.__hierarchy = hierarchy
		self.__color_array = color
		self.__color_array_border = border_color

	def save_contour(self, path, shape):
		shape = np.array(shape)[:2]
		contour = self.__contour_points
		hierarchy = self.__hierarchy
		color = self.__color_array
		border_color = self.__color_array_border
		np.savez(path, shape = shape, contour = contour, hierarchy = hierarchy, color = color, border_color = border_color)

	def load_countour(self, path):
		with np.load( path ) as data:
			contour = data['contour']
			hierarchy = data['hierarchy'].copy()
			shape = data['shape']
			try:
				color = data['color']
			except Exception as e:
				color = np.zeros(len(contour))
				print e
			try:
				border_color = data['border_color']
			except Exception as e:
				border_color = np.zeros(len(contour))
		self.set_contour(contour, hierarchy, color, border_color)
		return shape

	@property
	def edges(self):
		return self.__edges.copy()

	@property
	def contour(self):
		return self.__contour_points	

	@property
	def color_array(self):
		return self.__color_array

	@property 
	def color_dict (self):
		return self.__color_dict	