from datetime import *

import math

from PyQt4 import QtCore, QtGui, QtSvg, Qt

import guides_qt
import character_set
import nibs_qt
import stroke_qt

class mainDrawingArea(QtGui.QFrame):
	def __init__(self, parent): 
		QtGui.QWidget.__init__(self, parent)
		self.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.setMouseTracking(True)
		
		self.__drawGuidelines = True
		self.__drawNibGuides = True
		self.__charData = None
		self.__selection = [] #None
		self.__dragging = 0
		self.__draggingCtrlPt = 0
		self.__addCtrlPoint = 0
		self.__selectedPt = None
		self.__oldXpos = None
		self.__oldYpos = None
		self.__newStroke = 0
		self.__newFreehandStroke = 0
		self.__curXpos = None
		self.__curYpos = None
		self.__beforeMoveXpos = 0
		self.__beforeMoveYpos = 0
		self.__newStrokePts = []
		self.__mouseX = -1
		self.__mouseY = -1
		self.__bgColor = QtGui.QColor(240, 240, 230)
		self.__altbgColor = QtGui.QColor(230, 230, 220)
		self.__bgBrush = QtGui.QBrush(self.__bgColor, QtCore.Qt.SolidPattern) 
		self.__instanceBgBrush = QtGui.QBrush(self.__altbgColor, QtCore.Qt.SolidPattern)
		self.__bgPen = QtGui.QPen(self.__bgColor, 1, QtCore.Qt.SolidLine) #wx.SOLID
		self.__grayPen = QtGui.QPen(QtGui.QColor(200, 200, 200), 1, QtCore.Qt.SolidLine) 
		self.__dkGrayPenDashed = QtGui.QPen(QtGui.QColor(100, 100, 100), 2, QtCore.Qt.DashLine)
		self.__clearBrush = QtGui.QBrush(QtGui.QColor(0,0,0), QtCore.Qt.NoBrush)
		
		self.__nib = None
		self.__instNib = nibs_qt.Nib()

		self.__snapAxially = True
		self.__snapToNibAxes = False
		self.__snapToGrid = False
		self.__snapToCtrlPts = False
		self.__snapToStrokes = False
		self.__snapTolerance = 10
		self.__slopeTolerancePosA = 0
		self.__slopeToleranceNegA = 0
		self.__slopeTolerancePosB = 0
		self.__slopeToleranceNegB = 0
		self.__snappedNibPts = None
		self.__snappedAxisPts = None
		self.__snappedGridPts = None
		self.__snappedCtrlPts = None
		self.__snappedStrokePts = None

		self.__guideLines = guides_qt.guideLines()
		self.__guideLines.angle
		
		self.__undoStack = None
		self.__redoStack = None
		self.__clipBoard = None

		self.__last_time = None
		self.__now_time = None
		self.__instanceEditMode = False

	def setUndoStack(self, undoStack):
		self.__undoStack = undoStack
		
	def setRedoStack(self, redoStack):
		self.__redoStack = redoStack
	
	def setBgColor(self, bgcolor):
		self.__bgColor = bgcolor
		self.__bgBrush = QtGui.QBrush(self.__bgColor, QtCore.Qt.SolidPattern) 
		self.__bgPen = QtGui.QPen(self.__bgColor, 1, QtCore.Qt.SolidLine) #wx.SOLID
		
	def getBgColor(self):
		return self.__bgColor
		
	def setNib(self, nib):
		self.__nib = nib
			
		self.__slopeB = abs(math.tan(math.radians(self.__nib.getAngle())))
		if self.__slopeB:
			self.__slopeA = abs(1.0 / float(0 - self.__slopeB))
		else:
			self.__slopeA = 0
		
	def getNib(self):
		return self.__nib
	
	def getGuideLines(self):
		return self.__guideLines
		
	def setGuideAngle(self, angle):
		self.__guideLines.angle = angle
		
	def getGuideAngle(self):
		return self.__guideLines.angle
				
	def setCharData(self, charDataPtr):
		self.__charData = charDataPtr
	
	def getSelectedStrokes(self):
		return self.__selection
	
	def getSelectedCtrlPoint(self):
		if self.__selectedPt == None or self.__selectedPt < 0:
			return None
		else:
			selStroke = self.__selection[0]
			selPt = selStroke.getCtrlVertex(self.__selectedPt)
			
			return selPt

	def setSelectedStrokes(self, strokes):
		self.__selection = strokes
		self.__selectedPt = None
		self.repaint()
	
	def toggleGuidelines(self):
		self.__drawGuidelines = not self.__drawGuidelines
	
	def toggleNibGuides(self):
		self.__drawNibGuides = not self.__drawNibGuides
		
	def toggleSnapAxially(self):
		self.__snapAxially = not self.__snapAxially
	
	def toggleSnapToNibAxes(self):
		self.__snapToNibAxes = not self.__snapToNibAxes
	
	def toggleSnapToGrid(self):
		self.__snapToGrid = not self.__snapToGrid

	def toggleSnapToCtrlPts(self):
		self.__snapToCtrlPts = not self.__snapToCtrlPts

	def toggleSnapToStrokes(self):
		self.__snapToStrokes = not self.__snapToStrokes

	def setInstanceEditMode(self, onoff):
		self.__instanceEditMode = onoff

	def newStroke(self):
		self.__newFreehandStroke = 0
		self.__newStroke = 1
		self.__newStrokePts = []
		self.__addCtrlPoint = 0
	
	def newFreehandStroke(self):
		self.__newFreehandStroke = 1
		self.__newStroke = 1
		self.__newStrokePts = []
		self.__addCtrlPoint = 0
	
	def resizeEvent(self, event):
		self.__guideLines.calculateGridPts(self.size())
		self.repaint()
	
	def addControlPoint(self):
		self.__addCtrlPoint = 1
		self.__newFreehandStroke = 0
		self.__newStroke = 0
		self.__newStrokePts = []
	 	
	def keyReleaseEvent(self, event):
		oldSel = self.__selection
		key = event.key()
		#print key
		
		if (key == QtCore.Qt.Key_Delete) or \
		   (key == QtCore.Qt.Key_Backspace):
			if (self.__selection):
				if (self.__selectedPt >= 0):
					doArgs = {}
					doArgs['strokes'] = self.__selection[:]
					doArgs['selPt'] = self.__selectedPt

					undoArgs = {}
					undoArgs['strokes'] = self.__selection[:]
					undoArgs['selPt'] = self.__selectedPt
					undoArgs['ctrlPts'] = self.__selection[0].getCtrlVertices() 
							
					if (len(undoArgs['ctrlPts']) > 2):
						command = {
							'undo': self.resetCtrlPointsForSelected, 'undoArgs': undoArgs,
							'do' : self.deleteCtrlPointFromSelected, 'doArgs': doArgs
						}
						
						selStroke = self.__selection[0]
						selStroke.deleteCtrlVertex(self.__selectedPt)
						
						self.__selectedPt = None
					else:
						command = {
							'undo': self.addStrokes, 'undoArgs': undoArgs, 
							'do': self.deleteStrokes, 'doArgs': doArgs
						}
					
						for stroke in self.__selection:
							self.__charData.deleteStroke(stroke)

						self.__selection = []
										
					self.__undoStack.append(command)
					self.__redoStack[:] = []
					
				else:
					if self.__instanceEditMode:
						QtGui.QWidget.keyReleaseEvent(self, event)
						return

					doArgs = {}
					doArgs['strokes'] = self.__selection[:]
					undoArgs = {}
					undoArgs['strokes'] = self.__selection[:]
					for stroke in self.__selection:
						if isinstance(stroke, stroke_qt.Stroke):
							for inst in stroke.getInstances():
								doArgs['strokes'].append(inst)
								undoArgs['strokes'].append(inst)

					
					command = {
							'undo': self.addStrokes, 'undoArgs': undoArgs, 
							'do': self.deleteStrokes, 'doArgs': doArgs
							}

					self.__undoStack.append(command)
					self.__redoStack[:] = []
				
					self.deleteStrokes(doArgs)

					self.__selection = []
				
				self.repaint()
			else:
				QtGui.QWidget.keyReleaseEvent(self, event)

	def deleteStrokes(self, args):
		if (args.has_key('strokes')):
			strokes = args['strokes']
			
			for stroke in strokes:
				char = stroke.getParent()
				char.deleteStroke(stroke)
				if (stroke in self.__selection):
					self.__selection.remove(stroke)
					
			self.repaint()

	def addStrokes(self, args):
		if (args.has_key('strokes')):
			strokes = args['strokes']
			
			for stroke in strokes:
				char = stroke.getParent()
				strokeList = char.strokes
				strokeList.append(stroke)
			
			self.repaint()
			#self.__selection = [strokes]
	
	def resetCtrlPointsForSelected(self, args):
		if (args.has_key('strokes')):
			selStroke = args['strokes'][0]
			
			if (args.has_key('ctrlPts')):
				selStroke.setCtrlVertices(args['ctrlPts'])
				
				self.__selection = args['strokes']
				
				if (args.has_key('selPt')):
					self.__selectedPt = args['selPt']
				
				self.repaint()
	
	def deleteCtrlPointFromSelected(self, args):
		if (args.has_key('strokes')):
			self.__selection = args['strokes']
			selStroke = args['strokes'][0]
			
			if (args.has_key('selPt')):
				selPt = args['selPt']
				selStroke.deleteCtrlVertex(selPt)
				self.__selectedPt = None
				
				self.repaint()
			
	def mouseMoveEvent(self, event):
		pt = event.pos()
		self.__normalizeMouseCoords__(pt)
		tmpX = self.__oldXpos
		tmpY = self.__oldYpos
		if (self.__newStroke > 0):
			if (self.__newFreehandStroke > 1):
				xpos = pt.x()
				ypos = pt.y()

				self.__now_time = datetime.now()
				if self.__last_time is None or self.__now_time - self.__last_time > timedelta(milliseconds=20):
					self.__newStrokePts.append([xpos, ypos])
					self.__last_time = self.__now_time
					self.repaint()

				self.__oldXpos = xpos
				self.__oldYpos = ypos
			else:
				self.repaint()

			self.__mouseX = pt.x()
			self.__mouseY = pt.y()
			
			
		else:
			self.__mouseX = -1
			self.__mouseY = -1
		
		if self.__dragging or self.__draggingCtrlPt:
			self.__snappedNibPts = None
			self.__snappedAxisPts = None
			self.__snappedGridPts = None
			self.__snappedCtrlPts = None

			if self.__snapAxially:
				self.snapPointAxially(pt)
			if self.__snapToNibAxes: # and (self.__snappedAxisPts is None):	
				self.snapPointToNibAxes(pt)
			if self.__snapToGrid:
				pt = event.pos()
				self.snapPointToGrid(pt)
				self.__normalizeMouseCoords__(pt)
			if self.__snapToCtrlPts:
				self.snapPointToCtrlPts(pt)
			if self.__snapToStrokes:
				self.snapPointToStroke(pt)

			self.onDrag(pt.x(), pt.y())
	
	def mousePressEvent(self, event):
		btn = event.button()
		if (btn == QtCore.Qt.LeftButton):
			self.onLButtonDown(event)

	def mouseReleaseEvent(self, event):
		btn = event.button()
		if (btn == QtCore.Qt.LeftButton):
			self.onLButtonUp(event)
		elif (btn == QtCore.Qt.RightButton):
			self.onRButtonUp(event)
			
	def onDrag(self, xpos, ypos):
		if self.__dragging:
			if (self.__selection):
				if self.__oldXpos and self.__oldYpos:
					dx = xpos - (self.__oldXpos)
					dy = ypos - (self.__oldYpos)
				else:
					dx = 0
					dy = 0
					
				for stroke in self.__selection:
					pos = stroke.getPos()
					
					stroke.setPos(pos[0]+dx, pos[1]+dy)
				
				self.__oldXpos = xpos
				self.__oldYpos = ypos
				
				self.repaint()
							
		elif self.__draggingCtrlPt:
			
			if (self.__selection):
				
				if (self.__selectedPt >= 0):
					offset = self.__selection[0].getPos()
					ctrlPts = self.__selection[0].getCtrlVertices(False)
					
					vpos = ctrlPts[self.__selectedPt].getPosOfSelected()
					dx = xpos - (vpos[0]+offset[0])
					dy = ypos - (vpos[1]+offset[1])
					
					ctrlPts[self.__selectedPt].setPosOfSelected(vpos[0]+dx, vpos[1]+dy)
							
					self.__selection[0].updateCtrlVertices()
					self.__selection[0].calcCurvePoints()
					self.repaint()
		
	def __normalizeMouseCoords__(self, pt):
		winSize = self.size()
		xleft = 0
		ytop = 0
		xright = xleft+winSize.width()
		ybottom = ytop+winSize.height()
		
		xpos = pt.x()
		ypos = pt.y()
		
		if xpos > xright:
			xpos = xright
		elif xpos < xleft:
			xpos = xleft
			
		if ypos > ybottom:
			ypos = ybottom
		elif ypos < ytop:
			ypos = ytop
		
		wdiv2 = winSize.width()/2
		hdiv2 = winSize.height()/2

		xpos = xpos - wdiv2
		ypos = ypos - hdiv2

		pt.setX(xpos)
		pt.setY(ypos)
	
	def snapPointToNibAxes(self, pt):
		self.__snappedNibPts = None
		
		if (self.__selectedPt >= 0):
			offset = self.__selection[0].getPos()
			ctrlPts = self.__selection[0].getCtrlVertices(False)
			
			if (self.__selectedPt == 0) and (ctrlPts[self.__selectedPt].isKnotSelected()):
				vpos = ctrlPts[self.__selectedPt+1].getPos()
			elif (ctrlPts[self.__selectedPt].isKnotSelected()):
				vpos = ctrlPts[self.__selectedPt-1].getPos()
			elif (ctrlPts[self.__selectedPt].isLeftHandleSelected()) or (ctrlPts[self.__selectedPt].isRightHandleSelected()):
				vpos = ctrlPts[self.__selectedPt].getPos()
			else:
				return
			
			normPt = [pt.x()-offset[0], pt.y()-offset[1]]
			
			dx = normPt[0]-vpos[0]
			dy = normPt[1]-vpos[1]
			
			vecLength = math.sqrt(float(dx)*float(dx) + float(dy)*float(dy))
			
			nibAng = self.__nib.getAngle()
			
			if (dx > 0 and dy > 0):
				nibAng = nibAng
			elif (dx > 0 and dy < 0):
				nibAng = 90 + nibAng
			elif (dx < 0 and dy < 0):
				nibAng = 180 + nibAng	
			else:
				nibAng = 270 + nibAng
				
			newx = vecLength * math.sin(math.radians(nibAng)) + offset[0] + vpos[0]
			newy = vecLength * math.cos(math.radians(nibAng)) + offset[1] + vpos[1]	
			
			newdy = pt.y() - newy
			newdx = pt.x() - newx
			
			if abs(newdy) < self.__snapTolerance or ((abs(newdx) < self.__snapTolerance) and (abs(newdy / 2) > self.__snapTolerance)):
				pt.setY(newy)
				pt.setX(newx)
				self.__snappedNibPts = [QtCore.QPoint(vpos[0]+offset[0], vpos[1]+offset[1]), pt]	
				
				
	def snapPointAxially(self, pt):
		self.__snappedAxisPts = None
		
		if (self.__selectedPt >= 0):
			offset = self.__selection[0].getPos()
			ctrlPts = self.__selection[0].getCtrlVertices(False)
			
			if (self.__selectedPt == 0) and (ctrlPts[self.__selectedPt].isKnotSelected()):
				vpos = ctrlPts[self.__selectedPt+1].getPos()
			elif (ctrlPts[self.__selectedPt].isKnotSelected()):
				vpos = ctrlPts[self.__selectedPt-1].getPos()
			elif (ctrlPts[self.__selectedPt].isLeftHandleSelected()) or (ctrlPts[self.__selectedPt].isRightHandleSelected()):
				vpos = ctrlPts[self.__selectedPt].getPos()
			else:
				return
				
			normPt = [pt.x()-offset[0], pt.y()-offset[1]]
			
			dx = normPt[0]-vpos[0]
			dy = normPt[1]-vpos[1]
				
			slope = 0.0
			slopeToUse = 0.0
			if abs(dy) < self.__snapTolerance:
				pt.setY(vpos[1]+offset[1])
				self.__snappedAxisPts = [QtCore.QPoint(vpos[0]+offset[0], vpos[1]+offset[1]), pt]
			else:
				vecLength = math.sqrt(float(dx)*float(dx) + float(dy)*float(dy))

				guideAng = 0 - self.__guideLines.angle

				if (guideAng > 0):
					dx = 0 - dx
					
				if (dx < 0 and dy > 0):
					guideAng = guideAng
				elif (dx > 0 and dy < 0):
					guideAng = 180 + guideAng
				else:
					return
					
				newx = vecLength * math.sin(math.radians(guideAng)) + offset[0] + vpos[0]
				newy = vecLength * math.cos(math.radians(guideAng)) + offset[1] + vpos[1]	
			
				newdy = pt.y() - newy
				newdx = pt.x() - newx

				if (abs(newdx) < self.__snapTolerance):
					pt.setY(newy)
					pt.setX(newx)
					self.__snappedAxisPts = [QtCore.QPoint(vpos[0]+offset[0], vpos[1]+offset[1]), pt]
				
	def snapPointToGrid(self, pt):
		self.__snappedGridPts = None
		winSize = self.size()
		wdiv2 = winSize.width()/2
		hdiv2 = winSize.height()/2

		if (self.__selectedPt >= 0):
			offset = self.__selection[0].getPos()
			gridPts = self.__guideLines.getGridPts()
			
			normPt = [pt.x(), pt.y()]
			for testPt in gridPts:
				dx = abs((normPt[0]-wdiv2) - testPt[0])
				dy = abs((normPt[1]-hdiv2) - testPt[1])

				if (dx < self.__snapTolerance) and (dy < self.__snapTolerance):
					pt.setX(testPt[0]+wdiv2)
					pt.setY(testPt[1]+hdiv2)
					self.__snappedGridPts = [QtCore.QPoint(testPt[0], testPt[1])]

					return
			
	def snapPointToCtrlPts(self, pt):
		self.__snappedCtrlPts = None
		winSize = self.size()
		wdiv2 = winSize.width()/2
		hdiv2 = winSize.height()/2

		if (self.__selectedPt >= 0):
			cur_offset = self.__selection[0].getPos()
			normPt = [pt.x(), pt.y()]
			
			if self.__charData:
				for stroke in self.__charData.strokes:
					selPt = self.getSelectedCtrlPoint()
					ctrlPts = stroke.getCtrlVertices(False)
					numPts = len(ctrlPts)
					offset = stroke.getPos()

					for i in range(0, numPts):
						# don't snap to self; that'd be awkward
						if selPt == ctrlPts[i]:
							continue

						pos = ctrlPts[i].getPos()

						dx = abs((pos[0]+offset[0])-normPt[0])
						dy = abs((pos[1]+offset[1])-normPt[1])

						if (dx < self.__snapTolerance) and (dy < self.__snapTolerance):
							pt.setX(pos[0]+offset[0])
							pt.setY(pos[1]+offset[1])

							self.__snappedCtrlPts = [QtCore.QPoint(pos[0]+offset[0], pos[1]+offset[1])]
							return
	
	def snapPointToStroke(self, pt):
		self.__snappedStrokePts = None

		if (self.__selectedPt >= 0):
			cur_offset = self.__selection[0].getPos()
			normPt = [pt.x(), pt.y()]
			
			if self.__charData:
				for stroke in self.__charData.strokes:
					if stroke == self.__selection[0]:
						continue
					
					offset = stroke.getPos()
					idx, bbox, junk = stroke.insideStroke(normPt)
					if idx > 0:
						hitPt = stroke.getHitPoint(bbox)
						
						pt.setX(hitPt[0]+offset[0])
						pt.setY(hitPt[1]+offset[1])

						self.__snappedStrokePts = [QtCore.QPoint(hitPt[0]+offset[0], hitPt[1]+offset[1])]
						return

	def setCtrlVertBehavior(self, args):
		if (args.has_key('stroke')):
			selStroke = args['stroke']
		
			if (args.has_key('selPt')):
				selPt = args['selPt']
			
				if (args.has_key('behavior')):
					behavior = args['behavior']
				
					selPt.setBehavior(behavior)	
					if (args.has_key('pts')):
						selPt.setPos(args['pts'][1][0],args['pts'][1][1])
						selPt.setLeftHandlePos(args['pts'][0][0], args['pts'][0][1])
						selPt.setRightHandlePos(args['pts'][2][0],args['pts'][2][1])
					
					selStroke.updateCtrlVertices()
					selStroke.calcCurvePoints()
					self.repaint()
					
	def alignTangentsSymmetrical(self):
		if self.__selectedPt == None:
			return
		else:
			selStroke = self.__selection[0]
			selPt = selStroke.getCtrlVertex(self.__selectedPt)
			
			undoArgs = {}
			undoArgs['stroke'] = selStroke
			undoArgs['selPt'] = selPt
			undoArgs['behavior'] = selPt.getBehavior()
			undoArgs['pts'] = [selPt.getLeftHandlePos(), selPt.getPos(), selPt.getRightHandlePos()]
			doArgs = {}
			selPt.setBehaviorToSymmetric()
			doArgs['stroke'] = selStroke
			doArgs['selPt'] = selPt
			doArgs['behavior'] = selPt.getBehavior()
			
			command = {
					'undo': self.setCtrlVertBehavior, 'undoArgs': undoArgs, 
					'do': self.setCtrlVertBehavior, 'doArgs': doArgs
					}

			self.__undoStack.append(command)
			self.__redoStack[:] = []
			
			selStroke.updateCtrlVertices()
			selStroke.calcCurvePoints()
			self.repaint()
					
	def alignTangents(self):
		if self.__selectedPt == None:
			return
		else:
			selStroke = self.__selection[0]
			selPt = selStroke.getCtrlVertex(self.__selectedPt)
			
			undoArgs = {}
			undoArgs['stroke'] = selStroke
			undoArgs['selPt'] = selPt
			undoArgs['behavior'] = selPt.getBehavior()
			undoArgs['pts'] = [selPt.getLeftHandlePos(), selPt.getPos(), selPt.getRightHandlePos()]
			doArgs = {}
			selPt.setBehaviorToSmooth()
			doArgs['stroke'] = selStroke
			doArgs['selPt'] = selPt
			doArgs['behavior'] = selPt.getBehavior()
			
			command = {
					'undo': self.setCtrlVertBehavior, 'undoArgs': undoArgs, 
					'do': self.setCtrlVertBehavior, 'doArgs': doArgs
					}

			self.__undoStack.append(command)
			self.__redoStack[:] = []
			
			selStroke.updateCtrlVertices()
			selStroke.calcCurvePoints()
			self.repaint()
				
	def breakTangents(self):
		if self.__selectedPt == None:
			return
		else:
			selStroke = self.__selection[0]
			selPt = selStroke.getCtrlVertex(self.__selectedPt)
			
			undoArgs = {}
			undoArgs['stroke'] = selStroke
			undoArgs['selPt'] = selPt
			undoArgs['behavior'] = selPt.getBehavior()
			undoArgs['pts'] = [selPt.getLeftHandlePos(), selPt.getPos(), selPt.getRightHandlePos()]
			doArgs = {}
			selPt.setBehaviorToSharp()
			doArgs['stroke'] = selStroke
			doArgs['selPt'] = selPt
			doArgs['behavior'] = selPt.getBehavior()
			
			command = {
					'undo': self.setCtrlVertBehavior, 'undoArgs': undoArgs, 
					'do': self.setCtrlVertBehavior, 'doArgs': doArgs
					}

			self.__undoStack.append(command)
			self.__redoStack[:] = []
			
			selStroke.updateCtrlVertices()
			selStroke.calcCurvePoints()
			self.repaint()
	
	def cutSelected(self):
		self.__newClipBoard = []
	
		for stroke in self.__selection:
			self.__newClipBoard.append(self.__charData.copyStroke(stroke))
			
		undoArgs = {}
		undoArgs['clipboard'] = self.__newClipBoard
		undoArgs['char'] = self.__charData
		doArgs = {}
		doArgs['clipboard'] = self.__newClipBoard
		doArgs['selection'] = self.__selection[:]
		doArgs['char'] = self.__charData

		command = {
				'undo': self.pasteClipboard, 'undoArgs': undoArgs,
				'do': self.cutClipboard, 'doArgs': doArgs
				}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		self.cutClipboard(doArgs)

		self.repaint()

	def cutClipboard(self, args):
		if (args.has_key('char')):
			self.__charData = args['char']

			if (args.has_key('selection')):
				for stroke in args['selection']:
					self.__charData.deleteStroke(stroke)

				if (args.has_key('clipboard')):
					self.__clipBoard = args['clipboard']

	def pasteClipboard(self, args):
		if (args.has_key('char')):
			self.__charData = args['char']

			if (args.has_key('clipboard')):
				newSel = []

				for stroke in args['clipboard']:
					if isinstance(stroke, stroke_qt.Stroke):
						newSel.append(self.__charData.addStroke(stroke))
					else:
						newSel.append(self.__charData.addStrokeInstance(stroke))

				self.setSelectedStrokes(newSel)
	
	def copyClipboard(self, args):
		if (args.has_key('char')):
			self.__charData = args['char']

			if (args.has_key('clipboard')):
				self.__clipBoard = args['clipboard']

	def copySelected(self):
		self.__newClipBoard = []
	
		for stroke in self.__selection:
			self.__newClipBoard.append(self.__charData.copyStroke(stroke))
			
		undoArgs = {}
		undoArgs['clipboard'] = self.__newClipBoard
		undoArgs['char'] = self.__charData
		doArgs = {}
		doArgs['clipboard'] = self.__newClipBoard
		doArgs['char'] = self.__charData

		command = {
				'undo': self.pasteClipboard, 'undoArgs': undoArgs,
				'do': self.copyClipboard, 'doArgs': doArgs
				}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		self.copyClipboard(doArgs)

		self.repaint()

	def pasteSelected(self):
		self.__newClipBoard = []
	
		undoArgs = {}
		undoArgs['clipboard'] = self.__clipBoard[:]
		undoArgs['selection'] = self.__selection[:]
		undoArgs['char'] = self.__charData
		doArgs = {}
		doArgs['clipboard'] = self.__clipBoard[:]
		doArgs['char'] = self.__charData

		command = {
				'undo': self.cutClipboard, 'undoArgs': undoArgs,
				'do': self.pasteClipboard, 'doArgs': doArgs
				}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		self.pasteClipboard(doArgs)

		self.repaint()

	def pasteSelectedAsInstances(self):
		selectList = []

		for stroke in self.__clipBoard:
			selectList.append(self.__charData.addStrokeInstance(stroke))
			
		self.setSelectedStrokes(selectList)
		
		self.repaint()

	def onLButtonDown(self, event):
		oldSel = self.__selection
		
		pt = event.pos()
		mod = event.modifiers()
		
		cmdDown = mod & QtCore.Qt.ControlModifier
		altDown = mod & QtCore.Qt.AltModifier
		shiftDown = mod & QtCore.Qt.ShiftModifier
			
		self.__normalizeMouseCoords__(pt)
		
		xpos = pt.x()
		ypos = pt.y()
		
		self.__draggingCtrlPt = None
		self.__selectedPt = -1
		self.__snappedNibPts = None
		self.__snappedAxisPts = None
		self.__snappedGridPts = None
		self.__snappedCtrlPts = None
		
		insideStrokes = []
		hit = 0
		
		if (self.__newStroke == 0):
			self.__dragging = 1
			self.__oldXpos = xpos
			self.__oldYpos = ypos
		else:
			# if we're making a new stroke, don't check for 
			# a hit on a stroke.
			return

		if self.__charData:
			strokeList = self.__charData.strokes
			
			self.__selectedPt = None
			for stroke in self.__selection:
				ctrlPts = stroke.getCtrlVertices(False)
				numPts = len(ctrlPts)
				offset = stroke.getPos()
				for i in range(0, numPts):
					hit = 0
					hit = ctrlPts[i].checkForHit(xpos, ypos, offset)
					if (hit):
						self.__draggingCtrlPt = 1
						self.__dragging = 0
						self.__selectedPt = i
						self.__selection = [stroke]
						
			if (not hit):	
				if self.__instanceEditMode:					
					insideStrokes.append(self.__selection[0])
				else:
					for stroke in strokeList:
						idx, bbox, junk = stroke.insideStroke([xpos, ypos])
						if idx > 0:
							insideStrokes.append(stroke)
						
					for stroke in insideStrokes:
						if (shiftDown):
							if not (stroke in self.__selection):
								self.__selection.append(stroke)
							else:
								self.__selection.remove(stroke)
						else:
							if not (stroke in oldSel): #self.__selection):
								self.__selection = [stroke]
								self.repaint()
								break
			
				## should we check these first so we don't deselect a selected 
				## while trying to click one of its points?
				self.__selectedPt = None
				for stroke in self.__selection:
					ctrlPts = stroke.getCtrlVertices(False)
					numPts = len(ctrlPts)
					offset = stroke.getPos()
					for i in range(0, numPts):
						hit = 0
						hit = ctrlPts[i].checkForHit(xpos, ypos, offset)
						if (hit):
							self.__draggingCtrlPt = 1
							self.__dragging = 0
							self.__selectedPt = i
							self.__selection = [stroke]
							
																
		if (len(insideStrokes) == 0) and (not self.__draggingCtrlPt):
			self.__beforeMoveXpos = 0
			self.__beforeMoveYpos = 0
			self.__selection = []
			self.__dragging = 0
			#self.__ctrlState = 0
		elif (len(insideStrokes) > 0) and (not self.__draggingCtrlPt):
			self.__beforeMoveXpos = xpos
			self.__beforeMoveYpos = ypos
			self.__dragging = 1
		elif self.__draggingCtrlPt:
			self.__beforeMoveXpos = xpos
			self.__beforeMoveYpos = ypos
				
		self.repaint()
		
	def onLButtonUp(self, event):
		oldSel = self.__selection
		
		pt = event.pos()
		self.__normalizeMouseCoords__(pt)
		
		xpos = pt.x()
		ypos = pt.y()
		
		if (self.__newStroke == 1):
			if (self.__newFreehandStroke == 1):
				self.__newFreehandStroke = 2
			elif (self.__newFreehandStroke == 0):
				self.__newStrokePts.append([xpos, ypos])
		
				self.__oldXpos = xpos
				self.__oldYpos = ypos	
		elif (self.__addCtrlPoint):
			for stroke in self.__selection:
				ptIdx, bbox, t = stroke.insideStroke([xpos, ypos])
				if (ptIdx):
					doArgs = {}
					doArgs['stroke'] = stroke
					doArgs['ptIdx'] = ptIdx
					doArgs['t'] = t
					undoArgs = {}
					undoArgs['pts'] = stroke.getCtrlVertices()
					undoArgs['stroke'] = stroke
					command = {
						'undo': self.resetCtrlVerticesForStroke, 'undoArgs': undoArgs,
						'do': self.addCtrlVertexForStroke, 'doArgs': doArgs
						}
						
					self.__undoStack.append(command)
					self.__redoStack[:] = []
					self.addCtrlVertexForStroke(doArgs)
					
					break
			self.__addCtrlPoint = 0
			self.__dragging = 0
			self.__draggingCtrlPt = 0	
		else:
			if (self.__dragging):
				doArgs = {}
				doArgs['strokes'] = self.__selection
				doArgs['delta'] = [xpos - self.__beforeMoveXpos, ypos - self.__beforeMoveYpos]
				undoArgs = {}
				undoArgs['strokes'] = self.__selection
				undoArgs['delta'] = [self.__beforeMoveXpos - xpos, self.__beforeMoveYpos - ypos]
				
				command = {
						'undo': self.moveStrokes, 'undoArgs': undoArgs, 
						'do': self.moveStrokes, 'doArgs': doArgs
						}

				self.__undoStack.append(command)
				self.__redoStack[:] = []
				
			elif (self.__draggingCtrlPt and self.__selectedPt):
				stroke = self.__selection[0]
				ctrlPts = stroke.getCtrlVertices()
				doArgs = {}
				doArgs['strokes'] = [stroke]
				doArgs['points'] = [self.__selectedPt]
				doArgs['handle'] = stroke.getCtrlVertex(self.__selectedPt).getSelectedHandle()
				doArgs['delta'] = [xpos - self.__beforeMoveXpos, ypos - self.__beforeMoveYpos]
				undoArgs = {}
				undoArgs['strokes'] = [stroke]
				undoArgs['points'] = [self.__selectedPt]
				undoArgs['handle'] = ctrlPts[self.__selectedPt].getSelectedHandle()
				undoArgs['delta'] = [self.__beforeMoveXpos - xpos, self.__beforeMoveYpos - ypos]
				
				command = {
						'undo': self.movePoints, 'undoArgs': undoArgs, 
						'do': self.movePoints, 'doArgs': doArgs
						}

				self.__undoStack.append(command)
				self.__redoStack[:] = []
				
			
			self.__dragging = 0
			self.__draggingCtrlPt = None
			self.__oldXpos = None
			self.__oldYpos = None
				
		self.repaint()
	
	def moveStrokes(self, args):
		if (args.has_key('strokes')):
			strokeList = args['strokes']
			
			if (args.has_key('delta')):
				strokeDelta = args['delta']
				dx = strokeDelta[0]
				dy = strokeDelta[1]
				
				for stroke in strokeList:
					pos = stroke.getPos()
					
					stroke.setPos(pos[0]+dx, pos[1]+dy)	
	
					self.repaint(QtCore.QRect(stroke.getBoundRect()))
				
	def movePoints(self, args):
		if (args.has_key('strokes')):
			strokeList = args['strokes']
			
			if (args.has_key('points')):
				selPts = args['points']
				
				if (args.has_key('delta')):
					strokeDelta = args['delta']
					dx = strokeDelta[0]
					dy = strokeDelta[1]
				
					for stroke in strokeList:
						ctrlPts = stroke.getCtrlVertices(False)
						
						for pt in selPts:
							ctrlVert = ctrlPts[pt]
							ctrlVert.selectHandle(args['handle'])
							curPos = ctrlVert.getPosOfSelected()
							if (curPos):
								ctrlVert.setPosOfSelected(curPos[0]+dx, curPos[1]+dy)
								
						stroke.updateCtrlVertices()
						stroke.calcCurvePoints()
						self.repaint(QtCore.QRect(stroke.getBoundRect()))
						
					self.__selection = strokeList
					self.__selectedPt = selPts[0]
					
					#self.Refresh()
	
	def addCtrlVertexForStroke(self, args):
		if (args.has_key('stroke')):
			stroke = args['stroke']
			
			if (args.has_key('ptIdx')):
				ptIdx = args['ptIdx']
				
				if (args.has_key('t')):
					t = args['t']
					
					stroke.addCtrlVertex(t, ptIdx)
					
	def resetCtrlVerticesForStroke(self, args):
		if (args.has_key('stroke')):
			stroke = args['stroke']
			
			if (args.has_key('pts')):
				pts = args['pts']
				stroke.setCtrlVertices(pts)
									
	def onRButtonUp(self, event):
		pt = event.pos()
		self.__normalizeMouseCoords__(pt)
		tempStroke = None
		
		xpos = pt.x()
		ypos = pt.y()
		
		if (self.__newStroke == 1):
			if (len(self.__newStrokePts)):
				if (self.__newFreehandStroke):
					tempStroke = self.__charData.newFreehandStroke(self.__newStrokePts)
				else:
					tempStroke = self.__charData.newStroke(self.__newStrokePts)
					
				self.__newStroke = 0
				self.__newFreehandStroke = 0
		
				if (tempStroke):
					#tempStroke.addEndSerif(5)
					#tempStroke.addStartSerif(10)
					self.__oldXpos = None
					self.__oldYpos = None
			
					self.__selection = [tempStroke]
			
					doArgs = {}
					doArgs = tempStroke
					undoArgs = {}
					undoArgs = tempStroke

					strokeList = self.__charData.strokes
					
					command = {
							'undo': self.__charData.deleteStroke, 'undoArgs': undoArgs, 
							'do': strokeList.append, 'doArgs': doArgs
							}

					self.__undoStack.append(command)
					self.__redoStack[:] = []
			
			self.repaint()
		
	def createIconFromCanvas(self, scale): #, win):
		tempGuidelines = 0
		tempNibGuides = 0
		
		if self.__drawGuidelines or self.__drawNibGuides:
			tempGuidelines = self.__drawGuidelines
			tempNibGuides = self.__drawNibGuides
			self.__drawGuidelines = 0
			self.__drawNibGuides = 0
			self.repaint()
		
		fullImg = QtGui.QPixmap.grabWidget(self, 0, 0, self.width(), self.height())
		if (fullImg) and (fullImg.width() > 0) and (fullImg.height() > 0):
			iconBitmap = fullImg.scaled(scale, scale, QtCore.Qt.KeepAspectRatioByExpanding, 1)
		else:
			iconBitmap = None
			
		if tempGuidelines or tempNibGuides:
			self.__drawGuidelines = tempGuidelines
			self.__drawNibGuides = tempNibGuides
			self.repaint()
		
		return iconBitmap			
	
	def drawGuides(self, gc, size, nib):
		baseY = self.__guideLines.getBaselineY() #(size.height >> 1) + (size.height >> 4)
		
		ascent = self.__guideLines.getAscent()
		descent = self.__guideLines.getDescent()
		base = self.__guideLines.getBaseHeight()
		
		nibWidth = nib.getWidth() << 1
		baseNibWidths = nibWidth * base
		ascNibWidths = nibWidth * ascent
		halfNibWidth = nibWidth >> 1
		
		if (self.__drawNibGuides):
			color = nib.getColor()
			nib.setColor(QtGui.QColor(200, 195, 180))
			nib.setAlpha(200)
			nib.vertNibWidthScale(gc, nibWidth+halfNibWidth, baseY-baseNibWidths+halfNibWidth, base)
			nib.vertNibWidthScale(gc, nibWidth+nibWidth+halfNibWidth, baseY-baseNibWidths-ascNibWidths+halfNibWidth, ascent)
			nib.vertNibWidthScale(gc, nibWidth+nibWidth+halfNibWidth, baseY+halfNibWidth, descent)
			nib.setColor(color)
			
			
		return
									
	def paintEvent(self, event):
		
		winPos = self.pos()
		winSize = self.size()
		xpos = winPos.x()
		ypos = winPos.y()
		w = winSize.width()
		h = winSize.height()
		ptRadius = 10
			
		dc = QtGui.QPainter(self)
		dc.setRenderHint(QtGui.QPainter.Antialiasing)
		bgBrush = self.__bgBrush
		if self.__instanceEditMode:
			bgBrush = self.__instanceBgBrush

		dc.setBackground(bgBrush)

		dc.eraseRect(QtCore.QRect(xpos, ypos, xpos+w, ypos+h))
	
		if (self.__drawGuidelines):
		 	self.__guideLines.draw(dc, winSize, self.__nib)
		if self.__drawNibGuides:
			self.drawGuides(dc, winSize, self.__nib)
		
		dc.save()
		dc.translate(w/2, h/2)
			
		if self.__charData:
			nibToUse = self.__nib
			if self.__instanceEditMode:
				nibToUse = self.__instNib
				nibToUse.setColor(QtGui.QColor(100,100,100))

			strokeList = self.__charData.strokes 
			for stroke in strokeList:
				if (stroke in self.__selection):
					stroke.draw(dc, 1, self.__nib, self.__selectedPt)
				else:
					stroke.draw(dc, 0, nibToUse)
				
		if (self.__newStroke > 0):
			dc.setPen(self.__grayPen)
			dc.setBrush(self.__clearBrush)
			if (self.__newFreehandStroke > 0):
				ptRadius = 5
			elif len(self.__newStrokePts) > 1:
				tmpStrokePts = self.__newStrokePts[:]
				tmpStroke = self.__charData.newStroke(tmpStrokePts, False)
				
				tmpStroke.draw(dc, 0, self.__nib)


			prevPt = None
			for pt in self.__newStrokePts:		
				dc.drawEllipse(QtCore.QPoint(pt[0], pt[1]), ptRadius, ptRadius)
				if prevPt:
					dc.drawLine(prevPt[0], prevPt[1], pt[0], pt[1])
				prevPt = pt
				
			dc.drawEllipse(QtCore.QPoint(self.__mouseX, self.__mouseY), ptRadius+ptRadius, ptRadius+ptRadius)		
			if prevPt:
				dc.drawLine(prevPt[0], prevPt[1], self.__mouseX, self.__mouseY)
				
		if (self.__snappedAxisPts) and (self.__draggingCtrlPt):
			dc.setPen(self.__dkGrayPenDashed)
			dc.setBrush(self.__clearBrush)
			
			pt1 = self.__snappedAxisPts[0]
			pt2 = self.__snappedAxisPts[1]
			dy = (pt1.y() - pt2.y()) 
			dx = (pt1.x() - pt2.x())
			vecLen = math.sqrt(dx * dx + dy * dy)
			
			if (not vecLen == 0):
				dx = dx * 50 / vecLen
				dy = dy * 50 / vecLen
			else:
				dx = 0
				dy = 0
			
			dc.drawLine(pt1.x(), pt1.y(), pt1.x() + dx, pt1.y() + dy)
			dc.drawLine(pt2.x(), pt2.y(), pt2.x() - dx, pt2.y() - dy)
		
		if (self.__snappedNibPts) and (self.__draggingCtrlPt):
			dc.setPen(self.__dkGrayPenDashed)
			dc.setBrush(self.__clearBrush)

			pt1 = self.__snappedNibPts[0]
			pt2 = self.__snappedNibPts[1]
			dy = (pt1.y() - pt2.y()) 
			dx = (pt1.x() - pt2.x())
			vecLen = math.sqrt(dx * dx + dy * dy)

			if (not vecLen == 0):
				dx = dx * 50 / vecLen
				dy = dy * 50 / vecLen
			else:
				dx = 0
				dy = 0

			dc.drawLine(pt1.x(), pt1.y(), pt1.x() + dx, pt1.y() + dy)
			dc.drawLine(pt2.x(), pt2.y(), pt2.x() - dx, pt2.y() - dy)
				
		if (self.__snappedGridPts) and (self.__draggingCtrlPt):
			dc.setPen(self.__dkGrayPenDashed)
			dc.setBrush(self.__clearBrush)
			
			dc.drawEllipse(self.__snappedGridPts[0], self.__snapTolerance*2, self.__snapTolerance*2)
			
		if (self.__snappedCtrlPts) and (self.__draggingCtrlPt):
			dc.setPen(self.__dkGrayPenDashed)
			dc.setBrush(self.__clearBrush)
			
			dc.drawEllipse(self.__snappedCtrlPts[0], self.__snapTolerance*2, self.__snapTolerance*2)
		
		if (self.__snappedStrokePts) and (self.__draggingCtrlPt):
			dc.setPen(self.__dkGrayPenDashed)
			dc.setBrush(self.__clearBrush)
			
			dc.drawEllipse(self.__snappedStrokePts[0], self.__snapTolerance*2, self.__snapTolerance*2)
		

		dc.restore()
		dc.end()
		QtGui.QFrame.paintEvent(self,event)
