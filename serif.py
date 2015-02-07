#!/usr/bin/python
#
# serif class definitions
#
#
import splines
import polygon
import nibs_qt
import control_vertex
import stroke_qt

import math
import time
import random

from PyQt4 import QtCore, QtGui

START=-1
END=1

#
# base class
#
class Serif(object):
	def __init__(self):
		self.strokes = []
		self.nib = None
		self.__x = 0
		self.__y = 0
	
	def setPos(self, x, y):
		self.__x = x
		self.__y = y
		for stroke in self.strokes:
			stroke.setPos(x, y)

	def getPos(self):
		return [int(self.__x), int(self.__y)]
	
	def setNib(self, nib):
		self.__nib = nib
		
	def draw(self, gc, nib=None):
		if not nib:
			nib = self.__nib
		
		for stroke in self.strokes:
			stroke.draw(gc, 0, nib)

#
# 
#
class Flick(Serif):
	def __init__(self, direction=START):
		Serif.__init__(self)
		self.__angle = 45
		self.__length = 5
		self.__mult = direction

	def setCtrlVertices(self, ctrlVerts):
		self.strokes[:] = []
		stroke = stroke_qt.Stroke()
		ctrlPts = []
		if (self.__mult == END):
			pos = ctrlVerts[-1]
			ctrlVertX = pos[0] - ctrlVerts[-2][0]
			ctrlVertY = pos[1] - ctrlVerts[-2][1]
		else:
			pos = ctrlVerts[0]
			ctrlVertX = pos[0] - ctrlVerts[1][0]
			ctrlVertY = pos[1] - ctrlVerts[1][1]

		if (ctrlVertX != 0):
			dx = self.__mult * abs(math.sin(math.radians(self.__angle)) * self.__length)
			dy = self.__mult * abs(math.cos(math.radians(self.__angle)) * self.__length)
		else:
			ctrlVertAngle = 0
			dx = self.__length
			dy = 0

		ctrlPts.append([pos[0], pos[1]])#[pos[0], pos[1]])
		ctrlPts.append([pos[0]+dx, pos[1]-dy])
		ctrlPts.append([pos[0]+dx+dx, pos[1]-dy-dy])
		ctrlPts.append([pos[0]+dx+dx+dx, pos[1]-dy-dy-dy])

		stroke.setCtrlVerticesFromList(ctrlPts)
		stroke.calcCurvePoints()
		self.strokes.append(stroke)
		#self.setPos(pos[0], pos[1])
		
		
	def resetCtrlVertices(self):
		ctrlVerts = self.strokes[0].getCtrlVerticesAsList()
		
		dx = self.__mult * abs(math.sin(math.radians(90-self.__angle)) * self.__length)
		dy = self.__mult * abs(math.cos(math.radians(90-self.__angle)) * self.__length)
		self.strokes[:] = []
		stroke = stroke_qt.Stroke()
		ctrlPts = []
		pos = ctrlVerts[0]
		
		ctrlPts.append([pos[0], pos[1]])#[pos[0], pos[1]])
		ctrlPts.append([pos[0]+dx, pos[1]-dy])
		ctrlPts.append([pos[0]+dx+dx, pos[1]-dy-dy])
		ctrlPts.append([pos[0]+dx+dx+dx, pos[1]-dy-dy-dy])

		stroke.setCtrlVerticesFromList(ctrlPts)
		stroke.calcCurvePoints()
		self.strokes.append(stroke)
		
		
		
	def setDirection(self, direction):
		if (direction == START) or (direction == END):
			self.__mult = direction

	def setLength(self, length):
		self.__length = length
		self.resetCtrlVertices()

	def setAngle(self, angle):
		self.__angle = angle
		self.resetCtrlVertices()
	

#
# 
#
class RoundedFlick(Serif):
	def __init__(self, direction=START):
		Serif.__init__(self)
		self.__angle = 45
		self.__length = 5
		self.__mult = direction
		
	def setCtrlVertices(self, ctrlVerts):
		self.strokes[:] = []
		stroke = stroke_qt.Stroke()
		ctrlPts = []
		if (self.__mult == END):
			pos = ctrlVerts[-1]
			ctrlVertX = pos[0] - ctrlVerts[-2][0]
			ctrlVertY = pos[1] - ctrlVerts[-2][1]
		else:
			pos = ctrlVerts[0]
			ctrlVertX = pos[0] - ctrlVerts[1][0]
			ctrlVertY = pos[1] - ctrlVerts[1][1]
		
		if (ctrlVertX != 0):
			ctrlVertAngle = math.atan(float(ctrlVertY)/float(ctrlVertX))
			dx = self.__mult * abs(math.cos(ctrlVertAngle) * self.__length*2)
			dy = self.__mult * abs(math.sin(ctrlVertAngle) * self.__length*2)
		else:
			ctrlVertAngle = 0
			dx = 0
			dy = self.__length
			
		ctrlPts.append([pos[0], pos[1]])
		ctrlPts.append([pos[0]+dx, pos[1]+dy])
		ctrlPts.append([pos[0]+dx, pos[1]+dy])
		lastPt_x = pos[0]+dx + (self.__mult * math.cos(math.radians(self.__angle)) * self.__length*2)
		lastPt_y = pos[1]+dy - (self.__mult * math.sin(math.radians(self.__angle)) * self.__length*2)
		ctrlPts.append([lastPt_x,lastPt_y])
		
		stroke.setCtrlVerticesFromList(ctrlPts)
		stroke.calcCurvePoints()
		self.strokes.append(stroke)
		#self.setPos(pos[0], pos[1])
	
	def setDirection(self, direction):
		if (direction == START) or (direction == END):
			self.__mult = direction
		
	def setLength(self, length):
		self.__length = length
			
	def setAngle(self, angle):
		self.__angle = angle
		

