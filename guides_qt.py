#!/usr/bin/python
#

import math
from PyQt4 import QtCore, QtGui

class guideLines(object):
	def __init__(self):
		# units are nibwidths from baseline
		self.__baseHeight = 5
		self.__width = 4
		self.__ascentHeight = 3
		self.__descentHeight = 3
		self.__capHeight = 2
		# nibwidths between rows
		self.__gapHeight = 2
		
		# degrees
		self.__angle = 5
		self.__angleDX = math.tan(math.radians(self.__angle))
		self.__baselineY = 300
		self.__baseX = 400
		
		self.__lineColor = QtGui.QColor(200, 195, 180)
		self.__lineColorLt = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30)
		self.__lineColorAlpha = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30, 128)
		self.__linePenLt = QtGui.QPen(self.__lineColorLt, 1, QtCore.Qt.SolidLine)
		self.__linePen = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.SolidLine)
		self.__linePen2 = QtGui.QPen(self.__lineColor, 2, QtCore.Qt.SolidLine)
		self.__linePenDotted = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.DotLine)
		self.__spacerBrush = QtGui.QBrush(self.__lineColorAlpha, QtCore.Qt.SolidPattern)
		self.__lastNibWidth = 0
		self.__gridPts = []
	
	def setAngle(self, angle):
		self.__angle = angle
		self.__angleDX = math.tan(math.radians(angle))
		
	def getAngle(self):
		return self.__angle
		
	angle = property(getAngle, setAngle)
	
	def setLineColor(self, linecolor):
		self.__lineColor = linecolor
		self.__lineColorLt = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30)
		self.__lineColorAlpha = QtGui.QColor(self.__lineColor.red()+30, self.__lineColor.green()+30, self.__lineColor.blue()+30, 192)
		self.__linePenLt = QtGui.QPen(self.__lineColorLt, 1, QtCore.Qt.SolidLine)
		self.__linePen = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.SolidLine)
		self.__linePen2 = QtGui.QPen(self.__lineColor, 2, QtCore.Qt.SolidLine)
		self.__linePenDotted = QtGui.QPen(self.__lineColor, 1, QtCore.Qt.DotLine)
		self.__spacerBrush = QtGui.QBrush(self.__lineColorAlpha, QtCore.Qt.SolidPattern)
		
	def getLineColor(self):
		return self.__lineColor

	lineColor = property(getLineColor, setLineColor)
	
	def setBaseHeight(self, height):
		self.__baseHeight = height
	
	def getBaseHeight(self):
		return self.__baseHeight
		
	baseHeight = property(getBaseHeight, setBaseHeight)
	
	def setAscent(self, height):
		self.__ascentHeight = height #+self.__baseHeight
		
	def getAscent(self):
		return self.__ascentHeight #-self.__baseHeight

	ascentHeight = property(getAscent, setAscent)

	def setCapHeight(self, height):
		self.__capHeight = height #+self.__baseHeight
		
	def getCapHeight(self):
		return self.__capHeight #-self.__baseHeight

	capHeight = property(getCapHeight, setCapHeight)
	
	def setDescent(self, height):
		self.__descentHeight = height

	def getDescent(self):
		return self.__descentHeight

	descentHeight = property(getDescent, setDescent)
	
	def setGap(self, height):
		self.__gapHeight = height

	def getGap(self):
		return self.__gapHeight

	gapHeight = property(getGap, setGap)
	
		
	def setBaselineY(self, y):
		self.__baselineY = y
		
	def getBaselineY(self):
		return self.__baselineY
	
	baselineY = property(getBaselineY, setBaselineY)
	def calculateGridPts(self, size, nibWidth=0):
		self.__gridPts = []
		if nibWidth == 0:
			if self.__lastNibWidth == 0:
				return
			else:
				nibWidth = self.__lastNibWidth
			
		wdiv2 = size.width()/2
		hdiv2 = size.height()/2
		baseWidth = nibWidth * self.__width
		halfBaseWidth = nibWidth * self.__width / 2
		baseHeight = nibWidth * self.__baseHeight
		ascentHeight = nibWidth * (self.__ascentHeight + self.__baseHeight)
		descentHeight = nibWidth * self.__descentHeight
		capHeight = nibWidth * (self.__capHeight + self.__baseHeight)
		gapHeight = nibWidth * self.__gapHeight
		
		dx = self.__angleDX * (size.height() - self.__baselineY)
		dist = halfBaseWidth + baseWidth
		baseDx = self.__angleDX * self.__baselineY
		
		vpos = self.__baselineY
		while (vpos > 0):
			vpos = vpos - (ascentHeight + descentHeight + gapHeight)
			
		vpos = vpos - hdiv2
		#ddxx = float((0 - dx - baseDx) / size.height())
		#print ddxx
		while (vpos < (size.height() + gapHeight + ascentHeight)):
			startPos = self.__baseX - halfBaseWidth   #float(self.__baseX) * ddxx #0 - baseDx - baseWidth 
			while (startPos > 0):
				startPos = startPos - baseWidth
			
			startPos = startPos - wdiv2
				
			while (startPos < size.width()):
				pos = startPos+(float(vpos-(baseHeight))*-self.__angleDX)
				self.__gridPts.append([int(pos), int(vpos-(baseHeight))])
				pos = startPos+((vpos-(capHeight))*-self.__angleDX)
				self.__gridPts.append([int(pos), int(vpos-(capHeight))])
				pos = startPos+((vpos-(ascentHeight))*-self.__angleDX)
				self.__gridPts.append([int(pos), int(vpos-(ascentHeight))])
				pos = startPos+(float(vpos)*-self.__angleDX)
				self.__gridPts.append([int(pos), int(vpos)])
				pos = startPos+(float(vpos+(descentHeight))*-self.__angleDX)
				self.__gridPts.append([int(pos), int(vpos+(descentHeight))])
				
				startPos = startPos + baseWidth
		
			vpos = vpos + ascentHeight + descentHeight + gapHeight
	
	def getGridPts(self):
		return self.__gridPts[:]
		
	def draw(self, gc, size, nib):
		nibWidth = nib.getWidth() << 1
		self.__lastNibWidth = nibWidth
		baseWidth = nibWidth * self.__width
		halfBaseWidth = nibWidth * self.__width / 2
		baseHeight = nibWidth * self.__baseHeight
		ascentHeight = nibWidth * (self.__ascentHeight + self.__baseHeight)
		descentHeight = nibWidth * self.__descentHeight
		capHeight = nibWidth * (self.__capHeight + self.__baseHeight)
		gapHeight = nibWidth * self.__gapHeight
		self.__baseX = (size.width() / 2)
		self.__baselineY = (size.height() / 2)
		self.calculateGridPts(size, nibWidth)
			
		dx = self.__angleDX * (size.height() - self.__baselineY)
		baseDx = self.__angleDX * self.__baselineY
		
		# draw horizontal grid
		dist = halfBaseWidth + baseWidth
		pos = baseWidth
		gc.setPen(self.__linePenLt)
		while (pos < size.width()):
			gc.drawLine(self.__baseX-(dist)-dx, size.height(), self.__baseX-(dist)+baseDx, 0)
			gc.drawLine(self.__baseX+(dist)-dx, size.height(), self.__baseX+(dist)+baseDx, 0)
			
			dist = dist + baseWidth
			pos = pos + baseWidth
			
		gc.setPen(self.__linePen2)
			
		gc.drawLine(0, self.__baselineY, size.width(), self.__baselineY)
			
		gc.setPen(self.__linePen)
			
		gc.drawLine(0, self.__baselineY-(baseHeight), size.width(), self.__baselineY-(baseHeight))
		
		gc.drawLine(0, self.__baselineY-(ascentHeight), size.width(), self.__baselineY-(ascentHeight))
		gc.drawLine(0, self.__baselineY+(descentHeight), size.width(), self.__baselineY+(descentHeight))
		
		gc.setPen(self.__linePenDotted)
		gc.drawLine(0, self.__baselineY-capHeight, size.width(), self.__baselineY-capHeight)
		
		vpos = self.__baselineY - ascentHeight - gapHeight - descentHeight
		while (vpos > (0 - gapHeight - descentHeight)):
			gc.setPen(self.__linePen2)
			gc.drawLine(0, vpos, size.width(), vpos)

			gc.setPen(self.__linePen)

			gc.drawLine(0, vpos-(baseHeight), size.width(), vpos-(baseHeight))

			gc.drawLine(0, vpos-(ascentHeight), size.width(), vpos-(ascentHeight))
			gc.drawLine(0, vpos+(descentHeight), size.width(), vpos+(descentHeight))

			gc.setPen(self.__linePenDotted)
			gc.drawLine(0, vpos-capHeight, size.width(), vpos-capHeight)
			gc.setBrush(self.__spacerBrush)
			gc.drawRect(0, vpos+descentHeight, size.width(), gapHeight)
			vpos = vpos - ascentHeight - descentHeight - gapHeight
			
		vpos = self.__baselineY + ascentHeight + gapHeight + descentHeight
		while (vpos < (size.height() + gapHeight + ascentHeight)):
			gc.setPen(self.__linePen2)
			gc.drawLine(0, vpos, size.width(), vpos)

			gc.setPen(self.__linePen)

			gc.drawLine(0, vpos-(baseHeight), size.width(), vpos-(baseHeight))

			gc.drawLine(0, vpos-(ascentHeight), size.width(), vpos-(ascentHeight))
			gc.drawLine(0, vpos+(descentHeight), size.width(), vpos+(descentHeight))

			gc.setPen(self.__linePenDotted)
			gc.drawLine(0, vpos-capHeight, size.width(), vpos-capHeight)
			gc.setBrush(self.__spacerBrush)
			gc.drawRect(0, vpos-ascentHeight-gapHeight, size.width(), gapHeight)
			vpos = vpos + ascentHeight + gapHeight + descentHeight
			
		gc.setPen(self.__linePen)
		gc.drawLine(self.__baseX-(halfBaseWidth)-dx, size.height(), self.__baseX-(halfBaseWidth)+baseDx, 0)
		gc.drawLine(self.__baseX+(halfBaseWidth)-dx, size.height(), self.__baseX+(halfBaseWidth)+baseDx, 0)
		
		return
		
