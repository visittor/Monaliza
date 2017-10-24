import numpy as np 
import cv2

def to_coor(coor1, coor2, section_line):
	delta = coor1 - coor2 ## x1-x2/y1-y2 = x1-secx/y1-secy --> x1-(y1-secy)*(x1-x2/y1-y2) --> dely_*x +delx_*y  = -c, y = sec, [x;y] = A'*[-c;sec]
	A = np.array([[delta[1], -delta[0]],[0, 1]] , dtype = float)
	b = np.array([[ delta[1]*coor1[0]-delta[0]*coor1[1] ], [section_line]], dtype = float)

	return np.linalg.solve(A, b).ravel()


def clipping(cnt, section_line, step = 1):
	index_upper = np.where(cnt[:,0,1] < section_line)[0]
	index_lower = np.where(cnt[:,0,1] >= section_line)[0]
	
	d_upper = np.diff(index_upper)
	d_lower = np.diff(index_lower)
	
	cruster_upper = np.array([[i[0], i[-1]] for i in np.split(index_upper, np.where(d_upper != step)[0] + 1) if len(i) > 0]).ravel()
	cruster_lower = np.array([[i[0], i[-1]] for i in np.split(index_lower, np.where(d_lower != step)[0] + 1) if len(i) > 0]).ravel()

	dc_upper = np.diff(cruster_upper)
	dc_lower = np.diff(cruster_lower)

	head_tail_upper = np.hstack([np.array([ cruster_upper[i] for i in range(len(dc_upper)) if dc_upper[i] > 0 ]), cruster_upper[-1]]) if len(cruster_upper) > 0 else []
	head_tail_lower = np.hstack([np.array([ cruster_lower[i] for i in range(len(dc_lower)) if dc_lower[i] > 0 ]), cruster_lower[-1]]) if len(cruster_lower) > 0 else []

	collected = None
	for indx in head_tail_upper:
		i = (indx+1)%len(cnt)
		if i in head_tail_lower:
			point = to_coor(cnt[indx,0], cnt[i,0], section_line)
			collected = np.vstack([collected,point]) if collected is not None else np.array([point])
	for indx in head_tail_lower:
		i = (indx+1)%len(cnt)
		if i in head_tail_upper:
			point = to_coor(cnt[indx,0], cnt[i,0], section_line)
			collected = np.vstack([collected,point]) if collected is not None else np.array([point])

	return collected

# def isCloseContour (cnt):


def infill_polygon(cnts, shape = (640,480), step = 10):
	infill = [[]]*len(cnts)
	for sec in range(10,shape[0], step):
		indx = 0
		for cnt in cnts:
			points = clipping(cnt, sec)
			if points is not None:
				points = points[np.argsort(points[:,0])]
				points = points.astype(int)
				for i in range(0, len(points), 2):
					infill[indx].append( np.array([points[i], points[i+1]])) 
			indx += 1
	return infill

with np.load( 'picture/test_open_polygon_infill.npz' ) as data:
# with np.load( 'picture/test_close_polygon_infill.npz' ) as data:
# with np.load( 'picture/geometry.npz' ) as data:
	contour = data['contour']
	hierarchy = data['hierarchy'].copy()
	shape = data['shape']
infills = infill_polygon(contour, shape = shape, step = 1)
blank = np.zeros(shape)
cv2.drawContours(blank, contour, -1, 255, 1)
for inf in infills:
	for line in inf:
		cv2.line(blank, (line[0,0], line[0,1]), (line[1,0], line[1,1]), 255, 1)

cv2.imshow("blank", blank)
cv2.waitKey(0)
cv2.destroyAllWindows()