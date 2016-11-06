import nibs_qt
from PyQt4 import QtCore, QtGui

class strokeInstance(object):
	def __init__(self):
		self.__stroke = None
		self.__x = 0
		self.__y = 0
		self.__instNib = None
		self.__color = QtGui.QColor(128, 128, 192, 90)

	def setPos(self, x, y):
		self.__x = x
		self.__y = y
	
	def getPos(self):
		return (int(self.__x), int(self.__y))

	def setStroke(self, stroke):
		self.__stroke = stroke
		self.__nib = nibs_qt.Nib()
		tmpNib = stroke.getNib()
		
		(self.__x, self.__y) = stroke.getPos()

		if tmpNib:
			self.__nib.fromNib(tmpNib)
			self.__nib.setColor(self.__color)
			

	def getStroke(self):
		return self.__stroke

	def draw(self, gc, showCtrlVerts=0, nib=None, selectedVert=-1):

		if self.__stroke == None:
			return

		if nib is not None:
			self.__nib = nibs_qt.Nib()
			self.__nib.fromNib(nib)
			self.__nib.setColor(self.__color)

		(stroke_x, stroke_y) = self.__stroke.getPos()		
		gc.save()

		gc.translate(-stroke_x, -stroke_y)
		gc.translate(self.__x, self.__y)

		self.__stroke.draw(gc, 0, self.__nib, selectedVert)

		gc.restore()

	def getBitmap(self):
		return self.__stroke.getBitmap()

	def getHitPoint(self, idx):
		return self.__stroke.getHitPoint(idx)

	def getBoundRect(self):
		return self.__stroke.getBoundRect()

	def insideStroke(self, pt):
		pos = self.__stroke.getPos()
		delta = [pos[0]-self.__x, pos[1]-self.__y]

		normPt = [pt[0]+delta[0], pt[1]+delta[1]] #-self.__x, pt[1]-self.__y]
		(vertIdx, origbboxIdx, idxPerVert) = self.__stroke.insideStroke(normPt)

		return vertIdx, origbboxIdx, idxPerVert

	def getCtrlVertices(self, copy=False):
		return []