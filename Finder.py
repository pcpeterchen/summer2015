'''
Author: Peter Chen, Maher Shamaa, Michael Morehead
Date: 7/22/2015
Project: Finder.py

Purpose: Given a folder of Raw EM data, and masks of nuclei, TIFF files,
for the EM data, find all the centers of the Nuclei.
Raw EM data comes from Serial Block Face Electron Microscopy and
is converted into TIFF files.  Then put through ILASTIK,
with Pixel Classification, to identify all probable Nuclei.
This program finds the centers of all probable Nuclei.

Known Issues: The program finds 56 centers, 27 of which are known cells.
The other 29 are false positives.  There are 37 cells known in
the original data.  We will make our testing standard by
cropping a small section of the original data, identify all
cells known, then debug.

Usage:  python Finder.py <dir of mask as folder of TIFF files> <dir of \
		original EM files at original resolution> <mask bin> <em bin>
Default Example: python Finder.py ~/Documents/p3_bin10_masks/ \
		~/Documents/p3_bin2/ 10 2
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
# a list of contours (the shape and list of points at each Z dimension)
# A method for adding points to the cell and a method for finding the center
class CellBody:
	# unique cell number.
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

	#  for loop through all the contours in self.contours and find the contour
	#  that matches the self.center
	#  Z coordinate.  contour has form [list of points, filenum]
	def contourZFind(self, contours, center):
		for contour in contours:
			if contour[1] == center[2]:
				return contour

	#  take in a list and return an average of the values
	def listaverage(self, sizes):
		length = len(sizes)
		return sum(sizes)/length

	#  returns the average point between all the X and Y coordinates.
	#  This is then averaged with the middle point of the list of centers.
	#  Returns a point.
	def cellCenter(self, centers):
		# get list of X, Y, Z
		length = len(centers)
		cenXs = [i for i, j, k in centers]
		cenYs = [j for i, j, k in centers]
		cenZs = [k for i, j, k in centers]

		avgX = sum(cenXs)/length
		avgY = sum(cenYs)/length
		avgZ = sum(cenZs)/length

		# middle of the centers list
		midXYZ = centers[length/2]
		return [(avgX + midXYZ[0])/2, (avgY + midXYZ[1])/2,
				(avgZ + midXYZ[2])/2]


#  finds the center of the largest contour and returns a point
#  ff is a file, and filenum is a slice number
def cenFind(ff, filenum):
	src = cv2.imread(ff, cv2.CV_LOAD_IMAGE_GRAYSCALE)

	# Set threshold and maxValue
	thresh = 1
	maxValue = 255

	# threshold the file to 0 and 255
	th, dst = cv2.threshold(src, thresh, maxValue, cv2.THRESH_BINARY | 
							cv2.THRESH_OTSU)

	# Find Contours
	mask = np.zeros(dst.shape, np.uint8)
	countours, hierarchy = cv2.findContours(dst, cv2.RETR_TREE,
		cv2.CHAIN_APPROX_SIMPLE)

	# *50 is a MAGIC NUMBER* but works well with test case
	lengths = [len(i) for i in countours]
	largeContours = [l for l in lengths if l > 50]

	# indecies of large contours
	z = [lengths.index(l) for l in largeContours]

	# calculates the average X and Y of the largest contour
	avgs = []
	cont = [countours[index] for index in z]
	for ii in xrange(0, len(cont)):
		totx = 0
		toty = 0
		for pp in cont[ii]:
			totx += pp[0][0]
			toty += pp[0][1]
		avgs.append([[totx/len(cont[ii]), toty/len(cont[ii]), filenum],
					[cont[ii], filenum]])
	return avgs


#  read through each file in files and create cells accordingly
#  return list of cells in cellList
def cellFind(files):
	cellList = []

	for f in files:
		# read in image and find the centers of large contours
		print "processing slice: " + f.split('/')[-1:][0]
		src = cv2.imread(f, cv2.CV_LOAD_IMAGE_GRAYSCALE)
		contourcens = cenFind(f, files.index(f))

		# if no cells, create new cells
		if len(cellList) is 0:
			for ii in contourcens:
				newCell = CellBody(ii[0], ii[0][2], ii[1])
				cellList.append(newCell)			
		else:
			for cen in contourcens:
				celladded = 0
				for cell in cellList:
					# calculate distance and add cell if in bounds
					endp = cell.points[cell.size-1]
					xydist = calcDist([endp[0], endp[1]], [cen[0][0],
									  cen[0][1]])
					zdist = abs(endp[2] - cen[0][2])
					if xydist < cell.avsize/(2 * math.pi):
						if zdist < 3:
							cell.add(cen[0], cen[1])
							celladded = 1
				# if cell not in any existing cell bounds create new cell
				if celladded is 0:
					newCell = CellBody(cen[0], cen[0][2], cen[1])
					cellList.append(newCell)

	#  remove cells from list that are not large enough to be nuclei
	#  *MAGIC NUMBERS* here
	cellList = [j for j in cellList if j.size > 50 and j.avsize > 80]
	cellList = sorted(cellList, key=lambda x: x.center[2], reverse=False)
	return cellList


# returns distance between points p1 and p2
def calcDist(p1, p2):
	return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


# transposes from one bin to another
# takes in a list of cells LargeCells, bin ratio bin,
# and original shape ogshape
# returns list of cells, and the original shape
#  written by Maher Shamaa
def scaleUp(largeCells, bin, ogshape):
	#  multiply each cell in the list by the bin ratio
	# multiply the dimensions of ogshape by bin ratio
	for cell in largeCells:
		cell.center[0] *= bin
		cell.center[1] *= bin
		cell.contours
	ogshape = list(ogshape)
	ogshape[0] *= bin
	ogshape[1] *= bin
	return largeCells, ogshape


def main():
	#  directory of tiff files that we want to find
	dir = sys.argv[1]

	#  directory of em tiff files
	emdir = sys.argv[2]

	#  original bin size
	ogbin = int(sys.argv[3])

	#  final bin sizeS
	finalbin = int(sys.argv[4])

	files = glob.glob(dir + "*.tiff")
	files = natsorted(files)

	emfiles = glob.glob(emdir + "*.tiff")
	emfiles1 = glob.glob(emdir + "*.tif")
	if len(emfiles1) > len(emfiles):
		emfiles = emfiles1
	emfiles = natsorted(emfiles)

	ogshape = cv2.imread(files[0], cv2.CV_LOAD_IMAGE_GRAYSCALE).shape
	cellList = cellFind(files)

	binratio = ogbin/finalbin

	correctedCells, correctedShape = scaleUp(cellList, binratio, ogshape)

	# dump results for use in cropper.  Dump list of cells CorrectedCells,
	# shape Corrected shpae, original emfiles, mask files, and binratio
	pickle.dump(correctedCells, open("correctedCells.p", "wb"))
	pickle.dump(correctedShape, open("correctedShape.p", "wb"))
	pickle.dump(emfiles, open("emfiles.p", "wb"))
	pickle.dump(files, open("files.p", "wb"))
	pickle.dump(binratio, open("bin.p", "wb"))

if __name__ == "__main__":
	main()
