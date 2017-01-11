#!/usr/bin/env python3

#****************************************************************************
# altbasedialog.py, provides a dialog box for other bases (binary, octal, hex
#
# rpCalc, an RPN calculator
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)
import calccore

class AltBaseDialog(QWidget):
    """Displays edit boxes for other number bases.
    """
    baseCode = {'X':16, 'O':8, 'B':2, 'D':10}
    def __init__(self, dlgRef, parent=None):
        QWidget.__init__(self, parent)
        self.dlgRef = dlgRef
        self.prevBase = None   # revert to prevBase after temp base change
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowTitle('rpCalc Alternate Bases')
        topLay = QVBoxLayout(self)
        self.setLayout(topLay)
        mainLay = QGridLayout()
        topLay.addLayout(mainLay)
        self.buttons = QButtonGroup(self)
        self.baseBoxes = {}
        hexButton = QPushButton('He&x')
        self.buttons.addButton(hexButton, 16)
        mainLay.addWidget(hexButton, 0, 0, Qt.AlignRight)
        self.baseBoxes[16] = AltBaseBox(16, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[16], 0, 1)
        octalButton = QPushButton('&Octal')
        self.buttons.addButton(octalButton, 8)
        mainLay.addWidget(octalButton, 1, 0, Qt.AlignRight)
        self.baseBoxes[8] = AltBaseBox(8, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[8], 1, 1)
        binaryButton = QPushButton('&Binary')
        self.buttons.addButton(binaryButton, 2)
        mainLay.addWidget(binaryButton, 2, 0, Qt.AlignRight)
        self.baseBoxes[2] = AltBaseBox(2, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[2], 2, 1)
        decimalButton = QPushButton('&Decimal')
        self.buttons.addButton(decimalButton, 10)
        mainLay.addWidget(decimalButton, 3, 0, Qt.AlignRight)
        self.baseBoxes[10] = AltBaseBox(10, self.dlgRef.calc)
        mainLay.addWidget(self.baseBoxes[10], 3, 1)
        for button in self.buttons.buttons():
            button.setCheckable(True)
        self.buttons.buttonClicked[int].connect(self.changeBase)
        self.bitsLabel = QLabel()
        self.bitsLabel.setAlignment(Qt.AlignHCenter)
        self.bitsLabel.setFrameStyle(QFrame.Box | QFrame.Plain)
        topLay.addSpacing(3)
        topLay.addWidget(self.bitsLabel)
        topLay.addSpacing(3)
        buttonLay = QHBoxLayout()
        topLay.addLayout(buttonLay)
        copyButton = QPushButton('Copy &Value')
        buttonLay.addWidget(copyButton)
        copyButton.clicked.connect(self.copyValue)
        closeButton = QPushButton('&Close')
        buttonLay.addWidget(closeButton)
        closeButton.clicked.connect(self.close)
        self.changeBase(self.dlgRef.calc.base, False)
        self.updateOptions()
        option = self.dlgRef.calc.option
        self.move(option.intData('AltBaseXPos', 0, 10000),
                  option.intData('AltBaseYPos', 0, 10000))

    def updateData(self):
        """Update edit box contents for current registers.
        """
        if self.prevBase and self.dlgRef.calc.flag != calccore.Mode.entryMode:
            self.changeBase(self.prevBase, False)
            self.prevBase = None
        for box in self.baseBoxes.values():
            box.setValue(self.dlgRef.calc.stack[0])

    def changeBase(self, base, endEntryMode=True):
        """Change core's base, button depression and label highlighting.
        """
        self.baseBoxes[self.dlgRef.calc.base].setHighlight(False)
        self.baseBoxes[base].setHighlight(True)
        self.buttons.button(base).setChecked(True)
        if endEntryMode and self.dlgRef.calc.base != base and \
                self.dlgRef.calc.flag == calccore.Mode.entryMode:
            self.dlgRef.calc.flag = calccore.Mode.saveMode
        self.dlgRef.calc.base = base

    def setCodedBase(self, baseCode, temp=True):
        """Set new base from letter code, temporarily if temp is true.
        """
        if temp:
            self.prevBase = self.dlgRef.calc.base
        else:
            self.prevBase = None
        try:
            self.changeBase(AltBaseDialog.baseCode[baseCode], not temp)
        except KeyError:
            pass

    def updateOptions(self):
        """Update bit limit and two's complement use.
        """
        self.dlgRef.calc.setAltBaseOptions()
        if self.dlgRef.calc.useTwosComplement:
            text = '{0} bit, two\'s complement'.format(self.dlgRef.calc.
                                                       numBits)
        else:
            text = '{0} bit, no two\'s complement'.format(self.dlgRef.calc.
                                                          numBits)
        self.bitsLabel.setText(text)

    def copyValue(self):
        """Copy the value in the current base to the clipboard.
        """
        text = str(self.baseBoxes[self.dlgRef.calc.base].text())
        clip = QApplication.clipboard()
        if clip.supportsSelection():
            clip.setText(text, QClipboard.Selection)
        clip.setText(text)

    def keyPressEvent(self, keyEvent):
        """Pass all keypresses to main dialog.
        """
        self.dlgRef.keyPressEvent(keyEvent)

    def keyReleaseEvent(self, keyEvent):
        """Pass all key releases to main dialog.
        """
        self.dlgRef.keyReleaseEvent(keyEvent)

    def closeEvent(self, closeEvent):
        """Change back to base 10 before closing.
        """
        self.changeBase(10)
        QWidget.closeEvent(self, closeEvent)


class AltBaseBox(QLabel):
    """Displays an edit box at a particular base.
    """
    def __init__(self, base, calcRef, parent=None):
        QLabel.__init__(self, parent)
        self.base = base
        self.calcRef = calcRef
        self.setHighlight(False)
        self.setLineWidth(3)
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Minimum)

    def setValue(self, num):
        """Set value to num in proper base.
        """
        self.setText(self.calcRef.numberStr(num, self.base))

    def setHighlight(self, turnOn=True):
        """Make border bolder if turnOn is true, restore if false.
        """
        if turnOn:
            style = QFrame.Panel | QFrame.Plain
        else:
            style = QFrame.Panel | QFrame.Sunken
        self.setFrameStyle(style)
