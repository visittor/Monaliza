import numpy as np 
import cv2

def process_image(thread_name, ui):
	img = cv2.imread("caradel_2.jpg")
	out = np.zeros(img.shape[:-1])
	while 1 == 1:
		img = cv2.imread("caradel_2.jpg")
		out = np.zeros(img.shape)
		lowerThr = ui.slider_lowerThr.value()
		upperThr = ui.slider_upperThr.value()
		contourStep = ui.slider_contourStep.value()
		GaussianBlur_kSizeG = 2*ui.dial_GaussianBlur_kSizeG.value()+1
		detailEnhance_sigmaM = ui.dial_detailEnhance_sigmaM.value()
		detailEnhance_sigmaS = ui.dial_detailEnhance_sigmaS.value()
		bilateralFilter_time = ui.dial_bilateralFilter_time.value()
		Laplacian_threshold = ui.dial_Laplacian_threshold.value()
		
		if ui.radioFilter_GaussianBlur.isChecked():
			img = cv2.GaussianBlur(img,(GaussianBlur_kSizeG,GaussianBlur_kSizeG),0)
		if ui.radioFilter_detailEnhance.isChecked():
			img = cv2.detailEnhance(img, sigma_s=detailEnhance_sigmaS, sigma_r=float(detailEnhance_sigmaM)/100)
		if ui.radioFilter_bilateralFilter.isChecked():
			for i in range (bilateralFilter_time):
				img = cv2.bilateralFilter(img,9,5,7)
		if ui.radioFilter_Laplacian.isChecked():
			lapa = cv2.Laplacian(img,cv2.CV_8U, ksize = 5)
			ret,thresh1 = cv2.threshold(lapa,Laplacian_threshold,255,cv2.THRESH_BINARY)
			lapa = cv2.bitwise_and(lapa, thresh1)
			img = np.uint8(img*(255.0 - 1.0*lapa)/255.0)

		edges = cv2.Canny(img.astype(np.uint8),lowerThr,upperThr,apertureSize = 3)

		_, contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		for i in contours:
			for j in range (contourStep,len(i),contourStep):
				cv2.line(out,(i[j,0,0],i[j,0,1]),(i[j-contourStep,0,0],i[j-contourStep,0,1]),255,1)
		
		cv2.imshow("ima", img)
		# cv2.imshow("ima", thresh1)
		cv2.imshow("edge", out)
		k = cv2.waitKey(1)
		if k == 27:
			break

	cv2.destroyAllWindows()

if __name__ == "__main__":
	def nothing(x):
	    pass

	cv2.namedWindow('image')
	cv2.createTrackbar('lower','image',0,500,nothing)
	cv2.createTrackbar('upper','image',0,500,nothing)
	cv2.createTrackbar('k_size','image',1,3,nothing)
	cv2.createTrackbar('k_size_g','image',1,11,nothing)
	cv2.createTrackbar('k_size_b','image',1,100,nothing)
	cv2.createTrackbar('thr', 'image',0,255,nothing)
	cv2.createTrackbar('step', 'image',1,10,nothing)

	img = cv2.imread("mona_lisa.jpg")
	out = np.zeros(img.shape[:-1])
	while 1 == 1:
		img = cv2.imread("mona_lisa.jpg")
		out = np.zeros(img.shape)
		# img = cv2.flip(img,1)
		lower_thr = cv2.getTrackbarPos('lower','image')
		upper_thr = cv2.getTrackbarPos('upper','image')
		k_size = 2*cv2.getTrackbarPos('k_size','image') + 1
		k_size_b = cv2.getTrackbarPos('k_size_b','image')
		k_size_g = 2*cv2.getTrackbarPos('k_size_g','image') + 1
		thr = cv2.getTrackbarPos('thr','image')
		step = cv2.getTrackbarPos('step','image')

		img = cv2.GaussianBlur(img,(k_size_g,k_size_g),0)
		img = cv2.detailEnhance(img, sigma_s=k_size_b, sigma_r=0.1)
		for i in range (k_size_b):
			img = cv2.bilateralFilter(img,9,5,7)
		lapa = cv2.Laplacian(img,cv2.CV_8U, ksize = 5)
		ret,thresh1 = cv2.threshold(lapa,thr,255,cv2.THRESH_BINARY)
		lapa = cv2.bitwise_and(lapa, thresh1)
		img = np.uint8(img*(255.0 - 1.0*lapa)/255.0)

		edges = cv2.Canny(img.astype(np.uint8),lower_thr,upper_thr,apertureSize = k_size)

		_, contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		for i in contours:
			for j in range (step,len(i),step):
				cv2.line(out,(i[j,0,0],i[j,0,1]),(i[j-step,0,0],i[j-step,0,1]),255,1)
		# cv2.drawContours(out, contours, -1,255, 1)
		# edges = cv2.Canny(thresh1,lower_thr,upper_thr,apertureSize = k_size)

		
		cv2.imshow("ima", img)
		# cv2.imshow("ima", thresh1)
		cv2.imshow("edge", out)
		k = cv2.waitKey(1)
		if k == 27:
			break

	cv2.destroyAllWindows()