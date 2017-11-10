# coding=utf-8
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import random
import cv2
# from shapely.geometry import Polygon

def voronoi_finite_polygons_2d(points, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.
    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.
    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.
    """

    # compute Voronoi tesselation
    vor = Voronoi(points)

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        if not all_ridges.has_key(p1):
            print 'error agian -"-'
            new_regions.append(vertices)
            continue
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

def colorize_voronoi_diagram(regions, vertices, img):
    color1 = 0
    color2 = 0
    color3 = 0
    voronoi_diagram = np.zeros((img.shape[0], img.shape[1],3), dtype = np.uint8)
    for i,region in enumerate(regions):
        polygon = np.array(vertices[region]).astype(int)
        P = np.array([ np.array([[j[1],j[0]]]) for j in polygon])
        c = ((i & (255<<16))>>16, (i & (255<<8))>>8,i & 255)
        cv2.drawContours(voronoi_diagram, [P], -1, c,-1)
    return voronoi_diagram

def find_centroid2(voronoi, numpoint, pdf_img):
    m  = np.zeros(numpoint, dtype = float)
    mx = np.zeros(numpoint, dtype = float)
    my = np.zeros(numpoint, dtype = float)
    for i in range(numpoint):
        # c1 = (i & 16711640)>>16
        c2 = (i & (255<<8))>>8
        c3 = i & 255
        indx = np.where( (voronoi[:,:,1] == c2) & (voronoi[:,:,2] == c3) )
        # print i
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
    # make up data points
    np.random.seed(1234)
    # points = 480*np.random.rand(7000, 2) 
    img = np.zeros( (480,640,3), dtype = np.uint8) + 1  
    pts = np.array( [ [img.shape[0]*random.random(), img.shape[1]*random.random()] for i in range(700) ], dtype = int ) 
    color = np.array( [ [256*random.random(),256*random.random(),256*random.random()] for i in range(pts.shape[0])], dtype = np.uint8 )
    print color[1]
    # plot
    vor = Voronoi(pts)
    regions, vertices = voronoi_finite_polygons_2d(pts, 5)

    # print "--"
    # print regions
    # print "--"
    print vertices
    # plt.subplot(211)
    # colorize
    print len( regions )
    for i,region in enumerate(regions):
        # polygon =vertices[region]
        polygon = np.array(vertices[region]).astype(int)
        P = np.array([ np.array([[j[1],j[0]]]) for j in polygon])
        c = tuple(color[i])
        cv2.drawContours(img, [P], -1, (int(c[0]), int(c[1]), int(c[2])),-1)
        # cv2.drawContours(img, [P], -1, (10000, 0, 0),-1)
        # plt.fill(*zip(*vertices[region]), alpha=0.4)

    for i in pts:
        cv2.circle(img, (i[1], i[0]), 5, (0,0,255), -1)

    # plt.plot(pts[:,0], pts[:,1], 'ko')
    # plt.xlim(vor.min_bound[0] - 0.1, vor.max_bound[0] + 0.1)
    # plt.ylim(vor.min_bound[1] - 0.1, vor.max_bound[1] + 0.1)
    # plt.xlim(0, img.shape[0])
    # plt.ylim(0, img.shape[1])
    # plt.subplot(212)
    plt.imshow(img)

    plt.show()
    # cv2.imshow('img', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
