'''
Author:  Peter Chen, Maher Shamaa, Michael Morehead
Date: 7/22/2015
Project: Viewer.py

Purpose: Outputs to a folder TestEM the contour of the center of each cell as
		in the mask and in the orignal EM data.

Usage: python Viewer.py
'''
import cPickle as pickle
import cv2
import code
import os
from pdb import set_trace as bp

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

#  load the cells from Cropper.py
srcshape = pickle.load(open("srcshape.p", "rb"))
imgs = pickle.load(open("imgs.p", "rb"))
imgs2 = pickle.load(open("imgs2.p", "rb"))

# create folder to put the TIFF files
if not os.path.exists("./TestEM/"):
	os.mkdir("./TestEM/")

# cycle through each cell and write the center contour to a tiff
# print out data for observation
for jj in imgs:
	print "cell center for imod: " + str([jj[1].center[0], srcshape[0] - \
										 jj[1].center[1], jj[1].center[2]])
	print "size: " + str(jj[1].size)
	print "cell start: " + str(jj[1].start)
	print "cell end: " + str(jj[1].end)
	print "avsize: " + str(jj[1].avsize)
	print "shape: " + str(jj[0].shape)
	print "cell number: " + str(jj[1].cellNum)

	cv2.imwrite("./TestEM/" + str(jj[1].cellNum) + ".tiff", jj[0])
	print "-------------------------------------------------------"

for ii in imgs2:
	thresh = 1
	maxValue = 255
	th, dst = cv2.threshold(ii[0], thresh, maxValue, cv2.THRESH_BINARY | \
		                    cv2.THRESH_OTSU)
	cv2.imwrite("./TestEM/" + str(ii[1].cellNum) + "_sil.tiff", dst)
print 'end'
