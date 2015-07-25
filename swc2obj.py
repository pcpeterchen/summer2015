'''
Author: Peter Chen
Date: 7/22/2015
Project: swc2obj.py

Purpose: convert swc files to obj files

Note: Majority of program was written by translating to python buildOBJ.m, 
	  points2cylinder.m, and saveobjmesh.m from the trees toolbox

Usage:  python swc2obj.py <SWC file>
Default Example: python swc2obj.py example1.swc
'''
from __future__ import division
from pdb import set_trace as bp
from collections import Counter
import sys
import os
import glob
import subprocess
import scipy.io
import math
import numpy as np
import random
import natsort
import shutil


#  build an obj.  Read in the swc file and convert it to obj
#  return the name of the path to the obj files
def buildOBJ(file):
	f = open(file, 'r')
	data = f.readlines()
	path = os.path.dirname(os.path.realpath(file))
	temppath = path + '/swc2objtemp'

	if os.path.exists(temppath):
		shutil.rmtree(temppath)
	os.makedirs(temppath)

	# read in swc data
	l = [i[:-1] for i in data if i[0] is not '#']
	ll = [i.split(' ') for i in l]
	a = np.asarray(ll)
	indx = a[:,0].astype(np.int)
	objType = a[:,1]
	X = a[:,2].astype(np.float)
	Y = a[:,3].astype(np.float)
	Z = a[:,4].astype(np.float)
	rad = a[:,5].astype(np.float)
	parent = a[:,6].astype(np.int)
	parents = []
	children = []

	# build obj at each line of swc file
	for ii in xrange(1, len(indx)-1):
		par = parent[ii-1]	
		child = indx[ii-1]
		parents.append(par)
		children.append(indx[ii])
		if par != parent[0]:
			if par != child:
				try:
					chindex = np.where(indx == child)[0][0]
					parindex = np.where(indx == par)[0][0]
					childpts = [X[chindex], Y[chindex], Z[chindex]]
					parentpts = [X[parindex], Y[parindex], Z[parindex]]	
					if childpts == parentpts:
						print childpts
						print parentpts
						print child
					[x,y,z] = points2cylinder(rad[parindex], 10, 
						parentpts, childpts)
					name = temppath + '/' + str(par) + '_' + str(child) \
					 + '.obj'
					saveobjmesh(name, x, y, z)
				except:
					continue
	parents.append(parent[ii+1])
	
	return temppath


#  write obj to file
#  take in String name, lists x, y, z
def saveobjmesh(name, x, y, z, nx=None, ny=None, nz=None):
	normals = 1
	if nx is None:
		nx = []
	if ny is None:
		ny = []
	if nz is None:
		nz = []
	if len(sys.argv) < 5:
		normals = 0

	l = len(x)
	h = len(x[0])
	n = np.zeros((l, h))
	fid = open(name, 'w')
	nn = 1

	for i in xrange(0, l):
		for j in xrange(0, h):
			n[i,j] = nn
			fid.write('v %f %f %f\n' % (x[i,j], y[i,j], z[i,j]))
			
			if normals == 1:
				fid.write('vn %f %f %f\n' % (nx[i,j], ny[i,j], nz[i,j]))
			nn = nn + 1
	
	fid.write('g mesh\n')
	for i in xrange(0, l-1):
		for j in xrange(0, h-1):
			if normals == 1:
				fid.write('f %d/%d/%d %d/%d/%d %d/%d/%d %d/%d/%d\n' % (n[i,j],
				n[i,j], n[i,j], n[i+1,j], n[i+1,j], n[i+1,j], n[i+1,j+1], 
				n[i+1,j+1], n[i+1,j+1], n[i,j+1], n[i,j+1], n[i,j+1]))
			else:
				fid.write('f %d/%d %d/%d %d/%d %d/%d\n' % (n[i,j], n[i,j], 
					n[i+1,j], n[i+1,j], n[i+1,j+1], n[i+1,j+1], n[i,j+1], 
					n[i,j+1]))
	fid.write('g\n\n')
	fid.close()


#  calculate the cylinder between two point and create the cylinder
#  take in radius R, lists r1 and r2, and the number of vertecies N
#  return list of X, Y, and Z values
def points2cylinder(R, N, r1, r2):
	theta = np.linspace(0, 2*math.pi, N)
	R = [R, R]
	m = 2

	#preallocate memory
	X = np.zeros((m, N))
	Y = np.zeros((m, N))
	Z = np.zeros((m, N))

	#normalized vectors
	#cylinder axis described by: r(t)=r1+v*t for 0<t<1
	rr = np.subtract(r2, r1)
	v = rr / math.sqrt(np.dot(rr,rr.conj().transpose()))
	R2 = np.random.rand(1,3)	#linear independent vector (of v)
	#orthogonal vector to v
	x2 = v - R2 / (np.dot(R2, v.conj().transpose()))
	#orthogonal vector to v
	x2 = x2 / math.sqrt(np.dot(x2, x2.conj().transpose()))
	x3 = np.cross(v, x2)	#vector orthonormal to v and x2
	x3 = x3 / math.sqrt(np.dot(x3, x3.conj().transpose()))

	r1x = r1[0]
	r1y = r1[1]
	r1z = r1[2]
	r2x = r2[0]
	r2y = r2[1]
	r2z = r2[2]
	vx = v[0]
	vy = v[1]
	vz = v[2]
	x2x = x2[0][0]
	x2y = x2[0][1]
	x2z = x2[0][2]
	x3x = x3[0][0]
	x3y = x3[0][1]
	x3z = x3[0][2]

	time = np.linspace(0,1,m)
	for j in xrange(0, m):
		t = time[j]
		eggs = r2x-r1x
		cosTheta = []
		for each in xrange(0, len(theta)):
			cosTheta.append(math.cos(theta[each]))
		sinTheta = []
		for each in xrange(0, len(theta)):
			sinTheta.append(math.sin(theta[each]))
		X[j,] = r1x + (r2x-r1x) * t + np.multiply(R[j], 
			np.multiply(cosTheta, x2x)) + np.multiply(R[j], 
			np.multiply(sinTheta, x3x))
		Y[j,] = r1y + (r2y-r1y) * t + np.multiply(R[j], 
			np.multiply(cosTheta, x2y)) + np.multiply(R[j], 
			np.multiply(sinTheta, x3y))
		Z[j,] = r1z + (r2z-r1z) * t + np.multiply(R[j], 
			np.multiply(cosTheta, x2z)) + np.multiply(R[j], 
			np.multiply(sinTheta, x3z))
	return X, Y, Z


#  create the command name for meshlab specified for 'count'
#  glob is the name of all the OBJ in the command
#  count is the number of OBJ in the command
#  index is the current number of OBJ needed processing
def commandname(glob, count, index):
	oneglob = ''
	for ii in xrange(index, index + count-1):
		oneglob = oneglob + glob[ii] + ' '
	oneglob = oneglob + glob[(count-1) + index]
	return oneglob	


def main(file):

	# read in data and create the obj files
	path = os.path.dirname(os.path.realpath(file))
	scriptpath = os.getcwd()
	
	[yyy] = file.split('.')[:-1]
	filename = str(yyy)
	completename = filename + '.obj'

	if os.path.isfile(completename):
		os.remove(completename)

	temppath = buildOBJ(file)

	dir = glob.glob(temppath + '/*.obj')
	dir = natsort.natsorted(dir)

	# loop through each .obj in the path and mesh it together until 
	# only one obj remains
	index = 0
	globcount = 0
	for ii in xrange(0, len(dir)):
		
		if (len(dir) - index) > 100:
			globcount = 100
		else:
			globcount = (len(dir) - index)
			break

		oneglob = commandname(dir, globcount, index)
		index += globcount
		mcommand = 'meshlabserver -i ' + oneglob + ' ' + completename \
				+ ' -o ' + completename + ' -s ' + scriptpath + '/flatten.mlx'
		m = subprocess.call([mcommand], shell=True)	
		if m!= 0:
			subprocess.check_output([mcommand], shell=True)
			print subprocess.CalledProcessError.output

	oneglob = commandname(dir, globcount, index)
	mcommand = 'meshlabserver -i ' + oneglob + ' ' + completename \
				+ ' -o ' + completename + ' -s ' + scriptpath + '/flatten.mlx'
	m = subprocess.call([mcommand], shell=True)
	if m!= 0:
		subprocess.check_output([mcommand], shell=True)
		print subprocess.CalledProcessError.output
	
	invert = 'meshlabserver -i ' + completename + ' -o ' \
			+ completename	+ ' -s ' + scriptpath + '/invert.mlx'
	m = subprocess.call([invert], shell=True)
	if m!= 0:
		subprocess.check_output([invert], shell=True)
		print subprocess.CalledProcessError.output

	# shutil.rmtree(temppath)

if __name__ == "__main__":

	if os.path.isfile('./flatten.mlx') == False:
		print "Error: No flatten.mlx in directory"
		sys.exit()


	if os.path.isfile('./invert.mlx') == False:
		print "Error: No invert.mlx in directory"
		sys.exit()

	if len(sys.argv) > 2:
		print """Error: too many arguments.\ntry\n~python meshlabkicker.py 
		arg1 (where arg1 is an .swc file)"""
		sys.exit()

	if len(sys.argv) < 2:
		print """Error: too few arguments.\ntry\n~python meshlabkicker.py 
		arg1 (where arg1 is an .swc file)"""
		sys.exit()

	main(sys.argv[1])