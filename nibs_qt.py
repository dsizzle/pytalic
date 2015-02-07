#!/usr/bin/python
#
# nibs class definitions
#

import math
import random
import time

import shapes.polygon

from PyQt4 import QtCore, QtGui

# move color to stroke
class Nib:
	def __init__(self, width=5, angle=40, color=QtGui.QColor(125,25,25)): #FL_BLACK):
		if (angle < 0):
			angle = 180+angle
				
		angle = angle % 180
		self.width = width
		self.angle = angle
		self.angleRads = (self.angle * math.pi) / 180.0		

		self.color = color
		self.nibwidth_x = self.width * math.cos(self.angle * 
		                    math.pi / 180.0)
		self.nibwidth_y = self.width * math.sin(self.angle * 
                            math.pi / 180.0)

		self.seed = time.localtime()
		self.color = color
		self.pen = QtGui.QPen(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 220), QtCore.Qt.SolidPattern)
	
	def getColor(self):
		return self.color
	
	def setAlpha(self, alpha):
		self.pen = QtGui.QPen(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), ((90.0 / 255.0) * alpha)), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), ((220.0 / 255.0) * alpha)), QtCore.Qt.SolidPattern)
		
	def resetAlpha(self):
		self.pen = QtGui.QPen(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 220), QtCore.Qt.SolidPattern)
		
	def setColor(self, color):
		self.color = color
		self.pen = QtGui.QPen(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 90), 1, QtCore.Qt.SolidLine)
		self.brush = QtGui.QBrush(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 220), QtCore.Qt.SolidPattern)
		
	def setAngle(self, angle):
		if (angle < 0):
			angle = 180+angle
		
		angle = angle % 180
		
		self.angle = angle
		self.angleRads = (self.angle * math.pi) / 180.0		

		self.nibwidth_x = self.width * math.cos(self.angleRads)
		self.nibwidth_y = self.width * math.sin(self.angleRads)
	
	def getAngle(self):
	   	return self.angle
    	
   	def setWidth(self, width):
   		self.width = width
   		self.nibwidth_x = self.width * math.cos(self.angleRads)
		self.nibwidth_y = self.width * math.sin(self.angleRads)
			
	def getWidth(self):
		return self.width
                            
	def draw(self, gc, x,y,x2=None,y2=None, seed=None):

		pts = polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = polygon.normalizePolyRotation(pts)
		
		poly = QtGui.QPolygon(4)
		poly.setPoint(0, QtCore.QPoint(pts[0][0],pts[0][1]))
		poly.setPoint(1, QtCore.QPoint(pts[1][0],pts[1][1]))
		poly.setPoint(2, QtCore.QPoint(pts[2][0],pts[2][1]))
		poly.setPoint(3, QtCore.QPoint(pts[3][0],pts[3][1]))
		
		pen = self.pen
		nullpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1, QtCore.Qt.SolidLine)
		brush = self.brush
		
		gc.setPen(nullpen)
		gc.setBrush(brush)
		
		gc.setPen(nullpen)
		gc.drawPolygon(poly, QtCore.Qt.WindingFill)
		gc.setPen(pen)
		gc.drawPolyline(poly)
		
		return pts
	
	def vertNibWidthScale (self, dc, x, y, num=2):
		tempAngle = self.angle
		
		self.setAngle(90)
		
		random.seed(self.seed)
		for i in range (0, int(math.ceil(num))):
			ypos = y+self.nibwidth_y*i*2
			xpos = x
			if i % 2 == 0:
				xpos = x+self.width*2
			
			self.draw(dc, xpos, ypos, xpos+self.width*2, ypos)
			
		self.setAngle(tempAngle)
	
	def horzNibWidthScale (self, dc, x, y, num=2):
		tempAngle = self.angle
			
		self.setAngle(0)
		
		random.seed(self.seed)	
		for i in range (0, int(math.ceil(num))):
			xpos = x+self.nibwidth_y*i*2
			ypos = y
			if i % 2 == 0:
				ypos = y+self.width*2
			
			self.draw(dc, xpos, ypos, xpos, ypos+self.width*2, self.seed)
				
		self.setAngle(tempAngle)

	
class ScrollNib(Nib):
	def __init__(self, width=10, angle=40, split=5, color=QtGui.QColor(125,25,25)):
		self.__width = width-split
		self.split = split
		if split>width:
			split = 0
		Nib.__init__(self, width, angle, color)
		self.__split_x = (split) * math.cos(self.angle * 
		                    math.pi / 180.0)
		self.__split_y = (split) * math.sin(self.angle * 
                            math.pi / 180.0)
        
	def setSplitSize(self, splitSize):
		if (splitSize > self.width):
			splitSize = 0
			
		self.split = splitSize
	
		self.__split_x = (splitSize) * math.cos(self.angle * 
							math.pi / 180.0)
		self.__split_y = (splitSize) * math.sin(self.angle * 
							math.pi / 180.0)
	
	def getSplitSize(self):
		return self.split
		
	def draw(self, gc, x,y,x2=None,y2=None):
		
		pts = polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = polygon.normalizePolyRotation(pts)
		
		lpts = polygon.calcPoly(x, y, self.__split_x, self.__split_y, x2, y2)
		
		lpoly = QtGui.QPolygon(4)
		lpoly.setPoint(0, QtCore.QPoint(lpts[0][0],lpts[0][1]))
		lpoly.setPoint(1, QtCore.QPoint(lpts[1][0],lpts[1][1]))
		lpoly.setPoint(2, QtCore.QPoint(lpts[2][0],lpts[2][1]))
		lpoly.setPoint(3, QtCore.QPoint(lpts[3][0],lpts[3][1]))
		
		rpts = polygon.calcPoly(x+self.nibwidth_x+self.__split_x, 
			y-self.nibwidth_y-self.__split_y, 
			self.__split_x, self.__split_y, 
			x2+self.nibwidth_x+self.__split_x, y2-self.nibwidth_y-self.__split_y)
		
		rpoly = QtGui.QPolygon(4)
		rpoly.setPoint(0, QtCore.QPoint(rpts[0][0],rpts[0][1]))
		rpoly.setPoint(1, QtCore.QPoint(rpts[1][0],rpts[1][1]))
		rpoly.setPoint(2, QtCore.QPoint(rpts[2][0],rpts[2][1]))
		rpoly.setPoint(3, QtCore.QPoint(rpts[3][0],rpts[3][1]))
		
		pen = self.pen
		nullpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1, QtCore.Qt.SolidLine)
		brush = self.brush
		gc.setPen(nullpen)
		gc.setBrush(brush)
		
		gc.setPen(nullpen)
		gc.drawPolygon(lpoly, QtCore.Qt.WindingFill)
		gc.drawPolygon(rpoly, QtCore.Qt.WindingFill)
		
		gc.setPen(pen)
		gc.drawPolyline(lpoly)
		gc.drawPolyline(rpoly)
		
		return pts
		
	def setAngle(self, angle):
		if (angle < 0):
			angle = 180+angle

		angle = angle % 180

		self.angle = angle
		self.angleRads = (self.angle * math.pi) / 180.0		

		self.nibwidth_x = self.width * math.cos(self.angleRads)
		self.nibwidth_y = self.width * math.sin(self.angleRads)
		
		self.__split_x = (self.split) * math.cos(self.angle * 
		                    math.pi / 180.0)
		self.__split_y = (self.split) * math.sin(self.angle * 
                            math.pi / 180.0)
# 	 				 		
# 		
# 	
class BrushNib(Nib):
	def __init__(self, width=5, angle=40, color=QtGui.QColor(125,25,25)):
 		
		Nib.__init__(self, width, angle, color)
		self.__slope = float(self.nibwidth_y / self.nibwidth_x)
 		
	def draw(self, dc, x, y, x2=None,y2=None):
			
		pts = polygon.calcPoly(x, y, self.nibwidth_x, self.nibwidth_y, x2, y2)
		pts = polygon.normalizePolyRotation(pts)
		
		xp = x - self.nibwidth_x
		xp2 = x + self.nibwidth_x
		yp = y + self.nibwidth_y
		yp2 = y - self.nibwidth_y
		
		if (x2 == None) and (y2 == None):
			x2 = x
			y2 = y
		
		
		xxp = x2 - self.nibwidth_x
		xxp2 = x2 + self.nibwidth_x
		yyp = y2 + self.nibwidth_y
		yyp2 = y2 - self.nibwidth_y
		
		steep = abs(yp2 - yp) > abs(xp2 - xp)
						
		if (steep):
			xp, yp = yp, xp
			xp2, yp2 = yp2, xp2
			xxp, yyp = yyp, xxp
			xxp2, yyp2 = yyp2, xxp2
		if (xp > xp2):
			xp, xp2 = xp2, xp
			yp, yp2 = yp2, yp
			xxp, xxp2 = xxp2, xxp
			yyp, yyp2 = yyp2, yyp
		
		dx = xp2 - xp
		dy = abs(yp2 - yp)
		err = - dx / 2
		yy = yp
		yy2 = yyp
		
		stepsize = 2
		if (yp < yp2):
			ystep = stepsize
		else:
			ystep = -stepsize
		
		xx2 = xxp
		
		looprange = int(dx / (stepsize))
		
		#dc.BeginDrawing()
		
		self.pen = QtGui.QPen(QtGui.QColor(self.color.red(), self.color.green(), self.color.blue(), 200), stepsize*3, QtCore.Qt.SolidLine)
		pen = self.pen
		brush = self.brush
		
		dc.setPen(pen)
		dc.setBrush(brush)
		
		xx = xp
		for i in range (0, looprange):
			#xr = random.random()*2.0 - 1.0
			#yr = random.random()*2.0 - 1.0
			#xr2 = random.random()*2.0 - 1.0
			#yr2 = random.random()*2.0 - 1.0
			
			#xr = random.random()*(stepsize*2.0) - 1.0
			#yr = random.random()*(stepsize*2.0) - 1.0
			#xr2 = random.random()*(stepsize*2.0) - 1.0
			#yr2 = random.random()*(stepsize*2.0) - 1.0
			
			xr = random.random()*4.0 - 1.0
			yr = random.random()*4.0 - 1.0
			xr2 = random.random()*4.0 - 1.0
			yr2 = random.random()*4.0 - 1.0
			
			if (i == 0) or (i == looprange-1):
				xr = random.random()*1.5 - 1.0
				yr = random.random()*1.5 - 1.0
				xr2 = random.random()*1.5 - 1.0
				yr2 = random.random()*1.5 - 1.0
				
				
			plotx1 = xx
			ploty1 = yy
			plotx2 = xx2
			ploty2 = yy2
			
			err = err + dy
			if err > 0:
				yy = yy+ystep
				yy2 = yy2+ystep
				err = err - dx
			
			xx = xx+stepsize
			xx2 += stepsize
			
			if steep:
				plotx1, ploty1 = ploty1, plotx1
				plotx2, ploty2 = ploty2, plotx2
	
			dc.drawLine(plotx1+xr, ploty1+yr, plotx2+xr2, ploty2+yr2)
			
		
		return pts
