#!/opt/local/bin/python 
#
#
import sys

from PyQt4 import QtGui, QtCore

import stroke_frame_qt

class pytalic_app(QtGui.QApplication):
	def __init__(self, args):
		QtGui.QApplication.__init__(self, args)
		QtGui.qApp = self
		
		
def main(args=None):
	myQtApp = pytalic_app(args)
	myQtFrame = stroke_frame_qt.stroke_frame_qt(1024, 768, "Character Set Editor")
	myQtFrame.show()
	myQtFrame.activateWindow()
	myQtFrame.raise_()
	
	return myQtApp.exec_()
	
main(sys.argv)



