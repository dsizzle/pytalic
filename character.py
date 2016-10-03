import stroke_qt
import thirdparty.dp

import random
import math
import copy

CURVE_RESOLUTION = 10

class Character(object):
	def __init__(self):
		self.__strokes = []
		self.__defCv = [[1,1],[1, 50],[1, 50],[1, 100]]
		self.__defNumPts = len(self.__defCv) * CURVE_RESOLUTION
		self.__nib = None
		self.__bitmapPreview = None
		
	def newStroke(self, pts, add=True):
		myStroke = stroke_qt.Stroke()
		
		tempCv = []
		
		startX, startY = pts[0]
		numPts = len(pts)
		
		if (2 > numPts):
			return
		if (2 == numPts):
			dX = (pts[1][0]-pts[0][0])/3.
			dY = (pts[1][1]-pts[0][1])/3.
			cp1 = [pts[0][0]+dX, pts[0][1]+dY]
			cp2 = [pts[1][0]-dX, pts[1][1]-dY]
			pts = [pts[0], cp1, cp2, pts[1]]
		elif (3 == numPts):
			dX = (pts[2][0]-pts[1][0])/4.
			dY = (pts[2][1]-pts[1][1])/4.
			
			pts = [pts[0], [pts[1][0]-dX, pts[1][1]-dY], [pts[1][0]+dX, pts[1][1]+dY], pts[2]]
		else:
			firstPts = [pts[0], pts[1]]
			lastPts = [pts[-2], pts[-1]]
			midPts = []
			
			for i in range(2, numPts-2):
				dxT = (pts[i+1][0]-pts[i-1][0])/2.
				dyT = (pts[i+1][1]-pts[i-1][1])/2.
				
				dxA = (pts[i-1][0]-pts[i][0])
				dyA = (pts[i-1][1]-pts[i][1])
				vLenA = math.sqrt(float(dxA)*float(dxA) + float(dyA)*float(dyA))
				dxB = (pts[i+1][0]-pts[i][0])
				dyB = (pts[i+1][1]-pts[i][1])
				vLenB = math.sqrt(float(dxB)*float(dxB) + float(dyB)*float(dyB))
				
				if (vLenA > vLenB):
					ratio = (vLenA / vLenB) / 2.
					midPts.append([pts[i][0]-dxT*ratio, pts[i][1]-dyT*ratio])
					midPts.append(pts[i])
					midPts.append([pts[i][0]+(dxT/2.), pts[i][1]+(dyT/2.)])
				else:
					ratio = (vLenB / vLenA) / 2.
					midPts.append([pts[i][0]-(dxT/2.), pts[i][1]-(dyT/2.)])
					midPts.append(pts[i])
					midPts.append([pts[i][0]+dxT*ratio, pts[i][1]+dyT*ratio])
			
			pts = firstPts
			pts.extend(midPts)
			pts.extend(lastPts)
						
		for pt in pts:
			tempCv.append([pt[0]-startX+1, pt[1]-startY+1])
		
		myStroke.setCtrlVerticesFromList(tempCv)
		myStroke.setNumCurvePoints(len(tempCv * CURVE_RESOLUTION))
		myStroke.setPos(startX, startY)
		
		myStroke.calcCurvePoints()
		if (2 == numPts):
			myStroke.straighten()
	
		if add:
			self.__strokes.append(myStroke)

		return myStroke
		
	def newFreehandStroke(self, pts):
		myStroke = stroke_qt.Stroke()
		rawCv = []
		tempCv = []
		
		newPts = thirdparty.dp.simplify_points(pts, 10)
		startX, startY = newPts[0]
		numPts = len(newPts)
		while ((numPts % 4) != 0):
			newPts.append(newPts[-1])
			numPts = numPts + 1
			
		rawCv = myStroke.calcCtrlVertices(newPts)
		for pt in rawCv:
			tempCv.append([pt[0]-startX+1, pt[1]-startY+1])
		
		myStroke.setCtrlVerticesFromList(tempCv)
		myStroke.setNumCurvePoints(len(tempCv * CURVE_RESOLUTION))
		myStroke.setPos(startX, startY)

		myStroke.calcCurvePoints()
		if (2 == numPts):
			myStroke.straighten()

		self.__strokes.append(myStroke)

		return myStroke
		
	def addStroke (self, strokeToAdd):
		newStroke = self.copyStroke(strokeToAdd)
		self.__strokes.append(newStroke)
		return newStroke
		
	def copyStroke(self, strokeToCopy):
		copiedStroke = stroke_qt.Stroke(fromStroke=strokeToCopy)
		
		return copiedStroke
		
	def deleteStroke(self, strokeToDelete):
		try:
			self.__strokes.remove(strokeToDelete)
		except:
			print "ERROR: stroke to delete doesn't exist!"
	
	def joinStrokes(self, args):
		strokesToJoin = copy.copy(args['strokesToJoin'])
		
		firstStroke = strokesToJoin.pop(0)
		initStroke = self.copyStroke(firstStroke)
		
		while (len(strokesToJoin)):
			
			ptToUse = 0
			curStroke = strokesToJoin.pop(0)
			
			newCtrlPts = initStroke.getCtrlVerticesAsList()
			tempCtrlPts = curStroke.getCtrlVerticesAsList()
			
			(sx,sy) = newCtrlPts[0]
			(ex,ey) = newCtrlPts[-1]
			
			(ix,iy) = initStroke.getPos()
			(cx,cy) = curStroke.getPos()
			
			(csx,csy) = tempCtrlPts[0]
			(cex,cey) = tempCtrlPts[-1]
			sx += ix
			sy += iy
			ex += ix
			ey += iy
			
			csx += cx
			csy += cy
			cex += cx
			cey += cy
			
			dss = self.distBetweenPts(sx,sy,csx,csy)
			dse = self.distBetweenPts(sx,sy,cex,cey)
			des = self.distBetweenPts(ex,ey,csx,csy)
			dee = self.distBetweenPts(ex,ey,cex,cey)
			
			smallest = dss
			if (dse < smallest):
				smallest = dse
				ptToUse = 1
			if (des < smallest):
				smallest = des
				ptToUse = 2
			if (dee < smallest):
				smallest = dee
				ptToUse = 3
			
			if (ptToUse == 0):
				newCtrlPts.reverse()
			elif (ptToUse == 1):
				newCtrlPts.reverse()
				tempCtrlPts.reverse()
			elif (ptToUse == 3):
				tempCtrlPts.reverse()
			
			tempCtrlPts.pop(0)
			for i in range(0, len(tempCtrlPts)):
				tempCtrlPts[i][0] += cx-ix
				tempCtrlPts[i][1] += cy-iy
				
			newCtrlPts.extend(tempCtrlPts)			
			numPts = curStroke.getNumCurvePoints()+initStroke.getNumCurvePoints()
			initStroke.setCtrlVerticesFromList(newCtrlPts)
			initStroke.setNumCurvePoints(numPts)
			
		
		initStroke.updateCtrlVertices()
		initStroke.calcCurvePoints()
		
		for stroke in args['strokesToJoin']:
			self.deleteStroke(stroke)
		
		self.__strokes.append(initStroke)		
		
		return initStroke
		
	def unjoinStrokes (self, args): 
		joinedStroke = args['joinedStroke']
		strokesToUnjoin = args['strokesToUnjoin']
	
		for stroke in strokesToUnjoin:
			self.__strokes.append(stroke)
		
		self.deleteStroke(joinedStroke)
	
	def rejoinStrokes (self, args): 
		joinedStroke = args['joinedStroke']
		strokesToJoin = args['strokesToJoin']

		for stroke in strokesToJoin:
			self.deleteStroke(stroke)
			
		self.__strokes.append(joinedStroke)
	
		
	def distBetweenPts (self, x,y,x1,y1):
		return math.sqrt((x-x1)*(x-x1)+(y-y1)*(y-y1))
	
	@property
	def strokes(self):
		return self.__strokes
			
	def getBitmap(self):
		return self.__bitmapPreview
	
	def setBitmap(self, bmap):
		self.__bitmapPreview = bmap
		
	def delBitmap(self):
		del self.__bitmapPreview
	
	bitmapPreview = property(getBitmap, setBitmap, delBitmap, "bitmapPreview property")	
	
	def draw(self, showCtrlVerts=0, drawHandles=0, nib=None):
		
		for stroke in self.__strokes:
			stroke.draw(showCtrlVerts, drawHandles, nib)
