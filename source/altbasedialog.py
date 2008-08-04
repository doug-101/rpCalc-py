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
import icons

class AltBaseDialog(QtGui.QWidget):
    """Displays edit boxes for other number bases"""
    def __init__(self, dlgRef, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.dlgRef = dlgRef
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setWindowTitle('rpCalc Alternate Bases')
        self.setWindowIcon(icons.iconDict['calc'])
        self.base = 10
        topLay = QtGui.QVBoxLayout(self)
        self.setLayout(topLay)
        mainLay = QtGui.QGridLayout()
        topLay.addLayout(mainLay)
        self.buttons = QtGui.QButtonGroup(self)
        self.editBoxes = []
        hexButton = QtGui.QPushButton('Hex')
        self.buttons.addButton(hexButton, 16)
        mainLay.addWidget(hexButton, 0, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(16))
        mainLay.addWidget(self.editBoxes[-1], 0, 1)
        octalButton = QtGui.QPushButton('Octal')
        self.buttons.addButton(octalButton, 8)
        mainLay.addWidget(octalButton, 1, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(8))
        mainLay.addWidget(self.editBoxes[-1], 1, 1)
        binaryButton = QtGui.QPushButton('Binary')
        self.buttons.addButton(binaryButton, 2)
        mainLay.addWidget(binaryButton, 2, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(2))
        mainLay.addWidget(self.editBoxes[-1], 2, 1)
        decimalButton = QtGui.QPushButton('Decimal')
        self.buttons.addButton(decimalButton, 10)
        mainLay.addWidget(decimalButton, 3, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(10))
        mainLay.addWidget(self.editBoxes[-1], 3, 1)
        for button in self.buttons.buttons():
            button.setCheckable(True)
        self.buttons.button(self.base).setChecked(True)
        self.connect(self.buttons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.changeBase)
        closeButton = QtGui.QPushButton('Close')
        topLay.addWidget(closeButton)
        self.connect(closeButton, QtCore.SIGNAL('clicked()'), self.close)

    def updateData(self):
        """Update edit box contents for current registers"""
        for box in self.editBoxes:
            box.setValue(self.dlgRef.calc.stack[0])

    def changeBase(self, base):
        """Change base based on button click"""
        self.base = base

    def convertNumber(self, num):
        """Convert number to the current base"""
        if self.base != 10:
            num = int(num, self.base)
        return num


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
        self.setText(numberStr(num, self.base))


def numberStr(number, base):
    """Return string of number in given base (2-16)"""
    digits = '0123456789abcdef'
    number = int(round(number))
    result = ''
    sign = ''
    if number < 0:
        number = abs(number)
        sign = '-'
    while number:
        number, remainder = divmod(number, base)
        result = '%s%s' % (digits[remainder], result)
    return '%s%s' % (sign, result)
