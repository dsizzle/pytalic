import character
import random
import pickle

class character_set(object):
	def __init__(self):
		self.__characters = {}
		self.__currentChar = None
		self.__savedStrokes = []

	def newCharacter(self, charCode):
		myChar = character.Character()
		self.__characters[charCode] = myChar
		self.__currentChar = charCode
		
	def deleteChar(self, charToDelete):
		try:
			self.__characters[charToDelete] = None
		except:
			print "ERROR: character to delete doesn't exist!"
	
	def getCurrentChar(self):
		if self.__currentChar is not None:
			return self.__characters[self.__currentChar]
		else:
			return None
			
	def getCurrentCharName(self):
		return unichr(self.__currentChar)
	
	def getCurrentCharIndex(self):
		return self.__currentChar
	
	def setCurrentChar(self, char):
		if (self.__characters.has_key(char)):
			self.__currentChar = char
		else:
			self.newCharacter(char)
	
	def getChar(self, char):
		if (self.__characters.has_key(char)):
			return self.__characters[char]
		else:
			return None
		
	def getCharList(self):
		return self.__characters
		
	def getSavedStrokes(self):
		return self.__savedStrokes

	def saveStroke(self, item):
		self.__savedStrokes.append(item)

	def getSavedStroke(self, idx):
		if len(self.__savedStrokes) > idx:
			return self.__savedStrokes[idx]
		else:
			return None
			
	def serialize(self, fileName=None):
		if not (fileName):
			return 1
	
		try:
			dataFileFd = open(fileName, 'w')
		except IOError:
			print "ERROR: Couldn't open %s for writing." % (fileName)
			return 1
		
		try:
			dataPickler = pickle.Pickler(dataFileFd)
			tmpBitmapList = {}
			
			# clear bitmaps because they don't pickle... :(
			for mychar in self.__characters.keys():
				tmpBitmapList[mychar] = self.__characters[mychar].getBitmap()
				self.__characters[mychar].setBitmap(None)
				
			dataPickler.dump(self.__characters)
			for mychar in self.__characters.keys():
				self.__characters[mychar].setBitmap(tmpBitmapList[mychar])
			
		except pickle.PicklingError:
			print "ERROR: Couldn't serialize data"
			return 1
		
		if dataFileFd:
			dataFileFd.close()
			
		return 0
		
	def unserialize(self, fileName=None):
		if not (fileName):
			return 1
			
		try:
			dataFileFd = open(fileName, 'r')
		except IOError:
			print "ERROR: Couldn't open %s for reading." % (fileName)
			return 1
		
		try:
			dataPickler = pickle.Unpickler(dataFileFd)
		
			self.__characters = dataPickler.load()
		except:
			print "ERROR: Couldn't unserialize data"
			return 1
				
		if dataFileFd:
			dataFileFd.close()
					
		return 0
