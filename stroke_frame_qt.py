import os
import os.path
import sys
import pickle

import character_set
import stroke_edit_ui_qt
import nibs_qt
import stroke_qt

from PyQt4 import QtGui, QtCore, QtSvg

gICON_SIZE = 40
gICON_TEXT_SIZE = 30

class stroke_frame_qt(QtGui.QMainWindow):
	def __init__(self, w, h, label):
		QtGui.QMainWindow.__init__(self)
		
		self.resize(w, h)
		self.setWindowTitle(label)
	 	
		self.__label__ = label
		self.__clipBoard = []
		self.__undoStack = []
		self.__redoStack = []
		self.mainMenu = None
		self.charData = None
		self.fileOpenDlg = QtGui.QFileDialog() 
		self.fileSaveDlg = QtGui.QFileDialog() 
		self.colorPickerDlg = QtGui.QColorDialog()
		
		self.__color__ = QtGui.QColor(125, 25, 25)
		
		self.createUI()
		
		self.__fileName__ = None
		self.__dirName__ = os.getcwd()
		self.__mainNib__ = None 
			
		self.fileNew_cb()

	def createMenu(self):
		self.mainMenu = self.menuBar()
		self.toolBar = self.addToolBar("main") #QtGui.QToolBar(self)
		self.toolBar.resize(self.width(), gICON_SIZE+gICON_TEXT_SIZE)
		self.toolBar.setFloatable(False)
		self.toolBar.setMovable(False)
		self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
		
		fileMenu 	= self.mainMenu.addMenu('&File')
		editMenu 	= self.mainMenu.addMenu('&Edit')
		viewMenu	= self.mainMenu.addMenu('&View')
		
		strokeMenu 	= self.mainMenu.addMenu('Stro&ke')
		helpMenu 	= self.mainMenu.addMenu('&Help')

		fileNew = QtGui.QAction("&New", self)
		fileNew.setShortcut('Ctrl+N')
		fileNew.setStatusTip('Create a new character set')
		fileNew.triggered.connect(self.fileNew_cb)
		fileNew.setIcon(QtGui.QIcon("icons/script_add.png"))
		fileNew.setIconText("New")
		fileMenu.addAction(fileNew)
		self.toolBar.addAction(fileNew)
		
		fileOpen = QtGui.QAction("&Open", self)
		fileOpen.setShortcut('Ctrl+O')
		fileOpen.setStatusTip('Open a character set')
		fileOpen.setIcon(QtGui.QIcon("icons/script_go.png"))
		fileOpen.setIconText("Open")
		fileOpen.triggered.connect(self.fileOpen_cb)
		fileMenu.addAction(fileOpen)
		self.toolBar.addAction(fileOpen)
		fileMenu.addSeparator()
		
		fileSave = QtGui.QAction("&Save", self)
		fileSave.setShortcut('Ctrl+S')
		fileSave.setStatusTip('Save the character set')
		fileSave.setIcon(QtGui.QIcon("icons/script_save.png"))
		fileSave.triggered.connect(self.fileSave_cb)
		fileSave.setIconText("Save")
		fileMenu.addAction(fileSave)
		self.toolBar.addAction(fileSave)
		
		fileSaveAs = QtGui.QAction("&Save As...", self)
		fileSaveAs.setStatusTip('Save the character set with a new name')
		fileSaveAs.setIcon(QtGui.QIcon("icons/save_as.png"))
		fileSaveAs.setIconText("Save As...")
		fileSaveAs.triggered.connect(self.fileSaveAs_cb)
		fileMenu.addAction(fileSaveAs)
		self.toolBar.addAction(fileSaveAs)
		
		fileMenu.addSeparator()
		fileQuit = QtGui.QAction("Q&uit", self)
		fileQuit.setShortcut('Ctrl+Q')
		fileQuit.triggered.connect(self.quit_cb)
		fileMenu.addAction(fileQuit)

		self.toolBar.addSeparator()
		
		editUndo = QtGui.QAction("Undo", self)
		editUndo.setShortcut('Ctrl+Z')
		editUndo.setIcon(QtGui.QIcon("icons/arrow_undo.png"))
		editUndo.setIconText("Undo")
		editUndo.triggered.connect(self.undo_cb)
		editMenu.addAction(editUndo)
		self.toolBar.addAction(editUndo)
		
		editRedo = QtGui.QAction("Redo", self)
		editRedo.setShortcut('Ctrl+Shift+Z')
		editRedo.setIcon(QtGui.QIcon("icons/arrow_redo.png"))
		editRedo.setIconText("Redo")
		editRedo.triggered.connect(self.redo_cb)
		editMenu.addAction(editRedo)
		self.toolBar.addAction(editRedo)
		
		editMenu.addSeparator()
		self.toolBar.addSeparator()
		
		editCut = QtGui.QAction("Cut", self)
		editCut.setShortcut('Ctrl+X')
		editCut.setIcon(QtGui.QIcon("icons/cut.png"))
		editCut.setIconText("Cut")
		editCut.triggered.connect(self.cutStrokes_cb)
		editMenu.addAction(editCut)
		self.toolBar.addAction(editCut)
		
		editCopy = QtGui.QAction("Copy", self)
		editCopy.setShortcut('Ctrl+C')
		editCopy.setIcon(QtGui.QIcon("icons/page_white_copy.png"))
		editCopy.setIconText("Copy")
		editCopy.triggered.connect(self.copyStrokes_cb)
		editMenu.addAction(editCopy)
		self.toolBar.addAction(editCopy)
		
		editPaste = QtGui.QAction("Paste", self)
		editPaste.setShortcut('Ctrl+V')
		editPaste.setIcon(QtGui.QIcon("icons/page_white_paste.png"))
		editPaste.setIconText("Paste")
		editPaste.triggered.connect(self.pasteStrokes_cb)
		editMenu.addAction(editPaste)
		self.toolBar.addAction(editPaste)

		#editPasteInstance = QtGui.QAction("Paste Instance", self)
		#editPasteInstance.setShortcut('Ctrl+Shift+V')
		#editPasteInstance.setIcon(QtGui.QIcon("icons/page_white_paste.png"))
		#editPasteInstance.setIconText("Paste Instance")
		#editPasteInstance.triggered.connect(self.pasteStrokesAsInstances_cb)
		#editMenu.addAction(editPasteInstance)
		#self.toolBar.addAction(editPasteInstance)
		
		#editMenu.addSeparator()
		self.toolBar.addSeparator()
		
		# editGuidelinePrefs = QtGui.QAction("Guideline Preferences...", self)
		# editGuidelinePrefs.triggered.connect(self.guidelinePrefs_cb)
		# editMenu.addAction(editGuidelinePrefs)
			
		viewGuides = QtGui.QAction("Guidelines", self)
		viewGuides.setStatusTip('Toggle guidelines on/off')
		viewGuides.triggered.connect(self.viewToggleGuidelines_cb)
		viewGuides.setCheckable(True)
		viewGuides.setChecked(True)
		viewMenu.addAction(viewGuides)
		
		viewNibGuides = QtGui.QAction("Nib Guides", self)
		viewNibGuides.setStatusTip('Toggle nib guides on/off')
		viewNibGuides.triggered.connect(self.viewToggleNibGuides_cb)
		viewNibGuides.setCheckable(True)
		viewNibGuides.setChecked(True)
		viewMenu.addAction(viewNibGuides)
			
		viewMenu.addSeparator()
		
		viewSnapMenu = viewMenu.addMenu('&Snap')
	
		viewSnapToAxes = QtGui.QAction("To Axes", self)
		viewSnapToAxes.setStatusTip('Toggle snapping to axes')
		viewSnapToAxes.triggered.connect(self.viewToggleSnapAxially_cb)
		viewSnapToAxes.setCheckable(True)
		viewSnapToAxes.setChecked(True)
		viewSnapMenu.addAction(viewSnapToAxes)
		
		viewSnapToNibAxes = QtGui.QAction("To Nib Axes", self)
		viewSnapToNibAxes.setStatusTip('Toggle snapping to nib axes')
		viewSnapToNibAxes.triggered.connect(self.viewToggleSnapToNibAxes_cb)
		viewSnapToNibAxes.setCheckable(True)
		viewSnapToNibAxes.setChecked(False)
		viewSnapMenu.addAction(viewSnapToNibAxes)
		
		viewSnapToGrid = QtGui.QAction("To Grid", self)
		viewSnapToGrid.setStatusTip('Toggle snapping to grid')
		viewSnapToGrid.triggered.connect(self.viewToggleSnapToGrid_cb)
		viewSnapToGrid.setCheckable(True)
		viewSnapToGrid.setChecked(False)
		viewSnapMenu.addAction(viewSnapToGrid)
		
		viewSnapToCtrlPts = QtGui.QAction("To Control Points", self)
		viewSnapToCtrlPts.setStatusTip('Toggle snapping to control points')
		viewSnapToCtrlPts.triggered.connect(self.viewToggleSnapToCtrlPts_cb)
		viewSnapToCtrlPts.setCheckable(True)
		viewSnapToCtrlPts.setChecked(False)
		viewSnapMenu.addAction(viewSnapToCtrlPts)
		
		viewSnapToStroke = QtGui.QAction("To Strokes", self)
		viewSnapToStroke.setStatusTip('Toggle snapping to strokes')
		viewSnapToStroke.triggered.connect(self.viewToggleSnapToStroke_cb)
		viewSnapToStroke.setCheckable(True)
		viewSnapToStroke.setChecked(False)
		viewSnapMenu.addAction(viewSnapToStroke)
		
		strokeNew = QtGui.QAction("New", self)
		strokeNew.setStatusTip('Create a new stroke')
		strokeNew.setIcon(QtGui.QIcon("icons/draw_path.png"))
		strokeNew.setIconText("Stroke")
		strokeNew.triggered.connect(self.createNewStroke_cb)
		strokeMenu.addAction(strokeNew)
		self.toolBar.addAction(strokeNew)
		
		strokeNewFreehand = QtGui.QAction("New Experimental", self)
		strokeNewFreehand.setStatusTip('Create a new stroke freehand')
		strokeNewFreehand.setIcon(QtGui.QIcon("icons/draw_calligraphic.png"))
		strokeNewFreehand.setIconText("Freehand")
		strokeNewFreehand.triggered.connect(self.createNewFreehandStroke_cb)
		strokeMenu.addAction(strokeNewFreehand)
		self.toolBar.addAction(strokeNewFreehand)
		
		strokeStraighten = QtGui.QAction("Straighten", self)
		strokeStraighten.setStatusTip('Make the stroke straight')
		strokeStraighten.triggered.connect(self.straightenStroke_cb)
		strokeMenu.addAction(strokeStraighten)
		
		strokeJoin = QtGui.QAction("Join", self)
		strokeJoin.setStatusTip('Join multiple strokes into one')
		strokeJoin.triggered.connect(self.joinStrokes_cb)
		strokeMenu.addAction(strokeJoin)
		
		strokeMenu.addSeparator()
		strokeAlignTangents = QtGui.QAction("Set Tangent To Symmetric", self)
		strokeAlignTangents.triggered.connect(self.alignTangentsSymmetrical_cb)
		strokeMenu.addAction(strokeAlignTangents)
		
		strokeSmoothTangents = QtGui.QAction("Set Tangent To Smooth", self)
		strokeSmoothTangents.triggered.connect(self.alignTangents_cb)
		strokeMenu.addAction(strokeSmoothTangents)
		
		strokeSharpenTangents = QtGui.QAction("Set Tangent To Sharp", self)
		strokeSharpenTangents.triggered.connect(self.breakTangents_cb)
		strokeMenu.addAction(strokeSharpenTangents)
		strokeMenu.addSeparator()
		
		strokeAddVertex = QtGui.QAction("Add Control Point", self)
		strokeAddVertex.triggered.connect(self.addControlPoint_cb)
		strokeMenu.addAction(strokeAddVertex)
	
		strokeMenu.addSeparator()
		strokeSave = QtGui.QAction("Save Stroke", self)
		strokeSave.triggered.connect(self.saveStroke_cb)
		strokeMenu.addAction(strokeSave)

		strokeLoad = QtGui.QAction("Paste From Saved", self)
		strokeLoad.triggered.connect(self.pasteInstanceFromSaved_cb)
		strokeMenu.addAction(strokeLoad)

		strokeSavedEdit = QtGui.QAction("Edit Saved", self)
		strokeSavedEdit.triggered.connect(self.editSaved_cb)
		strokeMenu.addAction(strokeSavedEdit)

		strokeSavedEditDone = QtGui.QAction("Done Editing Saved", self)
		strokeSavedEditDone.setShortcut('Esc')
		strokeSavedEditDone.triggered.connect(self.editSavedDone_cb)
		strokeMenu.addAction(strokeSavedEditDone)
		#strokeLoadInst = QtGui.QAction("Paste Instance From Saved", self)
		#strokeLoadInst.triggered.connect(self.pasteInstanceFromSaved_cb)
		#strokeMenu.addAction(strokeLoadInst)

		helpAbout = QtGui.QAction("About", self)
		helpAbout.triggered.connect(self.about_cb)
		helpMenu.addAction(helpAbout)
			
	def createUI(self):
		
	 	menuHeight = 25
		self.createMenu()
			
		wid80 = int(self.width()*.75)
		wid20 = self.width() - wid80
		hgt = self.height() 
		
		charList = []
		for i in range(32, 128):
			charList.append(str(unichr(i)))
			
		self.uberMainLayout = QtGui.QVBoxLayout() #self.uberMainFrame)
		
		self.charSelectorLayout = QtGui.QHBoxLayout() #self.charSelectorPane)
		self.charSelectorLayout.setMargin(0)
		self.charSelectorLayout.setSpacing(0)
		self.charSelectorLayout.setContentsMargins(0, 0, 0, 0)

		self.charSelectorList = QtGui.QListWidget(self)
		self.charSelectorList.setFlow(QtGui.QListView.LeftToRight)
		self.charSelectorList.resize(self.width(), gICON_SIZE*2)
		self.charSelectorList.setMaximumHeight(gICON_SIZE*2)
		self.charSelectorList.addItems(QtCore.QStringList(charList))
		self.charSelectorList.setIconSize(QtCore.QSize(gICON_SIZE, gICON_SIZE))
		self.charSelectorList.currentItemChanged.connect(self.charSelected)

		blankPixmap = QtGui.QPixmap(gICON_SIZE, gICON_SIZE)
		blankPixmap.fill(QtGui.QColor(240, 240, 230))
		for idx in range(0, self.charSelectorList.count()):
			curItem = self.charSelectorList.item(idx)
			curItem.setIcon(QtGui.QIcon(blankPixmap))
			
		self.charSelectorLayout.addWidget(self.charSelectorList, 0, QtCore.Qt.AlignTop)
		charSelectHgt = self.charSelectorList.height()
			
		self.strokeSelectorLayout = QtGui.QHBoxLayout()
		self.strokeSelectorList = QtGui.QListWidget(self)
		self.strokeSelectorList.setFlow(QtGui.QListView.LeftToRight)
		self.strokeSelectorList.resize(self.width(), gICON_SIZE)
		self.strokeSelectorList.setMaximumHeight(gICON_SIZE*2)
		self.strokeSelectorList.setIconSize(QtCore.QSize(gICON_SIZE, gICON_SIZE))
		self.strokeSelectorLayout.addWidget(self.strokeSelectorList)
		
		self.mainLayout = QtGui.QVBoxLayout() #self.uberMainFrame)
		
		self.mainSplitter = MySplitter (self)

		self.dwgArea = stroke_edit_ui_qt.mainDrawingArea(self) 
		
		self.dwgArea.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken); #6);  # Sunken
		self.dwgArea.setLineWidth(2)
		
		self.toolPane = QtGui.QFrame()
		self.toolPaneLayout = QtGui.QVBoxLayout(self.toolPane)
		
		self.propertyTabs = QtGui.QTabWidget(self.toolPane)
		self.nibPropFrame = QtGui.QFrame()
		self.nibPropLayout = QtGui.QFormLayout(self.nibPropFrame)
		
		nibTypeList = ["Flat", "Scroll", "Brush", "Pen"]
		
		self.nibTypeLabel = QtGui.QLabel(self.nibPropFrame)
		self.nibTypeLabel.setText("Type:")
		
		self.nibTypeSelector = QtGui.QComboBox(self.nibPropFrame)
		self.nibTypeSelector.addItems(QtCore.QStringList(nibTypeList))
		self.nibTypeSelector.currentIndexChanged.connect(self.nibTypeSelected)
		self.nibIdx = 0
		
		self.nibColorLabel = QtGui.QLabel(self.nibPropFrame)
		self.nibColorLabel.setText("Color:")
		self.nibColorButton = QtGui.QPushButton(self.nibPropFrame)
	
		(r, g, b, a) = self.__color__.getRgb()
		self.nibColorButton.setStyleSheet("QPushButton { background-color: rgb("+str(r)+","+str(g)+","+str(b)+") }")
		QtCore.QObject.connect(self.nibColorButton, QtCore.SIGNAL("clicked()"), self.nibColorChanged)
		
		self.nibAngleLabel = QtGui.QLabel(self.nibPropFrame)
		self.nibAngleLabel.setText("Angle:")
		
		self.nibAngleSpin = QtGui.QSpinBox(self.nibPropFrame)
		self.nibAngleSpin.setMinimum(0)
		self.nibAngleSpin.setMaximum(179)
		self.nibAngleSpin.setValue(40)
		self.nibAngleSpin.setWrapping(True)
		QtCore.QObject.connect(self.nibAngleSpin, QtCore.SIGNAL("valueChanged(int)"), self.nibAngleChanged)
		
		self.nibSizeLabel = QtGui.QLabel(self.nibPropFrame)
		self.nibSizeLabel.setText("Width:")
		
		self.nibSizeSpin = QtGui.QSpinBox(self.nibPropFrame)
		self.nibSizeSpin.setMinimum(1)
		self.nibSizeSpin.setMaximum(50)
		self.nibSizeSpin.setValue(10)
		self.nibSizeSpin.setWrapping(False)
		QtCore.QObject.connect(self.nibSizeSpin, QtCore.SIGNAL("valueChanged(int)"), self.nibSizeChanged)
		
		self.nibSplitSizeLabel = QtGui.QLabel(self.nibPropFrame)
		self.nibSplitSizeLabel.setText("Split Width:")
		self.nibSplitSizeLabel.setEnabled(False)
				
		self.nibSplitSizeSpin = QtGui.QSpinBox(self.nibPropFrame)
		self.nibSplitSizeSpin.setMinimum(1)
		self.nibSplitSizeSpin.setMaximum(8)
		self.nibSplitSizeSpin.setValue(5)
		self.nibSplitSizeSpin.setWrapping(False)
		self.nibSplitSizeSpin.setEnabled(False)
		QtCore.QObject.connect(self.nibSplitSizeSpin, QtCore.SIGNAL("valueChanged(int)"), self.nibSplitSizeChanged)
		
		self.nibPropLayout.addRow(self.nibTypeLabel, self.nibTypeSelector)
		self.nibPropLayout.addRow(self.nibAngleLabel, self.nibAngleSpin)
		self.nibPropLayout.addRow(self.nibSizeLabel, self.nibSizeSpin)
		self.nibPropLayout.addRow(self.nibSplitSizeLabel, self.nibSplitSizeSpin)
		self.nibPropLayout.addRow(self.nibColorLabel, self.nibColorButton)
		
		self.nibPropFrame.setLayout(self.nibPropLayout)
		
		self.pointPropFrame = QtGui.QFrame()
		self.pointPropLayout = QtGui.QFormLayout(self.pointPropFrame)

		pointBehaviorList = ["Smooth", "Sharp", "Symmetric"]
		
		self.pointBehaviorLabel = QtGui.QLabel(self.pointPropFrame)
		self.pointBehaviorLabel.setText("Behavior:")
		
		self.pointBehaviorSelector = QtGui.QComboBox(self.pointPropFrame)
		self.pointBehaviorSelector.addItems(QtCore.QStringList(pointBehaviorList))
		#self.pointBehaviorSelector.currentIndexChanged.connect(self.pointBehaviorSelected)
		self.pointPropLayout.addRow(self.pointBehaviorLabel, self.pointBehaviorSelector)

		self.pointPropFrame.setLayout(self.pointPropLayout)

		self.guidePropFrame = QtGui.QFrame()
		self.guidePropLayout = QtGui.QFormLayout(self.guidePropFrame)

		guides = self.dwgArea.getGuideLines()
		
		mainLabel = QtGui.QLabel(self.guidePropFrame)
		mainLabel.setText("Note: All units are nib-widths.")
		self.guidePropLayout.addRow(mainLabel)
		
		self.baseHeightLabel = QtGui.QLabel(self.guidePropFrame)
		self.baseHeightLabel.setText("Base height:")
		
		self.baseHeightSpin = QtGui.QDoubleSpinBox(self.guidePropFrame)
		self.baseHeightSpin.setMinimum(1.0)
		self.baseHeightSpin.setMaximum(10.0)
		self.baseHeightSpin.setValue(guides.baseHeight)
		self.baseHeightSpin.setWrapping(True)
		self.baseHeightSpin.setDecimals(1)
		self.baseHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.baseHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.guideBaseHeightChanged)
		
		self.capHeightLabel = QtGui.QLabel(self.guidePropFrame)
		self.capHeightLabel.setText("Capital height:")
		
		self.capHeightSpin = QtGui.QDoubleSpinBox(self.guidePropFrame)
		self.capHeightSpin.setMinimum(0.5)
		self.capHeightSpin.setMaximum(guides.ascentHeight)
		self.capHeightSpin.setValue(guides.capHeight)
		self.capHeightSpin.setWrapping(True)
		self.capHeightSpin.setDecimals(1)
		self.capHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.capHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.guideCapHeightChanged)
		
		self.ascentHeightLabel = QtGui.QLabel(self.guidePropFrame)
		self.ascentHeightLabel.setText("Ascent height:")
		
		self.ascentHeightSpin = QtGui.QDoubleSpinBox(self.guidePropFrame)
		self.ascentHeightSpin.setMinimum(1)
		self.ascentHeightSpin.setMaximum(10)
		self.ascentHeightSpin.setValue(guides.ascentHeight)
		self.ascentHeightSpin.setWrapping(True)
		self.ascentHeightSpin.setDecimals(1)
		self.ascentHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.ascentHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.guideAscentChanged)
		
		self.descentHeightLabel = QtGui.QLabel(self.guidePropFrame)
		self.descentHeightLabel.setText("Descent height:")
		
		self.descentHeightSpin = QtGui.QDoubleSpinBox(self.guidePropFrame)
		self.descentHeightSpin.setMinimum(1)
		self.descentHeightSpin.setMaximum(10)
		self.descentHeightSpin.setValue(guides.descentHeight)
		self.descentHeightSpin.setWrapping(True)
		self.descentHeightSpin.setDecimals(1)
		self.descentHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.descentHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.guideDescentChanged)
				
		self.angleLabel = QtGui.QLabel(self.guidePropFrame)
		self.angleLabel.setText("Guide angle:")
		
		self.angleSpin = QtGui.QSpinBox(self.guidePropFrame)
		self.angleSpin.setMinimum(0)
		self.angleSpin.setMaximum(45)
		self.angleSpin.setValue(guides.angle)
		self.angleSpin.setWrapping(True)
		QtCore.QObject.connect(self.angleSpin, QtCore.SIGNAL("valueChanged(int)"), self.guideAngleChanged)
		
		self.gapHeightLabel = QtGui.QLabel(self.guidePropFrame)
		self.gapHeightLabel.setText("Gap distance:")
		
		self.gapHeightSpin = QtGui.QDoubleSpinBox(self.guidePropFrame)
		self.gapHeightSpin.setMinimum(1)
		self.gapHeightSpin.setMaximum(10)
		self.gapHeightSpin.setValue(guides.gapHeight)
		self.gapHeightSpin.setWrapping(True)
		self.gapHeightSpin.setDecimals(1)
		self.gapHeightSpin.setSingleStep(0.5)
		QtCore.QObject.connect(self.gapHeightSpin, QtCore.SIGNAL("valueChanged(double)"), self.guideGapHeightChanged)
		
		self.guidePropLayout.addRow(self.baseHeightLabel, self.baseHeightSpin)
		self.guidePropLayout.addRow(self.capHeightLabel, self.capHeightSpin)
		self.guidePropLayout.addRow(self.ascentHeightLabel, self.ascentHeightSpin)
		self.guidePropLayout.addRow(self.descentHeightLabel, self.descentHeightSpin)
		self.guidePropLayout.addRow(self.angleLabel, self.angleSpin)
		self.guidePropLayout.addRow(self.gapHeightLabel, self.gapHeightSpin)
	
		self.guidePropFrame.setLayout(self.guidePropLayout)

		self.propertyTabs.addTab(self.nibPropFrame, "Nib")
		self.propertyTabs.addTab(self.pointPropFrame, "Control Point")
		self.propertyTabs.addTab(self.guidePropFrame, "Guidelines")

		self.toolPaneLayout.setMargin(0)
		self.toolPaneLayout.setSpacing(0)
		self.toolPaneLayout.addWidget(self.propertyTabs)
		
		self.toolPane.setLayout(self.toolPaneLayout)
		self.toolPane.setMaximumWidth(self.toolPane.width())
		
		self.mainSplitter.addWidget(self.dwgArea)
		self.mainSplitter.addWidget(self.toolPane)
		self.mainSplitter.setMaxPaneWidth(wid20)
		self.mainSplitter.setSizes([wid80, wid20])
		
		self.mainLayout.addWidget(self.mainSplitter)
		self.mainLayout.setMargin(0)
		self.mainLayout.setSpacing(0)
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		mainSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.mainSplitter.setSizePolicy(mainSizePolicy)
		
		self.dwgArea.setSizePolicy(mainSizePolicy)

		self.uberMainLayout.addLayout(self.charSelectorLayout)
		self.uberMainLayout.addLayout(self.strokeSelectorLayout)
		self.uberMainLayout.addLayout(self.mainLayout, 2)

		self.mainWidget = QtGui.QWidget()
		self.mainWidget.setLayout(self.uberMainLayout)

		self.setCentralWidget(self.mainWidget)

	def about_cb(self, event):
		reply = QtGui.QMessageBox.information(self, 'About', "This is a program", \
			QtGui.QMessageBox.Ok )

	def quit_cb(self, event):
		reply = QtGui.QMessageBox.question(self, 'Quit Program', "Are you sure to quit?", \
			QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.close()
		

	def undo_cb(self, event):
		if not len(self.__undoStack):
			return
			
		undoItem = self.__undoStack.pop()
		undoItem['undo'](undoItem['undoArgs'])
		
		self.__redoStack.append(undoItem)
	
		self.repaint()
		self.dwgArea.repaint()
		
	def redo_cb(self, event):
		if not len(self.__redoStack):
			return
			
		redoItem = self.__redoStack.pop()
		
		redoItem['do'](redoItem['doArgs'])
		
		self.__undoStack.append(redoItem)
		
		self.repaint()
		self.dwgArea.repaint()
		
	def alignTangents_cb(self, event):
		self.dwgArea.alignTangents()
		self.dwgArea.repaint()
	
	def alignTangentsSymmetrical_cb(self, event):
		self.dwgArea.alignTangentsSymmetrical()
		self.dwgArea.repaint()
		
	def breakTangents_cb(self, event):
		self.dwgArea.breakTangents()
		self.dwgArea.repaint()
	
	def straightenStroke_cb(self, event):
		selectedStrokes = self.dwgArea.getSelectedStrokes()
		
		oldCtrlPtList = []
		newCtrlPtList = []
		
		doArgs = {}
		doArgs['strokes'] = selectedStrokes
		undoArgs = {}
		undoArgs['strokes'] = selectedStrokes 
						
		for stroke in selectedStrokes:
			oldCtrlPtList.append(stroke.straighten())
			newCtrlPtList.append(stroke.getCtrlVertices())
		
		doArgs['verts'] = newCtrlPtList
		undoArgs['verts'] = oldCtrlPtList
		
		command = {
			'undo': self.setStrokeCtrlVerts, 'undoArgs': undoArgs, 
			'do': self.setStrokeCtrlVerts, 'doArgs': doArgs
			}
		
		self.__undoStack.append(command)
		self.__redoStack[:] = []
		
		self.dwgArea.repaint()
	
	def setStrokeCtrlVerts(self, args):
		if (args.has_key('verts')):
			vertList = args['verts']
			
			if (args.has_key('strokes')):
				strokeList = args['strokes']
				
				for strokeNum in range(0, len(strokeList)):
					strokeList[strokeNum].setCtrlVertices(vertList[strokeNum])
					strokeList[strokeNum].calcCurvePoints()
				
				self.dwgArea.repaint()
	 
	def addControlPoint_cb(self, event):
		QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)
		self.dwgArea.addControlPoint()
		QtGui.qApp.restoreOverrideCursor()
		self.dwgArea.repaint()
		
	def cutStrokes_cb(self, event):
		self.dwgArea.cutSelected()
	
	def copyStrokes_cb(self, event):
		self.dwgArea.copySelected()

	def pasteStrokes_cb(self, event):
		self.dwgArea.pasteSelected()
	
	def pasteStrokesAsInstances_cb(self, event):
		self.dwgArea.pasteSelectedAsInstances()
	 
	def saveStroke_cb(self, event):
		selectedStrokes = self.dwgArea.getSelectedStrokes()

		for stroke in selectedStrokes:
			if isinstance(stroke, stroke_qt.Stroke):
				stroke.makePreview(gICON_SIZE)
				itemNum = self.strokeSelectorList.count()
				self.strokeSelectorList.addItem(str(itemNum))
				curItem = self.strokeSelectorList.item(itemNum)
				self.strokeSelectorList.setCurrentRow(itemNum)
				curItem.setIcon(QtGui.QIcon(stroke.getBitmap()))
				self.charData.saveStroke(stroke_qt.Stroke(fromStroke=stroke))
				curChar = self.charData.getCurrentChar()
				curChar.deleteStroke(stroke)
				stroke = self.charData.getSavedStroke(itemNum)
				selectList = []
				selectList.append(curChar.addStrokeInstance(stroke))			
				self.dwgArea.setSelectedStrokes(selectList)
			
		self.dwgArea.repaint()
			
	def pasteFromSaved_cb(self, event):
		strokeSel = self.strokeSelectorList.currentRow()
		curChar = self.charData.getCurrentChar()
	
		if strokeSel >= 0:
			stroke = self.charData.getSavedStroke(strokeSel)
			selectList = []
			selectList.append(curChar.addStroke(stroke))

			self.dwgArea.setSelectedStrokes(selectList)
		
			self.dwgArea.repaint()

	def pasteInstanceFromSaved_cb(self, event):
		strokeSel = self.strokeSelectorList.currentRow()
		curChar = self.charData.getCurrentChar()
	
		if strokeSel >= 0:
			stroke = self.charData.getSavedStroke(strokeSel)
			selectList = []
			selectList.append(curChar.addStrokeInstance(stroke))

			self.dwgArea.setSelectedStrokes(selectList)
		
			self.dwgArea.repaint()

	def editSaved_cb(self, event):
		curChar = self.charData.getCurrentChar()
		stroke = None

		selectedStrokes = self.dwgArea.getSelectedStrokes()
		if len(selectedStrokes):
			selectedStroke = selectedStrokes[0]
		else:
			return
			
		if not isinstance(selectedStroke, stroke_qt.Stroke):
			parent = selectedStroke.getStroke()
			for row in range(0, self.strokeSelectorList.count()):
				tmpStroke = self.charData.getSavedStroke(row) 
				if tmpStroke == parent:
					stroke = tmpStroke
					self.strokeSelectorList.setCurrentRow(row)
					break
				else:
					print tmpStroke, parent
				
		if stroke is None:
			return

		selectList = []
		selectList.append(curChar.addStroke(stroke,False))

		self.dwgArea.setSelectedStrokes(selectList)
		self.dwgArea.setInstanceEditMode(True);
		self.dwgArea.repaint()
	
	def editSavedDone_cb(self, event):
		strokeSel = self.strokeSelectorList.currentRow()
		curChar = self.charData.getCurrentChar()
	
		if strokeSel >= 0:
			stroke = self.dwgArea.getSelectedStrokes()[0]
			stroke.makePreview(gICON_SIZE)
			curItem = self.strokeSelectorList.item(strokeSel)
			curItem.setIcon(QtGui.QIcon(stroke.getBitmap()))
			curChar = self.charData.getCurrentChar()
			curChar.deleteStroke(stroke)
			self.dwgArea.setInstanceEditMode(False);
			self.dwgArea.repaint()

	def viewToggleGuidelines_cb(self, event):
		self.dwgArea.toggleGuidelines()	
		self.dwgArea.repaint()
	
	def viewToggleNibGuides_cb(self, event):
		self.dwgArea.toggleNibGuides()
		self.dwgArea.repaint()
	
	def viewToggleSnapAxially_cb(self, event):
		self.dwgArea.toggleSnapAxially()
		self.dwgArea.repaint()
	
	def viewToggleSnapToNibAxes_cb(self, event):
		self.dwgArea.toggleSnapToNibAxes()
		self.dwgArea.repaint()
	
	def viewToggleSnapToGrid_cb(self, event):
		self.dwgArea.toggleSnapToGrid()
		self.dwgArea.repaint()
		
	def viewToggleSnapToCtrlPts_cb(self, event):
		self.dwgArea.toggleSnapToCtrlPts()
		self.dwgArea.repaint()
		
	def viewToggleSnapToStroke_cb(self, event):
		self.dwgArea.toggleSnapToStrokes()
		self.dwgArea.repaint()
		
	# 		
	def fileNew_cb(self):
	 	self.__fileName__ = None
	
		self.charData = character_set.character_set()
		self.dwgArea.setCharData(self.charData.getCurrentChar())
		self.name = (self.__label__ + " - Untitled")
		self.setWindowTitle(self.name)

		self.strokeSelectorList.clear()
		
		self.charSelectorList.setCurrentRow(0)
	
		self.charSelected()
	 	self.nibTypeSelected()
		self.setNibColor({'color': self.__color__})
		
		self.__undoStack[:] = []
		self.__redoStack[:] = []
	
		self.dwgArea.setUndoStack(self.__undoStack)
		self.dwgArea.setRedoStack(self.__redoStack)
	
	# 					
	def fileSave_cb(self, event):
		if self.__fileName__ and os.path.isfile(self.__fileName__):
			self.save(self.__fileName__)
		else:
			self.fileSaveAs_cb(event)
				
	def fileSaveAs_cb(self, event):
		fileName = self.fileOpenDlg.getSaveFileName(self,
		     "Save Character Set", self.__dirName__, "Character Set Files (*.cs)")
			
		if (fileName):
			(self.__dirName__, self.__fileName__) = os.path.split(str(fileName))
				
			self.save(self.__fileName__)
			self.setWindowTitle(self.__label__ + " - " + self.__fileName__)
		 		
	def fileOpen_cb(self):
	 	fileName = None
		fileName = self.fileOpenDlg.getOpenFileName(self,
		     "Open Character Set", self.__dirName__, "Character Set Files (*.cs)")

		if (fileName):
			self.load(fileName)

			(self.__dirName__, self.__fileName__) = os.path.split(str(fileName))

			self.name = (self.__label__ + " - " + self.__fileName__)
	 		self.setWindowTitle(self.name)
		
			loadedChars = self.charData.getCharList().keys()
	 		loadedChars.sort()

			self.dwgArea.setCharData(self.charData.getCurrentChar())

	 		self.strokeSelectorList.clear()

	 		for stroke in self.charData.getSavedStrokes():
				stroke.makePreview(gICON_SIZE)
				itemNum = self.strokeSelectorList.count()
				self.strokeSelectorList.addItem(str(itemNum))
				curItem = self.strokeSelectorList.item(itemNum)
				self.strokeSelectorList.setCurrentRow(itemNum)
				curItem.setIcon(QtGui.QIcon(stroke.getBitmap()))
				
			self.charSelectorList.setCurrentRow(0)
			self.charSelected()
	 		self.nibTypeSelected()
			self.setNibColor({'color': self.__color__})
		
			self.dwgArea.setSelectedStrokes([])
	 		self.dwgArea.repaint()
		
			self.__undoStack[:] = []
			self.__redoStack[:] = []
			
			self.dwgArea.setUndoStack(self.__undoStack)
			self.dwgArea.setRedoStack(self.__redoStack)
	
	def save(self, fileName):
		try:
			dataFileFd = open(fileName, 'wb')
		except IOError:
			print "ERROR: Couldn't open %s for writing." % (fileName)
			return 1
		
		try:
			dataPickler = pickle.Pickler(dataFileFd)
			dataPickler.dump(self.charData)
		except pickle.PicklingError:
			print "ERROR: Couldn't serialize data"
			return 1
		
		if dataFileFd:
			dataFileFd.close()

	def load(self, fileName):
		try:
			dataFileFd = open(fileName, 'rb')
		except IOError:
			print "ERROR: Couldn't open %s for reading." % (fileName)
			return 1
		
		try:
			dataPickler = pickle.Unpickler(dataFileFd)		
			self.charData = dataPickler.load()
		except pickle.UnpicklingError:
			print "ERROR: Couldn't unserialize data"
			return 1
		except:
			print "ERROR: OTHER"
			return 1

		if dataFileFd:
			dataFileFd.close()
				
	# 		
	def createNewStroke_cb(self, event):
		curChar = self.charSelectorList.currentItem()

		if (curChar):
			QtGui.qApp.setOverrideCursor(QtCore.Qt.CrossCursor)
			self.dwgArea.newStroke()
			self.repaint()	
			QtGui.qApp.restoreOverrideCursor()
	
	def createNewFreehandStroke_cb(self, event):
		curChar = self.charSelectorList.currentItem()
		
		if (curChar):
			self.dwgArea.newFreehandStroke()
			self.repaint()
	
	def joinStrokes_cb(self, event):
		selectedStrokes = self.dwgArea.getSelectedStrokes()
	
		if (len(selectedStrokes) < 2):
			print("You must select at least two strokes to join!");
			return
		
		curChar = self.charData.getCurrentChar()
			
		doArgs = {}
		doArgs['strokesToJoin'] = selectedStrokes
		undoArgs = {}
		undoArgs['strokesToUnjoin'] = selectedStrokes 
		undoArgs['joinedStroke'] = curChar.joinStrokes(doArgs)
		doArgs['joinedStroke'] = undoArgs['joinedStroke']
		
		command = {
				'undo': curChar.unjoinStrokes, 'undoArgs': undoArgs, 
				'do': curChar.rejoinStrokes, 'doArgs': doArgs
				}
				
		self.__undoStack.append(command)
		self.__redoStack[:] = []
		
		selectList = []
		selectList.append(undoArgs['joinedStroke'])
		self.dwgArea.setSelectedStrokes(selectList)
		
		self.repaint()
		self.dwgArea.repaint()
	# 			
	def charSelected(self, event=None):
	 	iconBitmap = self.dwgArea.createIconFromCanvas(gICON_SIZE) #self.charWindow)
			
		curChar = self.charData.getCurrentChar()
		if (iconBitmap) and (curChar):
			curChar.bitmapPreview = iconBitmap
			oldCharIdx = self.charData.getCurrentCharIndex()
			curItem = self.charSelectorList.item(oldCharIdx)
			curItem.setIcon(QtGui.QIcon(curChar.bitmapPreview))
			
		curCharIdx = self.charSelectorList.currentRow()
		
		if (curChar):
	 		undoArgs = {}
	 		undoArgs['char'] = oldCharIdx
	 	
	 		doArgs = {}
	 		doArgs['char'] = curCharIdx
	 
	 		command = {
	 				'undo': self.selectChar, 'undoArgs': undoArgs, 
	 				'do': self.selectChar, 'doArgs': doArgs
	 				}
	 
	 		self.__undoStack.append(command)
	 		self.__redoStack[:] = []
	 	
	 	self.charData.setCurrentChar(curCharIdx)
	 	self.dwgArea.setCharData(self.charData.getCurrentChar())
		
	 	self.dwgArea.repaint()
	
	def selectChar(self, args):
	 	if (args.has_key('char')):
	 		newChar = args['char']
	 		
	 		self.charData.setCurrentChar(newChar)
			curChar = self.charData.getCurrentChar()
	 		self.dwgArea.setCharData(curChar)
	 		self.charSelectorList.setCurrentRow(newChar)
			
			self.dwgArea.repaint()
	
	def nibTypeSelected(self, event=None):
		curNibIdx = self.nibTypeSelector.currentIndex()
		undoArgs = {}
		undoArgs['nibType'] = self.nibIdx
		
		doArgs = {}
		doArgs['nibType'] = curNibIdx
	
		command = {
			'undo': self.selectNibType, 'undoArgs': undoArgs,
			'do': self.selectNibType, 'doArgs': doArgs
		}
		
		self.__undoStack.append(command)
		self.__redoStack[:] = []
		
		self.selectNibType(doArgs)
		
		self.repaint()
		self.dwgArea.repaint()
		
	def selectNibType(self, args):
		if (args.has_key('nibType')):
			self.nibIdx = args['nibType']
			
			width = self.nibSizeSpin.value()
			angle = self.nibAngleSpin.value()
			split = self.nibSplitSizeSpin.value()
			# this is so wasteful...create them in the beginning and just use 'em
			# make them singletons?
			del self.__mainNib__ 

			if (self.nibIdx == 0):
				self.nibSplitSizeLabel.setEnabled(False)
				self.nibSplitSizeSpin.setEnabled(False)
				self.nibAngleLabel.setEnabled(True)
				self.nibAngleSpin.setEnabled(True)
				self.__mainNib__ = nibs_qt.Nib(width, angle, color=self.__color__)
			elif (self.nibIdx == 1):
				self.nibSplitSizeLabel.setEnabled(True)
				self.nibSplitSizeSpin.setEnabled(True)
				self.nibAngleLabel.setEnabled(True)
				self.nibAngleSpin.setEnabled(True)
				self.__mainNib__ = nibs_qt.ScrollNib(width, angle, split, color=self.__color__)
			elif (self.nibIdx == 2):
				self.nibSplitSizeLabel.setEnabled(False)
				self.nibSplitSizeSpin.setEnabled(False)
				self.nibAngleLabel.setEnabled(True)
				self.nibAngleSpin.setEnabled(True)
				self.__mainNib__ = nibs_qt.BrushNib(width, angle, color=self.__color__)
			elif (self.nibIdx == 3):
				self.nibSplitSizeLabel.setEnabled(False)
				self.nibSplitSizeSpin.setEnabled(False)
				self.nibAngleLabel.setEnabled(False)
				self.nibAngleSpin.setEnabled(False)
				self.__mainNib__ = nibs_qt.PenNib(width, angle, color=self.__color__)
			
			self.dwgArea.setNib(self.__mainNib__)	

	def setNibColor(self, args):
		if (args.has_key('color')):
			color = args['color']
			
			self.__mainNib__.setColor(color)
			self.__color__ = color
			(r, g, b, a) = self.__color__.getRgb()
			self.nibColorButton.setStyleSheet("QPushButton { background-color: rgb("+str(r)+","+str(g)+","+str(b)+") }")
		
	def nibColorChanged(self):
		newColor = self.colorPickerDlg.getColor()

		if (newColor == self.__color__):
			return
		
		prevColor = self.__color__	
				
		command = {
			'undo': self.setNibColor, 'undoArgs': {'color': prevColor},
			'do': self.setNibColor, 'doArgs': {'color': newColor}
		}
		
		self.__undoStack.append(command)
		self.__redoStack[:] = []
		
		self.setNibColor({'color': newColor})
		
		self.repaint()
		
	# 		
	# 
	def nibAngleChanged(self, event):
		prevValue = self.__mainNib__.getAngle()
	 	newValue = self.nibAngleSpin.value()
		
	 	if (newValue == prevValue):
	 		return
	 		
	 	self.__mainNib__.setAngle(newValue)
	 	
	 	command = {
	 		'undo': self.changeNibAngle, 'undoArgs': {'value': prevValue},
	 		'do': self.changeNibAngle, 'doArgs': {'value': newValue}
	 		}
	 	
	 	self.__undoStack.append(command)
	 	self.__redoStack[:] = []
	 	self.repaint()
	
	# 
	def nibSizeChanged(self, event):
		prevValue = self.__mainNib__.getWidth()
		newValue = self.nibSizeSpin.value()
		
		if (newValue == prevValue):
			return
		
		command = {
			'undo': self.changeNibSize, 'undoArgs': {'value': prevValue},
			'do': self.changeNibSize, 'doArgs': {'value': newValue}
			}
		
		self.changeNibSize({'value': newValue})
		self.__undoStack.append(command)
		self.__redoStack[:] = []
		
		self.repaint()
	
	def nibSplitSizeChanged(self, event):
		newValue = self.nibSplitSizeSpin.value()
		
		if (self.nibIdx == 1):
			prevValue = self.__mainNib__.getSplitSize()
		else:
			prevValue = newValue
			
		if (newValue == prevValue):
			return

		if (self.nibIdx == 1):
			self.__mainNib__.setSplitSize(newValue)

		command = {
			'undo': self.changeNibSplitSize, 'undoArgs': {'value': prevValue},
			'do': self.changeNibSplitSize, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		self.repaint()

	def changeNibAngle(self, args):
		if (args.has_key('value')):
			val = args['value']
			
			self.__mainNib__.setAngle(val)
			self.nibAngleSpin.setValue(val)
	 	
	def changeNibSize(self, args):
		if (args.has_key('value')):
			val = args['value']
			
			self.__mainNib__.setWidth(val)
			self.nibSizeSpin.setValue(val)
			self.nibSplitSizeSpin.setMaximum(val-1)
			splitVal = self.nibSplitSizeSpin.value()
			if (splitVal >= val):
				self.nibSplitSizeSpin.setValue(val-1)
				if (self.nibIdx == 1):
					self.__mainNib__.setSplitSize(val-1)
			
	def changeNibSplitSize(self, args):
		if (args.has_key('value')):
			val = args['value']

			self.nibSizeSpin.setValue(val)

	def guideBaseHeightChanged(self, event):
		newValue = self.baseHeightSpin.value()

		guides = self.dwgArea.getGuideLines()
		
		prevValue = guides.baseHeight

		if (newValue == prevValue):
			return

		command = {
			'undo': self.changeGuideBaseHeight, 'undoArgs': {'value': prevValue},
			'do': self.changeGuideBaseHeight, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		guides.baseHeight = newValue

		self.dwgArea.repaint()

	def changeGuideBaseHeight(self, args):
		if (args.has_key('value')):
			val = args['value']

			guides = self.dwgArea.getGuideLines()
			guides.baseHeight = val
			self.baseHeightSpin.setValue(val)

	def guideCapHeightChanged(self, event):
		newValue = self.capHeightSpin.value()

		guides = self.dwgArea.getGuideLines()
		
		prevValue = guides.capHeight

		if (newValue == prevValue):
			return

		command = {
			'undo': self.changeCapHeight, 'undoArgs': {'value': prevValue},
			'do': self.changeCapHeight, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		guides.capHeight = newValue

		self.dwgArea.repaint()

	def changeCapHeight(self, args):
		if (args.has_key('value')):
			val = args['value']

			guides = self.dwgArea.getGuideLines()
			guides.capHeight = val
			self.capHeightSpin.setValue(val)

	def guideAscentChanged(self, event):
		newValue = self.ascentHeightSpin.value()

		guides = self.dwgArea.getGuideLines()
		
		prevValue = guides.ascentHeight

		if (newValue == prevValue):
			return

		command = {
			'undo': self.changeAscentHeight, 'undoArgs': {'value': prevValue},
			'do': self.changeAscentHeight, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		guides.ascentHeight = newValue
		self.capHeightSpin.setMaximum(newValue)
		
		self.dwgArea.repaint()

	def changeAscentHeight(self, args):
		if (args.has_key('value')):
			val = args['value']

			guides = self.dwgArea.getGuideLines()
			guides.ascentHeight = val
			self.ascentHeightSpin.setValue(val)

	def guideDescentChanged(self, event):
		newValue = self.descentHeightSpin.value()

		guides = self.dwgArea.getGuideLines()
		
		prevValue = guides.descentHeight

		if (newValue == prevValue):
			return

		command = {
			'undo': self.changeDescentHeight, 'undoArgs': {'value': prevValue},
			'do': self.changeDescentHeight, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		guides.descentHeight = newValue

		self.dwgArea.repaint()

	def changeDescentHeight(self, args):
		if (args.has_key('value')):
			val = args['value']

			guides = self.dwgArea.getGuideLines()
			guides.descentHeight = val
			self.descentHeightSpin.setValue(val)
	
	def guideAngleChanged(self, event):
		newValue = self.angleSpin.value()

		guides = self.dwgArea.getGuideLines()
		
		prevValue = guides.angle

		if (newValue == prevValue):
			return

		command = {
			'undo': self.changeGuideAngle, 'undoArgs': {'value': prevValue},
			'do': self.changeGuideAngle, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		guides.angle = newValue

		self.dwgArea.repaint()

	def changeGuideAngle(self, args):
		if (args.has_key('value')):
			val = args['value']

			guides = self.dwgArea.getGuideLines()
			guides.angle = val
			self.angleSpin.setValue(val)

	def guideGapHeightChanged(self, event):
		newValue = self.gapHeightSpin.value()

		guides = self.dwgArea.getGuideLines()
		
		prevValue = guides.gapHeight

		if (newValue == prevValue):
			return

		command = {
			'undo': self.changeGuideGapHeight, 'undoArgs': {'value': prevValue},
			'do': self.changeGuideGapHeight, 'doArgs': {'value': newValue}
		}

		self.__undoStack.append(command)
		self.__redoStack[:] = []

		guides.gapHeight = newValue

		self.dwgArea.repaint()

	def changeGuideGapHeight(self, args):
		if (args.has_key('value')):
			val = args['value']

			guides = self.dwgArea.getGuideLines()
			guides.gapHeight = val
			self.gapHeightSpin.setValue(val)

	def resizeEvent(self, evt):
		self.repaint()	
	
class MySplitter(QtGui.QSplitter):
	def __init__(self, parent):
		QtGui.QSplitter.__init__(self, parent)
		self.parent = parent
		self.maxPaneWidth = 0

	def createHandle(self):
		splitterHandle = MySplitterHandle(1, self)
		QtCore.QObject.connect(splitterHandle, QtCore.SIGNAL("doubleClickSignal"), self.onSashDoubleClick)
		return splitterHandle

	def onSashDoubleClick(self):
		dwgArea = self.widget(0)
		toolPane = self.widget(1)
		
		if (self.maxPaneWidth == 0):
			self.maxPaneWidth = toolPane.width()
		
		if (toolPane.size().width() > 0):
			self.moveSplitter(self.width(), 1)
		else:
			self.moveSplitter(self.width()-self.maxPaneWidth, 1)
		
		self.repaint()
		
	def setMaxPaneWidth(self, width):
		self.maxPaneWidth = width
			
class MySplitterHandle(QtGui.QSplitterHandle):
	def __init__(self, orientation, parent):
		QtGui.QSplitterHandle.__init__(self, orientation, parent)
		self.doubleClickSignal = QtCore.pyqtSignal()
		
	def mouseDoubleClickEvent(self, event):
		self.emit(QtCore.SIGNAL("doubleClickSignal"))
		
