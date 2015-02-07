#!/usr/bin/python
#
# stroke class definitions
#
#
import splines
import polygon
import nibs_qt
import control_vertex
import serif

import math
import time
import random


from PyQt4 import QtCore, QtGui

class Stroke(splines.BezierSpline):
	def __init__(self, dimension=2):
		splines.BezierSpline.__init__(self, dimension)
		#splines.CatmullRomSpline.__init__(self, 2.0)
		self.nib = None
		
		self.__startSerif = None
		self.__endSerif = None
		self.__startFlourish = None
		self.__endFlourish = None
		self.__x = 0
		self.__y = 0
		self.__handleSize = 10
		self.__boundBoxes = []
		self.__mainBoundBox = None
		self.__strokeCtrlVerts = []
		
		self.seed = time.localtime()
		
	def setPos(self, x, y):
		self.__x = x
		self.__y = y
		
	def getPos(self):
		return (int(self.__x), int(self.__y))
	
	def getHandlePos(self):
		return (int(self.__hx), int(self.__hy))
	
	def straighten(self):
		tempCv = []
		oldCv = splines.BezierSpline.getCtrlVertices(self)
		
		start = self.ctrlVerts[0]
		end = self.ctrlVerts[-1]
		
		dX = (end[0]-start[0])/(self.numVerts-1)
		dY = (end[1]-start[1])/(self.numVerts-1)
		
		for i in range (0, self.numVerts):
			tempCv.append([start[0]+dX*i, start[1]+dY*i])
		
		self.setCtrlVerticesFromList(tempCv)
		self.calcCurvePoints()
		
		return oldCv
			
	def setNib(self, nib):
		self.nib = nib
		
	def getNib(self):
		return self.nib
		
	def addEndSerif(self, distance):
		self.__endSerif = serif.Flick(serif.END)
		verts = self.getCtrlVerticesAsList()
		self.__endSerif.setCtrlVertices(verts)
		self.__endSerif.setLength(distance)
		if (self.nib):
			self.__endSerif.setAngle(self.nib.getAngle())
		
	def removeEndSerif(self):
		self.__endSerif = None
		
	def addStartSerif(self, distance):
		self.__startSerif = serif.Flick(serif.START)
		verts = self.getCtrlVerticesAsList()
		self.__startSerif.setCtrlVertices(verts)
		self.__startSerif.setLength(distance)
		if (self.nib):
			self.__startSerif.setAngle(self.nib.getAngle())

	def removeStartSerif(self):
		self.__startSerif = None

	def calcCurvePoints(self):
		numPts = splines.BezierSpline.getNumCurvePoints(self)
		splines.BezierSpline.setNumCurvePoints(self, numPts)
				         
		crvPts = splines.BezierSpline.calcCurvePoints(self)
		
		minx = 9999
		miny = 9999
		
		return crvPts[:]
	
	def calcCtrlVertices(self, pts):
		return splines.BezierSpline.calcCtrlVertices(self, pts)
	
	def getCtrlVertices(self):
		return self.__strokeCtrlVerts[:]
		
	def getCtrlVerticesAsList(self):
		pts = []
		for vert in self.__strokeCtrlVerts:
			l = vert.getLeftHandlePos()
			k = vert.getPos()
			r = vert.getRightHandlePos()
			
			if (l):
				pts.append(list(l))
			if (k):
				pts.append(list(k))
			if (r):
				pts.append(list(r))
				
		return list(pts)
		
	def setCtrlVerticesFromList(self, pts):
		splines.BezierSpline.setCtrlVertices(self, pts)
		self.__strokeCtrlVerts = []
		
		pos = 1
		newVert = control_vertex.controlVertex()
		
		for pt in pts:
			if (pos == 0):
				newVert = control_vertex.controlVertex()
				lPos = newVert.getLeftHandlePos()
				newVert.setLeftHandlePos(pt[0], pt[1])
				pos = 1
			elif (pos == 1):
				newVert.setPos(pt[0], pt[1])
				pos = 2
			elif (pos == 2):
				newVert.setRightHandlePos(pt[0], pt[1])
				pos = 0
				self.__strokeCtrlVerts.append(newVert)
				newVert = None
		
		if (newVert):
			self.__strokeCtrlVerts.append(newVert)
		
		
	
	def setCtrlVertices(self, ctrlVerts):
		self.__strokeCtrlVerts = ctrlVerts[:]
		self.updateCtrlVertices()
		
	def updateCtrlVertices(self):
		pts = self.getCtrlVerticesAsList()
		
		splines.BezierSpline.setCtrlVertices(self, pts)	
		self.calcCurvePoints()
		
	def deleteCtrlVertex(self, pt):
		if (pt == 0):
			self.__strokeCtrlVerts[pt+1].clearLeftHandlePos()
		elif (pt == len(self.__strokeCtrlVerts)-1):
			self.__strokeCtrlVerts[pt-1].clearRightHandlePos()
			
		self.__strokeCtrlVerts.remove(self.__strokeCtrlVerts[pt])
		self.updateCtrlVertices()
		self.calcCurvePoints()
	
	def addCtrlVertex(self, t, index):
		pts = self.getCtrlVerticesAsList()
		tmpCtrlVerts = self.getCtrlVertices()
		
		trueIndex = index*3
		
		p3 = pts[trueIndex]
		p2 = pts[trueIndex-1]
		p1 = pts[trueIndex-2]
		p0 = pts[trueIndex-3]
	
		newPts = []
		for i in range (0, 7):
			newPts.append([0,0])
			
		for k in range (0, 2):
			p0_1 = float((1.0-t)*p0[k] + (t * p1[k]))
			p1_2 = float((1.0-t)*p1[k] + (t * p2[k]))
			p2_3 = float((1.0-t)*p2[k] + (t * p3[k]))
 			p01_12 = float((1.0-t)*p0_1 + (t * p1_2))
			p12_23 = float((1.0-t)*p1_2 + (t * p2_3))
			p0112_1223 = float((1.0-t)*p01_12 + (t * p12_23))
		
			newPts[0][k] = p0[k]
			newPts[1][k] = p0_1
			newPts[2][k] = p01_12
			newPts[3][k] = p0112_1223
			newPts[4][k] = p12_23
			newPts[5][k] = p2_3
			newPts[6][k] = p3[k]
		
		pts[trueIndex-3:trueIndex+1] = newPts
		self.setCtrlVerticesFromList(pts)	
			
		self.calcCurvePoints()
				
	def draw(self, gc, showCtrlVerts=0, nib=None, selectedVert=-1):
		self.__boundBoxes = []
		self.__mainBoundBox = None
		minX = 9999
		minY = 9999
		maxX = 0
		maxY = 0
		
		random.seed(self.seed)
		if (self.nib):
			nib = self.nib
		elif (nib == None):
			print "ERROR: No nib provided to draw stroke\n"
			return
			
		gc.save()
		gc.translate(self.__x, self.__y)		
		
		curvePts = self.getCurvePoints()
		
		for i in range(0, (len(curvePts)-1)):
			
			if ((curvePts[i][0] == 0.0) and (curvePts[i][1] == 0.0)) and \
			   ((curvePts[i+1][0] == 0.0) and (curvePts[i+1][1] == 0.0)):
			   	continue
			else:
				bboxPts = None
					
				bboxPts = nib.draw(gc, curvePts[i][0],curvePts[i][1], \
				         curvePts[i+1][0],curvePts[i+1][1])
		
				if bboxPts:
					self.__boundBoxes.append(bboxPts)
					
					for pt in bboxPts:
						if pt[0] < minX:
							minX = pt[0]
						if pt[1] < minY:
							minY = pt[1]
						if pt[0] > maxX:
							maxX = pt[0]
						if pt[1] > maxY:
							maxY = pt[1]
				
					if (i == 0):
						tmpPt = bboxPts[3]
		
		self.__mainBoundBox = [minX, minY, maxX, maxY]
		
		if (self.__startSerif):
			verts = self.getCtrlVerticesAsList()
			self.__startSerif.setCtrlVertices(verts)
			self.__startSerif.setAngle(nib.getAngle())
			self.__startSerif.draw(gc, nib)
			
		if (self.__endSerif):
			verts = self.getCtrlVerticesAsList()
			self.__endSerif.setCtrlVertices(verts)
			self.__endSerif.setAngle(nib.getAngle())
			self.__endSerif.draw(gc, nib)
			
		if (showCtrlVerts):
						
			for vert in self.__strokeCtrlVerts:
				vert.draw(gc)
		
		gc.restore()
		
	def insideStroke(self, pt):
		inside = 0
		
		modPt = (pt[0]-self.__x, pt[1]-self.__y)
		
		numCtrlVerts = len(self.__strokeCtrlVerts)
		numBboxes = len(self.__boundBoxes)
		boxesPerVert = numBboxes / (numCtrlVerts - 1)
		
		bboxIdx = 0
		
		# check against main bounding box first
		if (modPt[0] < self.__mainBoundBox[0]) or \
		   (modPt[0] > self.__mainBoundBox[2]) or \
		   (modPt[1] < self.__mainBoundBox[1]) or \
		   (modPt[1] > self.__mainBoundBox[3]):
			inside = 0
		else:
			for quad in self.__boundBoxes:
				
				if (polygon.__windingNum__(modPt, quad, 4) == 1):
					inside = 1
					break
					
				bboxIdx = bboxIdx + 1
		
		vertIdx = 0		
		if (inside):
			for i in range(1, numCtrlVerts):
				if (bboxIdx < (i * boxesPerVert)) :
					vertIdx = i
					break
			while (bboxIdx > boxesPerVert):
				bboxIdx = bboxIdx - boxesPerVert
		
		return vertIdx, float(bboxIdx)/float(boxesPerVert)
	
	def getBoundRect(self):
		return QtCore.QRect(self.__mainBoundBox[0], self.__mainBoundBox[1],
							self.__mainBoundBox[2], self.__mainBoundBox[3])	

