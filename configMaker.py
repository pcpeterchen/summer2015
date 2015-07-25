'''
Author: Peter Chen
Date: 7/22/2015
Project: configMaker.py

Purpose: given a folder of swc.  make a folder of obj and a config

Sources: making the color gradient mehtods: arrayMultply, arraySum,
		intermediate, and gradient are from Python Fiddle source.
		http://pythonfiddle.com/color-gradients-and-intermediates

Usage:  python configMaker.py <SWC dir>
Default Example: python configMaker.py ~/swc dir/
'''
import os
import sys
import glob
import subprocess
from pdb import set_trace as bp
import natsort
import numpy as np


# given an array and an int c, multiply all values of the array by c
def arrayMultiply(array, c):
	return [element*c for element in array]


#  given two arrays a and b, return a sum of the two lists
def arraySum(a, b):
	return map(sum, zip(a,b))


#  given lists a, b, and a ratio retrun an intermediate value
def intermediate(a, b, ratio):
	aComponent = arrayMultiply(a, ratio)
	bComponent = arrayMultiply(b, 1-ratio)
	return arraySum(aComponent, bComponent)


#  given two lists a and b, return a list that is a gradient of the two values
#  with 'steps' number of steps
def gradient(a, b, steps):
	result = []
	steps = [n/float(steps) for n in range(steps)]
	for step in steps:
		result.append(intermediate(a, b, step))
	return result


#  translate integer aa into a hex value and return it
def tohex(aa):
	aa = np.asarray(aa, dtype = 'uint32')
	return '%02x%02x%02x' % (aa[0], aa[1], aa[2])


def main(file):
	# read in all swc files
	allswc = glob.glob(file + '/*.swc')
	allswc = natsort.natsorted(allswc)

	# format the name
	configname = allswc[0].split('/')[-1:]
	configname = configname[0].split('.')[:-1]
	configname = configname[0].split('_')[0]

	config = open(file + '/' + configname + 'config.ini', 'w+')

	# run swc2obj.py on all the swc
	for each in allswc:
		command = 'python swc2obj.py ' + each
		os.system(command)

	allobj = glob.glob(file + '/*.obj')
	allobj = natsort.natsorted(allobj)

	red = (255,0,0)
	blue = (0, 0, 255)
	grad  = gradient(red, blue, len(allobj))

	# write the config file and hex value
	for i in xrange(0, len(allobj)):
		config.write('#L#\tBO' + str(i+1) + '\t#' + tohex(grad[i]) + '\n')
	config.write('\n')

	for ii in xrange(0, len(allobj)):
		[objname] = allobj[ii].split('/')[-1:]
		config.write('#F#\tH:\\' + objname + '\t' + str(ii+1) + '\t1\n')

	print '\nDone\n'

if __name__ == "__main__":

	#take in directory of swc files
	main(sys.argv[1])
