import numpy as np 
import cv2

def clipping(cnt, section_line, step = 1):
	# print cnt.shape
	index_upper = np.where(cnt[:,0,1] < section_line)[0]
	di = np.diff(index_upper)
	out = np.split(index_upper, np.where((di != step) & (di < len(cnt)-1))[0] + 1)
	# out[0] = np.append([out[0]], [out[-1]])
	# out = np.delete(out,-1,0)
	if len(cnt) == 426 and len(di) > 0 and len(out)>1:
		print max(di), len(cnt)
		
		print out
	return out

def infill_polygon(cnts, shape = (640,480), step = 10):
	infill = [[]]*len(cnts)
	for sec in range(10,shape[0], step):
		indx = 0
		for cnt in cnts:
			seqs = clipping(cnt, sec)
			for i in range(len(seqs)): #####
				if len(seqs[i]) == 0:
					pass
				else:
					infill[indx].append( np.array( [cnt[max(seqs[i])], cnt[min(seqs[(i+1)%len(seqs)])]] ) ) 
			indx += 1
	return infill

with np.load( 'geometry.npz' ) as data:
	contour = data['contour']
	hierarchy = data['hierarchy'].copy()
	shape = data['shape']
infills = infill_polygon(contour, shape = shape)
print "*..",len(infills), len(contour)	
blank = np.zeros(shape)
# for i in range(50):
# 	print contour[i][0]
# 	cv2.putText(blank, str(i), (contour[i][0,0,0],contour[i][0,0,1]), cv2.FONT_HERSHEY_PLAIN, 5, 255)
# 	cv2.drawContours(blank, contour, i, 255, 1)
cv2.drawContours(blank, contour, 21, 255, 1)
print "**",len(contour[21])
for inf in infills:
	for line in inf:
		# print line
		cv2.line(blank, (line[0][0,0], line[0][0,1]), (line[1][0,0], line[1][0,1]), 255, 1)
for cnt in contour:
	if len(cnt) == 426:
		print cnt[0,0,0]
		cv2.circle(blank, (cnt[0,0,0],cnt[0,0,1]), 3, 255)
		cv2.circle(blank, (cnt[109,0,0],cnt[109,0,1]), 3, 255)
		cv2.circle(blank, (cnt[413,0,0],cnt[413,0,1]), 3, 255)
		cv2.circle(blank, (cnt[425,0,0],cnt[425,0,1]), 3, 255)
		cv2.circle(blank, (cnt[71,0,0],cnt[71,0,1]), 3, 255)
		cv2.circle(blank, (cnt[24,0,0],cnt[24,0,1]), 3, 255)

cv2.imshow("blank", blank)
cv2.waitKey(0)
cv2.destroyAllWindows()