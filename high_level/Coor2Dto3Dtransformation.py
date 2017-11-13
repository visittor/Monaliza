import numpy as np 
import cv2
import sys
import glob
import os
from rank_nullspace import nullspace

def findXYFromUndistortion_array(corners, dist_coefs):
	NewCorners = np.zeros(corners.shape, dtype = corners.dtype)
	r = np.sqrt(np.power(corners[:,0],2)+np.power(corners[:,1],2))
	k1 = dist_coefs[0][0]
	k2 = dist_coefs[0][1]
	k3 = dist_coefs[0][4]
	p1 = dist_coefs[0][2]
	p2 = dist_coefs[0][3]
	k4 = dist_coefs[0][5]
	k5 = dist_coefs[0][6]
	k6 = dist_coefs[0][7]

	a = (1 + k1 * np.power(r,2) + k2 * np.power(r,4) + k3 * np.power(r,6)) / (1 + k4 * np.power(r,2) + k5 * np.power(r,4) + k6 * np.power(r,6))
	b = 2*p1*corners[:,0]*corners[:,1] + p2*(np.power(r,2)+2*np.power(corners[:,0],2))
	NewCorners[:,0] = (corners[:,0] - b) / a
	c = p1*(np.power(r, 2) + 2*np.power(corners[:,1], 2)) + 2*p2*corners[:,0]*corners[:,1]
	NewCorners[:,1] = (corners[:,1] - c) / a
	NewCorners[:,2] += 1
	return NewCorners

def getPsuedoInvPMatAndCpoint(translation_vector, rotation_vector, camera_matrix):
	rotMat,jacobian = cv2.Rodrigues(rotation_vector)
	tvec = translation_vector
	RTMat = np.hstack((rotMat,tvec))
	pMat = np.dot(camera_matrix, RTMat)
	CPoint = nullspace(pMat).reshape(-1)
	pseudoInvPMat = np.linalg.pinv(pMat)
	return pseudoInvPMat, CPoint

def Project2Dto3D_(points, pseudoInvPMat, Cpoint):
	pOut = np.zeros((len(points),2), np.float32 )
	for i,p in enumerate(points):
		p = np.hstack((p, np.ones(1, np.float32))).reshape(-1,1) #[u, v, 1]
		p = np.dot(pseudoInvPMat, p).reshape(-1)
		lambdaVal = p[2] / Cpoint[2]
		p = p - (lambdaVal * Cpoint)
		p = p / p[3]
		pOut[i] = p[:2]
	return pOut

def Project2Dto3D(points, translation_vector, rotation_vector, camera_matrix):
	pseudoInvPMat, Cpoint = getPsuedoInvPMatAndCpoint(translation_vector, rotation_vector, camera_matrix)
	points = Project2Dto3D_(points.copy(), pseudoInvPMat, Cpoint)
	return points

def Calibrate_Camera(file_names, output_dir,pattern_size, square_size, origin, planar_name = None):
	objp = np.zeros( (pattern_size[0]*pattern_size[1], 3), np.float32 )
	objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
	objp *= square_size
	objp[:,0] += origin[0]
	objp[:,1] += origin[1]
	objp[:,2] += origin[2] if len(origin) >= 3 else 0

	objpoints = [] 
	imgpoints = []

	planar_indx = -1
	for i,filename in enumerate( file_names ):
		print "Working on: "+filename
		if planar_name is not None and filename == planar_name:
			planar_indx = i
			print "\nWorking on planar image\n"
		gray = cv2.imread(filename, 0)
		h, w = gray.shape[:2]
		ret, corners = cv2.findChessboardCorners(gray, pattern_size,None)

		if ret == True:
			print "Found Chess Board On", filename
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
			cv2.cornerSubPix(gray,corners,(5,5),(-1,-1),criteria)
			imgpoints.append(corners.reshape(-1,2))
			objpoints.append(objp)
		else:
			print "Not Found Chess Board In " + filename
			if planar_indx == i:
				print "\nCannot found Chessboard on planar image ignore everything and exit program ...\n"
				sys.exit()
		vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
		cv2.drawChessboardCorners(vis, pattern_size, corners, ret)
		if planar_indx == i:
			cv2.imwrite(output_dir+"\Detect_chessboard\planar"+".png", vis)
			continue
		cv2.imwrite(output_dir+"\Detect_chessboard\output"+str(i)+".png",vis)

	ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (w, h),None,None,flags = cv2.CALIB_RATIONAL_MODEL)

	return ret, mtx, dist, rvecs, tvecs, planar_indx