#!/usr/bin/env python

#****************************************************************************
# altbasedialog.py, provides a dialog box for other bases (binary, octal, hex
#
# rpCalc, an RPN calculator
# Copyright (C) 2008, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt4 import QtCore, QtGui
import calccore
import icons

class AltBaseDialog(QtGui.QWidget):
    """Displays edit boxes for other number bases"""
    baseCode = {'X':16, 'O':8, 'B':2, 'D':10}
    def __init__(self, dlgRef, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.dlgRef = dlgRef
        self.tempBase = False
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setWindowTitle('rpCalc Alternate Bases')
        self.setWindowIcon(icons.iconDict['calc'])
        topLay = QtGui.QVBoxLayout(self)
        self.setLayout(topLay)
        mainLay = QtGui.QGridLayout()
        topLay.addLayout(mainLay)
        self.buttons = QtGui.QButtonGroup(self)
        self.editBoxes = []
        hexButton = QtGui.QPushButton('&Hex')
        self.buttons.addButton(hexButton, 16)
        mainLay.addWidget(hexButton, 0, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(16))
        mainLay.addWidget(self.editBoxes[-1], 0, 1)
        octalButton = QtGui.QPushButton('&Octal')
        self.buttons.addButton(octalButton, 8)
        mainLay.addWidget(octalButton, 1, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(8))
        mainLay.addWidget(self.editBoxes[-1], 1, 1)
        binaryButton = QtGui.QPushButton('&Binary')
        self.buttons.addButton(binaryButton, 2)
        mainLay.addWidget(binaryButton, 2, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(2))
        mainLay.addWidget(self.editBoxes[-1], 2, 1)
        decimalButton = QtGui.QPushButton('&Decimal')
        self.buttons.addButton(decimalButton, 10)
        mainLay.addWidget(decimalButton, 3, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(10))
        mainLay.addWidget(self.editBoxes[-1], 3, 1)
        for button in self.buttons.buttons():
            button.setCheckable(True)
        self.buttons.button(self.dlgRef.calc.base).setChecked(True)
        self.connect(self.buttons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.changeBase)
        closeButton = QtGui.QPushButton('&Close')
        topLay.addWidget(closeButton)
        self.connect(closeButton, QtCore.SIGNAL('clicked()'), self.close)
        option = self.dlgRef.calc.option
        self.move(option.intData('AltBaseXPos', 0, 10000),
                  option.intData('AltBaseYPos', 0, 10000))

    def updateData(self):
        """Update edit box contents for current registers"""
        if self.tempBase and self.dlgRef.calc.flag != calccore.Mode.entryMode:
            self.dlgRef.calc.base = 10
            self.buttons.button(self.dlgRef.calc.base).setChecked(True)
            self.tempBase = False
        for box in self.editBoxes:
            box.setValue(self.dlgRef.calc.stack[0])

    def changeBase(self, base):
        """Change base based on button click"""
        self.dlgRef.calc.base = base

    def setTempBase(self, baseCode):
        """Set new base from letter code"""
        try:
            self.dlgRef.calc.base = AltBaseDialog.baseCode[baseCode]
            self.buttons.button(self.dlgRef.calc.base).setChecked(True)
            self.tempBase = True
        except KeyError:
            pass

    def keyPressEvent(self, keyEvent):
        """Pass most keypresses to main dialog"""
        if keyEvent.modifiers == QtCore.Qt.AltModifier:
            QtGui.QWidget.keyPressEvent(self, keyEvent)
        else:
            self.dlgRef.keyPressEvent(keyEvent)

    def keyReleaseEvent(self, keyEvent):
        """Pass most key releases to main dialog"""
        if keyEvent.modifiers == QtCore.Qt.AltModifier:
            QtGui.QWidget.keyReleaseEvent(self, keyEvent)
        else:
            self.dlgRef.keyReleaseEvent(keyEvent)


class AltBaseEdit(QtGui.QLabel):
    """Displays an edit box at a particular base"""
    def __init__(self, base, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.base = base
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setLineWidth(3)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Minimum)

    def setValue(self, num):
        """Set value to num in proper base"""
        self.setText(calccore.numberStr(num, self.base))
