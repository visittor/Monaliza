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

class Median_blur(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "MedianBlur", ui = ui)

	def apply(self, img):
		if self.ui.is_MedianBlur.isChecked():
			ksize = 2*self.ui.MedianBlur_kSize.value() + 1
			cv2.medianBlur(img, ksize, img)
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

	def unsharp_masking(self, img, ksize, weight):
		img_blur = img_blur = cv2.GaussianBlur(img, (ksize,ksize), 0.0)
		return cv2.addWeighted(img, 1.0 + weight, img_blur, -weight, 0)

	def overlay(self, target, blend, scale = 0.5):
		add_ = np.where(blend >= 127)
		sub_ = np.where(blend < 127)

		blend[sub_] = 255 - blend[sub_]
		blend = blend - 127
		target_add = cv2.addWeighted(target, 1, blend, scale, 0)
		target_sub = cv2.addWeighted(target, 1, blend, -scale, 0)
		target[add_] = target_add[add_]
		target[sub_] = target_sub[sub_]

		return target

	def high_pass_filter(self, img, ksize, weight):
		laplacian = cv2.Laplacian(img, cv2.CV_64F, ksize = ksize, scale = 1, delta = 0)
		laplacian *= (127.0/laplacian.max()) if laplacian.max() > -laplacian.min() else (127.0/(laplacian.min()))
		laplacian += 127
		return self.overlay(img, laplacian.astype(np.uint8), scale = weight)

	def apply(self, img):
		if self.ui.is_Sharpening.isChecked():
			ksize = 2*self.ui.Sharpening_ksize.value() + 1
			weight = float(self.ui.Sharpening_weight.value()) / 100.0
			mode = self.ui.Sharpening_mode.value()
			return self.unsharp_masking(img, ksize, weight) if mode == 0 else self.high_pass_filter(img, ksize, weight) 
		return img

class Grammar(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "Grammar", ui = ui)
		self.__grammar = 1.0
		self.__lookup = np.array([])
		self.__set_lookup()

	def __set_lookup(self):
		self.__lookup = np.array( [ 255.0*((float(i)/255.0)**(self.__grammar)) for i in range(256) ], dtype = np.uint8 )

	def apply(self, img):
		if self.ui.is_Grammar.isChecked():
			if self.ui.Grammar_grammar.value()/100.0 != self.__grammar:
				self.__grammar =  self.ui.Grammar_grammar.value()/100.0
				self.__set_lookup()
			img[:] = self.__lookup[img]
		return img

class StepThreshold(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "StepThreshold", ui = ui)
		self.__condlist = []
		self.__funclist = []
		self.__lookup = np.array([])
		self.__n_inter = 2
		self.__set_lookup()

	def __set_condlist(self):
		interval_ = 256/self.__n_inter
		thr = 0
		self.__condlist = []
		for i in range(self.__n_inter):
			cond = np.array([ True if thr <= ii < thr+interval_ else False for ii in range(256) ], dtype = bool)
			self.__condlist.append(cond)
			thr += interval_

	def __set_funclist(self):
		num_int_ = self.__n_inter - 1
		inter_lenght = 255/num_int_
		value = 0
		self.__funclist = []
		for i in range(self.__n_inter):
			self.__funclist.append(value)
			value += inter_lenght

	def __set_lookup(self):
		self.__set_condlist()
		self.__set_funclist()
		a  = np.array([ i for i in range(256)])
		self.__lookup = np.piecewise(a, self.__condlist, self.__funclist)

	def apply(self, img):
		if self.ui.is_StepThreshold.isChecked():
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) > 2 else img
			if self.ui.StepThreshold_numberOfInterval.value() != self.__n_inter:
				self.__n_inter = self.ui.StepThreshold_numberOfInterval.value() if self.ui.StepThreshold_numberOfInterval.value() > 1 else 2 
				self.__set_lookup()
			img[:] = self.__lookup[img]
		return img

class Bit_cut(Filter):

	def __init__(self, ui = None):
		Filter.__init__(self, "Bit_cut",ui = ui)

	def apply(self, img):
		if self.ui.is_Bit_cut.isChecked():
			mask_ = 255 - ((2**self.ui.Bit_cut_pos.value()) - 1)
			mask = np.zeros(img.shape, dtype = np.uint8) + mask_
			cv2.bitwise_and(img, mask, img)
		return img

class Filter2D(Filter):
	def __init__(self, ui = None):
		Filter.__init__(self, "Filter2D", ui = ui)
		self.__kernel = np.array([[-1,-2,-1],
								 [ 0, 0, 0],
								 [ 1, 2, 1]])
		# self.__kernel = np.ones((5,5), dtype = float)/25.0

	def apply(self, img):
		if self.ui.is_Filter2D.isChecked():
			# self.__kernel = np.ones( (self.ui.Filter2D_para1.value(), self.ui.Filter2D_para1.value()), dtype = float)/float(self.ui.Filter2D_para1.value()**2)
			# thresh = self.ui.Filter2D_para1.value()
			# ret,img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY) 
			img = cv2.Laplacian(img,cv2.CV_64F)
			# cv2.filter2D(img, -1, self.__kernel, img)
		return img

class PencilEffect(Filter):
	def __init__(self, ui = None):
		Filter.__init__(self, "PencilEffect",ui = ui)

	def __color_dodge(self, img, mask):
		return cv2.divide(img, 255 - mask, scale = 256)
		
	def __color_burn(self, img, mask):
		return 255 - cv2.divide(255-img, 255-mask, scale = 256)

	def apply(self, img):
		if self.ui.is_PencilEffect.isChecked():
			ksize = 2*self.ui.PencilEffect_kSize.value() + 1
			img_inv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			img_inv[:,:,1] = 0
			img_inv = cv2.cvtColor(img_inv, cv2.COLOR_HSV2BGR)
			img_inv = 255 - img_inv
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) > 2 else img
			img_inv = cv2.cvtColor(img_inv, cv2.COLOR_BGR2GRAY) if len(img_inv.shape) > 2 else img_inv
			cv2.GaussianBlur(img_inv, (ksize,ksize), 0.0, img_inv)
			img = self.__color_dodge(img, img_inv)
		return img
class ContrashBrightnessAdjustor(Filter):
	def __init__(self, ui = None):
		Filter.__init__(self, "ContrashBrightnessAdjustor",ui = ui)

	def apply(self, img):
		if self.ui.is_ContrashBrightnessAdjustor.isChecked():
			alpha = self.ui.ContrashBrightnessAdjustor_alpha.value()/100.0
			beta = self.ui.ContrashBrightnessAdjustor_beta.value()
			src2 = np.ones(img.shape, dtype = np.uint8)
			img = cv2.addWeighted(img, alpha, src2, beta, 0)
		return img

class BilateralFilter(Filter):
	def __init__(self, ui = None):
		Filter.__init__(self, "BilateralFilter", ui = ui)

	def apply(self, img):
		if self.ui.is_BilateralFilter.isChecked():
			d = self.ui.BilateralFilter_d.value()
			sigmaColor = self.ui.BilateralFilter_sigmaColor.value()
			sigmaSpace = self.ui.BilateralFilter_sigmaSpace.value()
			iterate = self.ui.BilateralFilter_iterate.value()
			for i in range(iterate):
				img = cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)
			return img
		return img

def filter_factory(ui):
	filter_manager = Filter_manager()

	gaussian_filter = Guassian_blur(ui = ui)
	median_blur = Median_blur( ui = ui)
	threshold = Threshold(ui = ui)
	sharpening = Sharpening(ui = ui)
	grammar = Grammar(ui = ui)
	stepthr = StepThreshold(ui = ui)
	bitcut = Bit_cut(ui = ui)
	filter2d = Filter2D(ui = ui)
	pencil_effect = PencilEffect(ui = ui)
	adjust_brighness = ContrashBrightnessAdjustor( ui = ui )
	bilateral = BilateralFilter( ui = ui )

	filter_manager.append_filter(grammar)
	filter_manager.append_filter(bitcut)
	filter_manager.append_filter(gaussian_filter)
	filter_manager.append_filter(median_blur)
	filter_manager.append_filter(bilateral)
	filter_manager.append_filter(pencil_effect)
	filter_manager.append_filter(adjust_brighness)
	filter_manager.append_filter(filter2d)
	filter_manager.append_filter(sharpening)
	filter_manager.append_filter(stepthr)
	filter_manager.append_filter(threshold)
	
	return filter_manager