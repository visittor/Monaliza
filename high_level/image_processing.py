import cv2
import numpy as np 
import threading

class ImageProcessing(threading.Thread):
	
	__filter_manager = None
	
	def __init__(self, start_flag = None):
		threading.Thread.__init__(self)
		self.__contour_point = np.array([])
		self.__hierarchy = np.array([])
		self.__image = np.zeros([480,640])
		self.__tween = None
		self.__start_flag = start_flag

	def recieve_image(self, img):
		self.__image = img

	def recieve_image_from_filename(self, file_name):
		img = cv2.imread(file_name)
		self.recieve_image(img)

	def attach_filter(self, filter_manager):
		self.__filter_manager = filter_manager

	def apply_filter(self, img):
		return self.__filter_manager.apply(img)

	def edge_detect(self, img, lowerThr, upperThr):
		edges = cv2.Canny(img.copy(),lowerThr,upperThr,apertureSize = 3)
		return edges

	def attach_tween(self, function_):
		self.__tween = function_

	def create_contour(self, edges):
		c = cv2.findContours( edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		self.__contour_point = c[1]
		self.__hierarchy = c[2]

	def draw_contour(self, img, step):
		for i in self.__contour_point:
			for j in range (step, len(i), step):
				cv2.line(img,(i[j,0,0],i[j,0,1]),(i[j-step,0,0],i[j-step,0,1]),255,1)

	def show_contour(self, step):
		img = np.zeros([self.__image.shape[0], self.__image.shape[1]], dtype = np.uint8)
		self.draw_contour(img, step)
		cv2.imshow("contour", img)

	def show_img(self, img):
		cv2.imshow("image", img)

	def run(self):
		if self.__start_flag is not None:
			self.__start_flag.wait()
		while self.__start_flag is None or self.__start_flag.is_set():
			img = self.__image.copy()
			img = self.apply_filter(img)
			edges = self.edge_detect(img, 0, 10)
			# edges = self.__tween(edges) if self.__tween is not None else edges
			self.create_contour(edges)
			self.show_contour(1)
			self.show_img(img)
			cv2.waitKey(1)
		cv2.destroyAllWindows()

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

	__filters = []

	def __init__(self):
		pass

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