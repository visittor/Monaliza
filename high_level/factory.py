import cv2
import numpy as np 

from image_processing import Filter
from image_processing import Filter_manager

class Guassian_blur(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "GaussianBlur", ui = ui)


	def apply(self, img):
		if self.ui.is_GaussianBlur.isChecked():
			ksize = 2*self.ui.GaussianBlur_kSize.value() + 1
			sigma = self.ui.GaussianBlur_sigma.value()
			cv2.GaussianBlur(img.copy(), (ksize,ksize), float(sigma)/10.0, img)
		return img

class Threshold(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "Threshold", ui = ui)

	def apply(self, img):
		if self.ui.is_Threshold.isChecked():
			block_size = 2*self.ui.Threshold_block_size.value() + 1
			c = self.ui.Threshold_c.value()
			thr = cv2.adaptiveThreshold( cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
			return thr
		return img

def filter_factory(ui):
	filter_manager = Filter_manager()

	gaussian_filter = Guassian_blur(ui = ui)
	threshold = Threshold(ui = ui)

	filter_manager.append_filter(gaussian_filter)
	filter_manager.append_filter(threshold)

	return filter_manager