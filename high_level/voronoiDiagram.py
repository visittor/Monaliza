import numpy as np 
import cv2
import random 
from queue import PriorityQueue

def find_voronoi(points, shape):
	voronoi_diagrame = np.zeros((shape[0],shape[1]), dtype = np.int32) - 1

	q = PriorityQueue()
	for i,p in enumerate(points):
		if 0<=p[0]<shape[0] and 0<=p[1]<shape[1]:
			q.put( (0, list(p), i) )

	counter = 0
	while not q.empty() and counter < voronoi_diagrame.shape[0]*voronoi_diagrame.shape[1]:
		_, pts, indx = q.get()

		if voronoi_diagrame[tuple(pts)] != -1:
			continue

		counter += 1
		voronoi_diagrame[tuple(pts)] = indx

		for pp in get_adjucent(pts):
			if 0<=pp[0]<shape[0] and 0<=pp[1]<shape[1] and voronoi_diagrame[ tuple(pp) ] == -1 :
				d = find_distance(pp, points[indx])
				q.put( (d, list(pp), indx) )
	return voronoi_diagrame

def get_adjucent(pts):
	a = np.array( [ [-1,0], [1,0], [0,-1], [0,1] ] )
	return pts + a

def find_distance(p1, p2):
	return max( np.abs(p1 - p2) )

def find_centroid(voronoi, numpoint, pdf_img):
	m  = np.zeros(numpoint, dtype = float)
	mx = np.zeros(numpoint, dtype = float)
	my = np.zeros(numpoint, dtype = float)
	for i in range(numpoint):
		indx = np.where( voronoi == i )
		m[i]  = np.sum( pdf_img[indx] )
		mx[i] = np.sum( indx[1]*pdf_img[indx] )
		my[i] = np.sum( indx[0]*pdf_img[indx] )
	indx_non_zero = np.where(m != 0)
	centroid = np.zeros( (len(indx_non_zero[0]), 2), dtype = int )
	print centroid.shape, my[indx_non_zero].shape
	centroid[:, 0] = (my[indx_non_zero] / m[indx_non_zero]).astype(int)
	centroid[:, 1] = (mx[indx_non_zero] / m[indx_non_zero]).astype(int)
	return centroid

if __name__ == '__main__':

	import time

	img = np.zeros( (480,640,3), dtype = np.uint8) + 1	
	pts = np.array( [ [img.shape[0]*random.random(), img.shape[1]*random.random()] for i in range(600) ], dtype = int )

	color = np.array( [ [256*random.random(),256*random.random(),256*random.random()] for i in range(pts.shape[0])], dtype = np.uint8 )

	start = time.time()
	voronoi_diagrame = find_voronoi(pts, img.shape)
	centroid = find_centroid(voronoi_diagrame, 6000, img[:,:,0])
	stop1 = time.time()
	img[:] = color[voronoi_diagrame]
	print stop1 - start
	for i in centroid:
		cv2.circle(img, (i[1], i[0]), 1, (0,0,255), -1)
	cv2.imshow("voronoi_diagrame", img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()