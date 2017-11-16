import numpy as np 
import cv2
import serial 
import glob
import time
import sys
import argparse
from Coor2Dto3Dtransformation import Project2Dto3D, Calibrate_Camera

def prepare_contour(contour, img_shape, cam_shape):
	out = [np.zeros((len(contour[i]),1, 2), dtype = contour[i].dtype) for i in range(len(contour))]
	for i,cnt in enumerate(contour):
		out[i][:,:,1] = (cnt[:,:,1].astype(float) * (cam_shape[0].astype(float) / img_shape[0].astype(float))).astype(int)
		out[i][:,:,0] = (cnt[:,:,0].astype(float) * (cam_shape[1].astype(float) / img_shape[1].astype(float))).astype(int)
	return out

def load_contour(path):
	with np.load( path ) as data:
		contour = data['contour']
		hierarchy = data['hierarchy'].copy()
		shape = data['shape']
		try:
			color = data['color']
		except Exception as e:
			color = np.zeros(len(contour))
			print e
	return contour, hierarchy, shape, color

def load_camera_matrix(path):
	with np.load( path ) as data:
		shape = data['shape']
		mtx = data['camera_matrix']
		dist = data['distortion_ceff']
		rvecs = data['rotation_vector']
		tvecs = data['translation_vector']
		planar_index = data['planar_index']
		rvec = rvecs[planar_index[0]]
		tvec = tvecs[planar_index[0]]
	return shape, mtx, dist, rvec, tvec

def finding_line( contour ):
	centroid = np.zeros( (len(contour), 2), np.float32 )
	for i,cnt in enumerate(contour):
		cx = np.sum(cnt[:,0])
		cy = np.sum(cnt[:,1])
		cx = cx / len(cnt)
		cy = cy / len(cnt)
		centroid[i,0] = cx
		centroid[i,1] = cy
	centroid = centroid[np.lexsort( np.transpose(centroid)[:-1] )] #sort by x then by y (https://stackoverflow.com/questions/2706605/sorting-a-2d-numpy-array-by-multiple-axes)
	print "centroid", centroid
	xMin = centroid[0]
	xMax = centroid[-1]
	v1 = xMax - xMin #find a vector from xMin to xMax.
	vectors = centroid - xMin #find vectors from xMin to any poit.
	crossProduct = (vectors[:,1])*v1[0] - vectors[:,0]*v1[1] #find a cross-product.
	print xMax, xMin
	print crossProduct
	upper = centroid[ np.where(crossProduct<0) ] #if cross product is positive it above a line between xMin to xMax.
	lower = centroid[ np.where(crossProduct>0) ][::-1] #otherwise it below that line. (sort in decent direction)
	final = np.vstack([xMin, upper]) #Stack every point together
	final = np.vstack([final, xMax])
	final = np.vstack([final, lower])
	
	return final


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("matrix_path",
                    help="path to camera matrix")
	parser.add_argument("contour_path",
					help="path to contour file")
	parser.add_argument("-o", "--option", type=str, choices=['l', 'c', 'cnt'],
						help="Draw line circle or contour")

	args = parser.parse_args()

	matrix_path = args.matrix_path
	contour_path = args.contour_path
	
	contour, hierarchy, image_shape, color = load_contour(contour_path)
	camera_shape, mtx, dist, rvec, tvec = load_camera_matrix(matrix_path)

	## reshape contour to camera shape
	if (image_shape != camera_shape).any():
		reshape_cnts = prepare_contour(contour, image_shape, camera_shape)
	else:
		reshape_cnts = contour

	reshape_cnts = [cnt.reshape(-1,2) for cnt in reshape_cnts]

	##if draw lines 
	if args.option == 'l':
		polygon = finding_line( reshape_cnts )
		print "polygon",polygon

	## Change image coordinate to world coordinate
	world_coor_contour = []
	for i in range(len(reshape_cnts)):
		point = reshape_cnts[i].reshape(-1,2).astype(np.float32)
		world_coor_contour.append( Project2Dto3D(point, tvec, rvec, mtx) )
	print world_coor_contour




