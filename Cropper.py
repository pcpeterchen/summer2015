'''
Author:  Peter Chen, Maher Shamaa, Michael Morehead
Date: 7/22/2015
Project: Cropper.py

Purpose: Given a folder of list of nucleus centers.
		Crop a section of the orignal em data and output a cropping to a
		unique folder in TestVolumes folder. Allows for processing of all
		cells at once. Allows user to pick a cell that needs further cropping.

Known Issues: The program will crop out each cell body, but sometimes ends of
			the cell in X,Y,Z directions are not fully cropped.
			Thus the user has the option to view each cell body and decide
			whether or not to crop it again with larger or smaller values.

Usage: python Cropper.py <num x pixels> <num of y pixels> <num of Z slices \
       in positive direction> <num of Z slices in negative direction> \
       <cell number>
		cell number -1 will crop all the cells.
Default Example: python Cropper.py 200 200 50 50 -1
'''
import cv2
import numpy as np
import glob
import math
import code
import heapq
from natsort import natsorted
import cPickle as pickle
from pdb import set_trace as bp
import sys
import os


# cell Body class.  A cell Body contains a center, list of points in the cell,
# A method for adding points to the cell and a method for finding the size
class CellBody:
	numCell = 0

	def __init__(self, c, i, cont):
		self.center = c
		self.points = [c]
		self.start = i
		self.avsize = len(cont[0])
		self.sizes = [len(cont[0])]
		self.maxsize = len(cont[0])
		self.size = 0
		self.contours = [cont]
		self.contour = cont
		self.end = c[2]
		self.cellNum = CellBody.numCell
		CellBody.numCell += 1

	#  add a point to the cell
	def add(self, pp, cc):
		self.points.append(pp)
		self.center = self.cellCenter(self.points)
		self.sizes.append(len(cc[0]))
		self.avsize = self.listaverage(self.sizes)
		self.size = len(self.points)
		self.contours.append(cc)
		self.contour = self.contourZFind(self.contours, self.center)
		self.end = pp[2]
		self.points = sorted(self.points, key=lambda x: x[2], reverse=False)

		if len(cc[0]) > self.maxsize:
			self.maxsize = len(cc[0])


# takes in a list of cells, bin ratio, X,Y,Z threshold
# crops the cell bodies and returns a list of cropped arrays and the cells
# they came from to a folder for each cell.
# return list of cropped array of the cells, and the cell they came from.
# For both em data and mask data.
def cropCell(cells, emfiles, files, bin, xthresh, ythresh, zposthresh, 
			 znegthresh):
	# loops through each cell
	# crops cellbodies that fit within an area in src.shape determined by
	# X,Y thresh
	imgs = []
	imgs2 = []
	for cc in cells:
		src = cv2.imread(emfiles[cc.center[2]], cv2.CV_LOAD_IMAGE_GRAYSCALE)
		src2 = cv2.imread(files[cc.center[2]], cv2.CV_LOAD_IMAGE_GRAYSCALE)

		x = cc.center[0]
		y = cc.center[1]

		# calculate the min and max values of each nucleus
		maxXs = []
		minXs = []
		maxYs = []
		minYs = []
		for bb in cc.contours:
			xs = [i[0][0] for i in bb[0]]
			minXs.append(min(xs))
			maxXs.append(max(xs))
		minX = min(minXs)
		maxX = max(maxXs)

		for bb in cc.contours:
			ys = [i[0][1] for i in bb[0]]
			minYs.append(min(ys))
			maxYs.append(max(ys))
		maxY = max(maxYs)
		minY = min(minYs)

		cropArr2 = src2[minY: maxY, minX: maxX]

		# multiply by bin ratio
		minX *= bin
		minY *= bin
		maxX *= bin
		maxY *= bin

		# modifications from cropping parameters
		minX = minX-xthresh
		minY = minY-ythresh
		maxX = maxX+xthresh
		maxY = maxY+ythresh

		# if cell boundaries do not exceed the boundaries of the em file, crop
		if (minX > 0 and minY > 0) and \
		   (maxX < src.shape[1] and maxY < src.shape[0]) and \
		    cc.start - znegthresh > 0 and cc.end + zposthresh <= len(files):

			if not os.path.exists("./TestVolumes/" + str(cc.cellNum)):
				os.mkdir("./TestVolumes/" + str(cc.cellNum))
			print "processing cell at: " + str(cc.center[2])

			cropArr = src[minY: maxY, minX: maxX]
			imgs.append([cropArr, cc])
			imgs2.append([cropArr2, cc])

			for xx in xrange(cc.start - znegthresh, cc.end + zposthresh):
				src = cv2.imread(emfiles[xx], cv2.CV_LOAD_IMAGE_GRAYSCALE)
				cropArr = src[minY: maxY, minX: maxX]
				cv2.imwrite("./TestVolumes/" + str(cc.cellNum) + "/" + \
							str(xx).zfill(4) + '.tiff', cropArr)

	print "Done processing %d cells" % len(imgs)
	return imgs, imgs2


def main():

	# The threshold values for cropping X,Y,Z
	xthresh = float(sys.argv[1])
	ythresh = float(sys.argv[2])
	zposthresh = int(sys.argv[3])
	znegthresh = int(sys.argv[4])
	cellNum = int(sys.argv[5])

	# load data dumped by Finder.py
	correctedCells = pickle.load(open("correctedCells.p", "rb"))
	emfiles = pickle.load(open("emfiles.p", "rb"))
	files = pickle.load(open("files.p", "rb"))
	bin = pickle.load(open("bin.p", "rb"))

	# crop all cells, or specified cell
	correctedCells = sorted(correctedCells, key=lambda x: x.cellNum,
							reverse=False)
	if cellNum == -1:
		imgs, imgs2 = cropCell(correctedCells, emfiles, files, bin, xthresh,
							   ythresh, zposthresh, znegthresh)
	else:
		onecellList=[]
		for ce in correctedCells:
			if cellNum == ce.cellNum:
				onecellList.append(ce)
				imgs, imgs2 = cropCell(onecellList, emfiles, files, bin,
					                   xthresh, ythresh, zposthresh,
					                   znegthresh)

	# dump cropped arrays
	pickle.dump(imgs, open("imgs.p", "wb"))
	pickle.dump(imgs2, open("imgs2.p", "wb"))
	print "done transposing"

if __name__ == "__main__":
	main()
