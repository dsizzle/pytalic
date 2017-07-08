import nibs_qt
import stroke_qt
from PyQt4 import QtCore, QtGui

class strokeInstance(object):
	def __init__(self, parent=None):
		self.__stroke = None
		self.__x = 0
		self.__y = 0
		self.__instNib = None
		self.__color = QtGui.QColor(128, 128, 192, 90)
		self.__boundBoxes = []
		self.__mainBoundBox = None
		self.__parent = parent
		self.__dkGrayPen = (128,128,128,QtCore.Qt.DotLine) #QtGui.QBrush(QtGui.QColor(128,128,128), wx.SOLID)
		self.__clearBrush = (0,0,0,QtCore.Qt.NoBrush) #QtGui.QBrush(QtGui.QColor(0,0,0), wx.TRANSPARENT)
		
	def __del__(self):
		if self.__stroke:
			self.__stroke.removeInstance(self)

	def setPos(self, x, y):
		self.__x = x
		self.__y = y
	
	def getPos(self):
		return (int(self.__x), int(self.__y))

	def setStroke(self, stroke):
		if self.__stroke:
			self.__stroke.removeInstance(self)

		self.__stroke = stroke
		self.__nib = nibs_qt.Nib()
		tmpNib = stroke.getNib()
		
		(self.__x, self.__y) = stroke.getPos()

		if tmpNib:
			self.__nib.fromNib(tmpNib)
			self.__nib.setColor(self.__color)
			
		self.__stroke.addInstance(self)

	def getStroke(self):
		return self.__stroke

	def setParent(self, parent):
		self.__parent = parent

	def getParent(self):
		return self.__parent

	def getNib(self):
		return self.__nib

	def getStartSerif(self):
		return self.__stroke.getStartSerif()

	def getEndSerif(self):
		return self.__stroke.getEndSerif()

	def draw(self, gc, showCtrlVerts=0, nib=None, selectedVert=-1):

		if self.__stroke == None:
			return

		if nib is not None:
			self.__nib = nibs_qt.Nib()
			self.__nib.fromNib(nib)
			self.__nib.setColor(self.__color)

		strokeToDraw = stroke_qt.Stroke(fromStroke=self.__stroke)

		#
		# perform overrides
		#

		(stroke_x, stroke_y) = self.__stroke.getPos()		
		gc.save()

		gc.translate(-stroke_x, -stroke_y)
		gc.translate(self.__x, self.__y)

		strokeToDraw.draw(gc, 0, self.__nib, selectedVert)
		self.__mainBoundBox = strokeToDraw.getBoundRect()
		gc.restore()

		if showCtrlVerts:
			gc.save()

			gc.translate(self.__x, self.__y)
			gc.setBrush(QtGui.QBrush(QtGui.QColor(self.__clearBrush[0], self.__clearBrush[1], self.__clearBrush[2]), self.__clearBrush[3]))
			gc.setPen(QtGui.QPen(QtGui.QColor(self.__dkGrayPen[0], self.__dkGrayPen[1], self.__dkGrayPen[2],128), 2, self.__dkGrayPen[3], QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
		
			gc.drawRect(self.__mainBoundBox)
			
			gc.restore()

		self.__boundBoxes = strokeToDraw.getBoundBoxes() #True)

	def getBitmap(self):
		return self.__stroke.getBitmap()

	def getHitPoint(self, idx):
		return self.__stroke.getHitPoint(idx)

	def getBoundRect(self):
		return self.__stroke.getBoundRect()

	def insideStroke(self, pt):
		pos = self.__stroke.getPos()
		delta = [pos[0]-self.__x, pos[1]-self.__y]

		normPt = [pt[0]+delta[0], pt[1]+delta[1]] 

		if self.__mainBoundBox:
			strokeToTest = stroke_qt.Stroke(fromStroke=self.__stroke)
			strokeToTest.setBoundRect(self.__mainBoundBox)
			strokeToTest.setBoundBoxes(self.__boundBoxes)

			(vertIdx, origbboxIdx, idxPerVert) = strokeToTest.insideStroke(normPt)
		else:
			vertIdx = 0
			origbboxIdx = 0
			idxPerVert = 0.0

		return vertIdx, origbboxIdx, idxPerVert

	def getCtrlVertices(self, copy=False):
		return []