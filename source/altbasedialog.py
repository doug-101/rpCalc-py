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
        topLay = QtGui.QVBoxLayout(self)
        self.setLayout(topLay)
        mainLay = QtGui.QGridLayout()
        topLay.addLayout(mainLay)
        mainLay.addWidget(QtGui.QLabel('Hex'), 0, 0,
                          QtCore.Qt.AlignRight)
        self.editBoxes = []
        self.editBoxes.append(AltBaseEdit(16))
        mainLay.addWidget(self.editBoxes[-1], 0, 1)
        mainLay.addWidget(QtGui.QLabel('Octal'), 1, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(8))
        mainLay.addWidget(self.editBoxes[-1], 1, 1)
        mainLay.addWidget(QtGui.QLabel('Binary'), 2, 0, QtCore.Qt.AlignRight)
        self.editBoxes.append(AltBaseEdit(2))
        mainLay.addWidget(self.editBoxes[-1], 2, 1)
        closeButton = QtGui.QPushButton('Close')
        topLay.addWidget(closeButton)
        self.connect(closeButton, QtCore.SIGNAL('clicked()'), self.close)

    def updateData(self):
        """Update edit box contents for current registers"""
        for box in self.editBoxes:
            box.setValue(self.dlgRef.calc.stack[0])


class AltBaseEdit(QtGui.QLineEdit):
    """Displays an edit box at a particular base"""
    def __init__(self, base, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.base = base

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
