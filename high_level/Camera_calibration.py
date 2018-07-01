import numpy as np 
import cv2
import sys
import glob
import os
from rank_nullspace import nullspace
from Coor2Dto3Dtransformation import Project2Dto3D, Calibrate_Camera

if __name__ == '__main__':
	print sys.argv
	try:
		image_dir = sys.argv[1]
	except Exception as e:
		print e
		print "missing image path"
		sys.exit()
	try:
		output_dir = sys.argv[2]
	except Exception as e:
		print e
		print "missing output directory"
		sys.exit()
	try:
		pattern_size = eval( sys.argv[3] )
	except Exception as e:
		print e
		print "missing Pattern size"
		sys.exit()
	image_extension = sys.argv[4] if len(sys.argv) >= 5 else "*.jpg"
	square_size = float(sys.argv[5]) if len(sys.argv) >= 6 else 1
	origin = eval(sys.argv[6]) if len(sys.argv) >= 7 else (0,0)

	image_names = glob.glob(image_dir + image_extension)
	print "Name of sample : ", image_names
	planar_image = sys.argv[7] if len(sys.argv) >= 8 else None
	planar_indx = -1
	try:
		os.mkdir(output_dir)

	except Exception as e:
		print e
		print "Directory",output_dir,"already exist not creat new directory"
	try:
		os.mkdir(output_dir+"/Detect_chessboard")
	except Exception as e:
		print "Directory",output_dir+"/Detect_chessboard","already exist not creat new directory"
	try:
		os.mkdir(output_dir+"/undistorted")
	except Exception as e:
		print "Directory",output_dir+"/undistorted","already exist not creat new directory"	

	ret, mtx, dist, rvecs, tvecs, planar_indx = Calibrate_Camera(image_names, output_dir, pattern_size, square_size, origin, planar_name = planar_image)
	shape = np.array(cv2.imread(image_names[0], 0).shape)
	
	np.savez(output_dir+"/output_matrix", shape = shape, camera_matrix = mtx, distortion_ceff = dist, rotation_vector = rvecs, translation_vector = tvecs, planar_index = np.array([planar_indx]))

	print "dist coefs: ", dist
	for i, filename in enumerate(image_names):
		img = cv2.imread(filename)
		h,  w = img.shape[:2]
		org_dst = cv2.undistort(img, mtx, dist)
		if i == planar_indx:
			cv2.imwrite(output_dir+"/undistorted/undistorted_planar"+".png", org_dst)
		else:
			cv2.imwrite(output_dir+"/undistorted/undistorted"+str(i)+".png", org_dst)

	input_undistorted = output_dir+'/undistorted'+'/'
	output_undistorted = output_dir+'/output_undistorted'
	image_undistorted_list = glob.glob(input_undistorted + "*.png")

	try:
		os.mkdir(output_undistorted)
	except Exception as e:
		print e
		print "Directory",output_undistorted,"already exist not creat new directory"
	try:
		os.mkdir(output_undistorted+"/Detect_chessboard")
	except Exception as e:
		print "Directory",output_undistorted+"/Detect_chessboard","already exist not creat new directory"

	print "input_undistorted: ", input_undistorted

	ret_2, mtx_2, dist_2, rvecs_2, tvecs_2, planar_indx_2 = Calibrate_Camera(image_undistorted_list, output_undistorted, pattern_size, square_size, origin, planar_name = input_undistorted+"undistorted_planar"+".png")
	np.savez(output_undistorted+"/output_matrix", shape = shape, camera_matrix = mtx_2, distortion_ceff = dist_2, rotation_vector = rvecs_2, translation_vector = tvecs_2, planar_index = np.array([planar_indx_2]))

	print "OK\nVerified Output...\n"

	planar_image = cv2.imread(image_undistorted_list[planar_indx_2], 0)
	h,w = planar_image.shape[:2]
	ret, imgPoints = cv2.findChessboardCorners(planar_image, pattern_size,None)
	if ret == True:
		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
		cv2.cornerSubPix(planar_image,imgPoints,(5,5),(-1,-1),criteria)
	imgPoints = imgPoints.reshape(-1,2)
	objp = np.zeros( (pattern_size[0]*pattern_size[1], 3), np.float32 )
	objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
	objp *= square_size
	objp[:,0] += origin[0]
	objp[:,1] += origin[1]
	objp[:,2] += origin[2] if len(origin) >= 3 else 0

	newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx_2, dist_2, (w,h), 1, (w,h))

	p = Project2Dto3D(imgPoints.copy(), tvecs[planar_indx], rvecs[planar_indx], mtx)

	diff = (np.abs(p - objp[:,:2]) / square_size) * 100
	print p
	print "error x,y respect to square size : ",np.mean(diff, axis = 0)

	vis = cv2.cvtColor(planar_image, cv2.COLOR_GRAY2BGR)
	vis[:,:,:] = 0
	# cv2.drawChessboardCorners(vis, pattern_size, imgPoints, ret)
	print imgPoints[0]
	cv2.circle(vis, (int(imgPoints[0][0]) , int(imgPoints[0][1])), 5, (0,0,255), -1)
	for i in range(len(p)):
		# cv2.circle(vis, (int(imgPoints[i][0]) , int(imgPoints[i][1])), 5, (0,0,255), -1)
		cv2.putText(vis, str(int(p[i][0]))+","+str(int(p[i][1])), (int(imgPoints[i][0]) - 25,int(imgPoints[i][1])-20), cv2.FONT_HERSHEY_PLAIN, 0.4, (0,0,255), 1)
	cv2.imwrite("vis.jpg",vis)
	cv2.imshow("vis", vis)
	cv2.waitKey(0)
	cv2.destroyAllWindows()