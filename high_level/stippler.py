import numpy as np 
import cv2
from voronoiDiagram import *
from colorized_voronoi_with_clipping import *
import itertools
import random
import time
import matplotlib.pyplot as plt
def stipper(img, gap, itr = 15, max_size = 12000, cutoff = 220):
	if len(img.shape) > 2 and img.shape[2] > 1:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# ratio = 600 / img.shape[0]
	ratio = 2.0
	tiles = []
	for i in range(1):
		for j in range(1):
			tile = img[i*img.shape[0]/1 : (i+1)*img.shape[0]/1, j*img.shape[1]/1 : (j+1)*img.shape[1]/1]
			tile = cv2.resize(tile, None, fx = 2, fy = 2)
			tiles.append(tile)
	
	print "start gen point"
	genPoint_list = []
	for i in range(1):
		genPoint_list.append( np.array(generate_point(max_size/1, tiles[i], cutoff = cutoff)))

	print "stop gen point"
	for j in range(itr):
		start = time.time()
		
		voronois = []
		centroids = []
		for i in range(1):
			print "find voronoi ... tile", i, "\n"
			voronois.append(find_voronoi(genPoint_list[i], tiles[i].shape))

			print "find centroid ...tile", i, "\n"

			pdf = 255 - tiles[i]
			
			centroids.append(find_centroid(voronois[i], len(genPoint_list[i]), pdf))

		mask = np.zeros((int(img.shape[0]), int(img.shape[1]))) + 255
		mask2 = np.zeros((int(tiles[0].shape[0]), int(tiles[0].shape[1]))) + 255

		for count,centroid in enumerate(centroids):
			for p in centroid:
				cv2.circle(mask, (int((1/ratio)*p[1]) + (count%4)*img.shape[1]/4, int((1/ratio)*p[0]) + (count/4)*img.shape[0]/4), 3, 0, -1)
				cv2.circle(mask2, (int(p[1]) + (count%4)*img.shape[1]/4, int(p[0]) + (count/4)*img.shape[0]/4), 5, 0, -1)

		genPoint_list = centroids
		# if genPoint.shape[0] == genPoint_.shape[0] and (genPoint_ == genPoint).all() :
		# 	print "finish...\n"
		# 	cv2.imwrite("output/final_"+str(i+1)+".jpg", mask)
		# 	break

		print "finish", j+1, "iterations"
		print "Time used :", time.time() - start, "\n"

		cv2.imwrite("output/iterations"+str(j+1)+".jpg", mask)
		cv2.imwrite("output/iterations_bigger"+str(j+1)+".jpg", mask2)
		path = "output/point.npz"
		np.savez(path, point = genPoint_list[0], shape = np.array(mask2.shape))

	return genPoint_list

def stipper2(img, gap, itr = 15, max_size = 12000, cutoff = 220):
	if len(img.shape) > 2 and img.shape[2] > 1:
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# ratio = 600 / img.shape[0]
	tiles = []
	for i in range(1):
		for j in range(1):
			tile = img[i*img.shape[0]/1 : (i+1)*img.shape[0]/1, j*img.shape[1]/1 : (j+1)*img.shape[1]/1]
			tile = cv2.resize(tile, None, fx = 4, fy = 4)
			tiles.append(tile)
	
	print "start gen point"
	genPoint_list = []
	for i in range(1):
		genPoint_list.append( np.array(generate_point(max_size/1, tiles[i], cutoff = cutoff)))

	print "stop gen point"
	for j in range(itr):
		start = time.time()
		
		voronois = []
		centroids = []
		for i in range(1):
			print "find voronoi ... tile", i, "\n"
			regions, vertices = voronoi_finite_polygons_2d(genPoint_list[i], radius=None)
			# voronoi_diagram = np.zeros((tiles[i].shape[0],tiles[i].shape[1],3), dtype = np.uint8)
			print "colorize..."
			voronoi_diagram = colorize_voronoi_diagram(regions, vertices, tiles[i])
			plt.imshow(voronoi_diagram)
			plt.show()
			voronois.append( voronoi_diagram.copy() )

			print "find centroid ...tile", i, "\n"

			pdf = 255 - tiles[i]
			
			centroids.append(find_centroid2(voronois[i], len(genPoint_list[i]), pdf))

		mask = np.zeros((int(img.shape[0]), int(img.shape[1]))) + 255
		mask2 = np.zeros((int(tiles[0].shape[0]), int(tiles[0].shape[1]))) + 255

		for count,centroid in enumerate(centroids):
			for p in centroid:
				cv2.circle(mask, (int(0.25*p[1]) + (count%4)*img.shape[1]/4, int(0.25*p[0]) + (count/4)*img.shape[0]/4), 3, 0, -1)
				cv2.circle(mask2, (int(p[1]) + (count%4)*img.shape[1]/4, int(p[0]) + (count/4)*img.shape[0]/4), 5, 0, -1)

		genPoint_list = centroids
		# if genPoint.shape[0] == genPoint_.shape[0] and (genPoint_ == genPoint).all() :
		# 	print "finish...\n"
		# 	cv2.imwrite("output/final_"+str(i+1)+".jpg", mask)
		# 	break

		print "finish", j+1, "iterations"
		print "Time used :", time.time() - start, "\n"

		cv2.imwrite("output/iterations"+str(j+1)+".jpg", mask)
		cv2.imwrite("output/iterations_bigger"+str(j+1)+".jpg", mask2)
		path = "output/point.npz"
		np.savez(path, point = genPoint_list[0], shape = np.array(mask2.shape))

	return genPoint_list

def generate_point(numPoint, img, cutoff = 220):
	cutoff = cutoff if cutoff < 255 else 254
	genPoint = []
	img_temp = img.copy()
	shape = img.shape
	max_itr = shape[0]*shape[1]
	for i in range(numPoint):
		y = int(shape[0] * random.random())
		x = int(shape[1] * random.random())
		count = 0
		while img_temp[y,x] > 220 * random.random():
			y = int(shape[0] * random.random())
			x = int(shape[1] * random.random())
			count += 1
			# if count > max_itr:
			# 	raise "Too much point"
		img_temp[y,x] = 255
		genPoint.append( np.array([ y, x]) )
	return genPoint


if __name__ == '__main__':
	img = cv2.imread("picture/pass_2_2.jpg", 0)
	# img = cv2.resize(img, None, fx = 2, fy = 2)
	print "image shape is:", img.shape
	point = np.array( stipper(img, 2, itr = 75, max_size = 10000, cutoff = 190) )
	path = "output/point.npz"
	# np.savez(path, point = point[0])