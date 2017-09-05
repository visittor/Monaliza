import cv2
import numpy as np 
import sys

def recieve_video_cam(id):
	cap = cv2.VideoCapture(id)
	# cap.set(3,240)
	# cap.set(4,240)
	# cap.set(5,320) #(240, 320, 3)

	cap.set(3,1080)
	cap.set(4,1080)
	cap.set(5,1080) #(480, 640, 3)

	try:
		while 1 == 1:
			ret,img = cap.read()
			yield img
	finally:
		cap.release()

def recieve_video_file(file_name, repeat = 1):
	cap = cv2.VideoCapture(file_name)
	try:
		while  1 == 1:
			ret, img = cap.read()
			if not ret :
				cap.set( 2, 0)
				ret,img = cap.read()
			if ret:
				yield img
	finally:
		cap.release()

def create_coor(img, grid_dis = 50):
	for x in range(grid_dis, img.shape[1], grid_dis):
		img[:, x-1:x+1] = [0, 0, 255]
		cv2.putText(img, str(x), (x,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0,0,255], 1)
	for y in range(grid_dis, img.shape[0], grid_dis):
		img[y-1:y+1, :] = [0,0,255]
		cv2.putText(img, str(y), (10,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0,0,255], 1)
	for x in range(grid_dis, img.shape[1], grid_dis):
		for y in range(grid_dis, img.shape[0], grid_dis):
			img[y-1:y+1, x-1:x+1] = [255, 0, 0]

if __name__ == '__main__':
	is_write = 0
	is_puase = 1
	id_ = int(sys.argv[1]) if len(sys.argv) >= 2 else 1
	reciver = recieve_video_cam(id_)
	fourcc = cv2.VideoWriter_fourcc(*'DIVX')
	out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
	img_ = next(reciver)
	img = img_
	while 1 == 1:
		if is_puase:
			img = next(reciver)
			img_ = img.copy()
		else:
			img = img_.copy()
		create_coor(img)
		cv2.imshow('img',img)
		if is_write:
			out.write(img)
		k = cv2.waitKey(1)
		if k&0XFF == 27:
			break
		elif k&0XFF == ord('s'):
			is_write = (is_write+1)%2
			a = 'writing...' if is_write == 1 else "puase..."
			print a
		elif k&0xFF == ord("c"):
			cv2.imwrite("save__.jpg",img)
		elif k&0xFF == ord("p"):
			is_puase = 0 if is_puase == 1 else 1

	reciver.close()
	out.release()
	cv2.destroyAllWindows()

