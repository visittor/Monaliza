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
			ksize = 2*self.ui.Threshold_ksize_median_blur.value() + 1
			if len(img.shape) > 2:
				img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			cv2.medianBlur(img, ksize, img)
			thr = cv2.adaptiveThreshold( img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)
			return thr
		return img

class Sharpening(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "Sharpening", ui = ui)

	def apply(self, img):
		if self.ui.is_Sharpening.isChecked():
			ksize = 2*self.ui.Sharpening_ksize.value() + 1
			weight = float(self.ui.Sharpening_weight.value()) / 100.0
			img_blur = np.zeros( img.shape, dtype = np.uint8)
			cv2.GaussianBlur(img, (ksize,ksize), 0.0, img_blur)
			cv2.addWeighted(img, 1.0 + weight, img_blur, -weight, 0, img)
			return img
		return img

def filter_factory(ui):
	filter_manager = Filter_manager()

	gaussian_filter = Guassian_blur(ui = ui)
	threshold = Threshold(ui = ui)
	sharpening = Sharpening(ui = ui)

	filter_manager.append_filter(gaussian_filter)
	filter_manager.append_filter(threshold)
	filter_manager.append_filter(sharpening)

	return filter_manager