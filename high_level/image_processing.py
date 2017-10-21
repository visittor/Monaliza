import cv2
import numpy as np 
import threading
from matplotlib import pyplot as plt

class ImageProcessing(threading.Thread):
	
	__filter_manager = None
	
	def __init__(self, start_flag = None, is_arrayFile = None, ui = None):
		threading.Thread.__init__(self)
		self.ui = ui
		self.__edges_detection_module = Edge_detection(ui)
		self.__contour_point = np.array([])
		self.__hierarchy = np.array([])
		self.__image = np.zeros([480,640])
		self.__tween = None
		self.__start_flag = start_flag
		self.__is_arrayFile = is_arrayFile

	def clear_image(self):
		self.__image = np.zeros([480,640])

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
		cv2.drawContours(img, cnts, -1, 255, 1)
		cv2.imshow("contour", img)

	def show_img(self, img):
		cv2.imshow("image", img)

	def save_image(self, image):
		img = np.zeros([self.__image.shape[0], self.__image.shape[1]], dtype = np.uint8)
		cnts = self.__edges_detection_module.contour
		if self.ui.milestone2.isChecked():
			self.__edges_detection_module.identify_polygons(cnts, img)
		cv2.drawContours(img, cnts, -1, 255, 1)
		cv2.imwrite("out_im.jpg", image)
		cv2.imwrite("out_edge.jpg", img)

	def run(self):
		if self.__start_flag is None:
			self.__start_flag = self.artificial_flag()
		if self.__is_arrayFile is None:
			self.__is_arrayFile = self.artificial_flag()
		self.__start_flag.wait()
		while self.__start_flag is None or self.__start_flag.is_set():
			# with self.ui.Lock:
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
	def __init__(self, name, ui = None):
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

	def __init__(self):
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

	def __init__(self, ui):
		self.__ui = ui
		self.__edges = np.zeros( (480, 640), dtype = np.uint8)
		self.__contour_points = np.array([])
		self.__hierarchy = np.array([])
		self.__tween = None

	def update_img(self, img):
		self.__edges = cv2.Canny(img.copy(), self.__ui.lower_thr_edges.value(), self.__ui.upper_thr_edges.value(), apertureSize = 3, L2gradient =True)
		self.__find_contour()

	def attach_tween(self, tween):
		self.__tween = tween

	def __find_contour(self):
		self.__edges = self.__tween(self.__edges) if callable(self.__tween) else self.__edges
		c = cv2.findContours( self.__edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		cnts_filtered = self.__filter_contour(c[1])
		if self.__ui.is_arc_lenght.isChecked():
			for i in range(len(cnts_filtered)):
				epsilon = float((self.__ui.epsilon.value())*cv2.arcLength(cnts_filtered[i],True))/1000.0
				cnts_filtered[i] = cv2.approxPolyDP(cnts_filtered[i],epsilon,True)
			self.__contour_points = cnts_filtered
		elif self.__ui.is_cnt_step.isChecked():
			self.__contour_points = [ np.array(i[::self.__ui.cnt_step.value()]) for i in cnts_filtered if len(i[::self.__ui.cnt_step.value()]) > 1]
		else:
			self.__contour_points = cnts_filtered
		self.__hierarchy = c[2]

	def __filter_contour(self, cnts):
		return [ np.array(i) for i in cnts if len(i) >= self.__ui.cnt_min_lenght.value()]

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

	def set_contour(self, contour, hierarchy):
		self.__contour_points = contour
		self.__hierarchy = hierarchy

	def save_contour(self, path, shape):
		shape = np.array(shape)[:2]
		contour = self.__contour_points
		hierarchy = self.__hierarchy
		np.savez(path, shape = shape, contour = contour, hierarchy = hierarchy)

	def load_countour(self, path):
		with np.load( path ) as data:
			contour = data['contour']
			hierarchy = data['hierarchy'].copy()
			shape = data['shape']
		self.set_contour(contour, hierarchy)
		return shape

	@property
	def edges(self):
		return self.__edges.copy()

	@property
	def contour(self):
		return self.__contour_points		