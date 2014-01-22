#!/usr/bin/env python3

#****************************************************************************
# calcbutton.py, provides a smaller, text activated button
#
# rpCalc, an RPN calculator
# Copyright (C) 2014, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt4 import QtCore, QtGui


class CalcButton(QtGui.QPushButton):
    """Calculator button class - size change & emits clicked text signal.
    """
    activated = QtCore.pyqtSignal(str)
    def __init__(self, text, parent=None):
        QtGui.QPushButton.__init__(self, text, parent)
        self.setMinimumSize(38, 16)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                             QtGui.QSizePolicy.Preferred))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(self.clickEvent)

    def clickEvent(self):
        """Emits signal with button text.
        """
        self.activated.emit(self.text())

    def sizeHint(self):
        """Set prefered size.
        """
        size = QtGui.QPushButton.sizeHint(self)
        size.setWidth(size.width() // 2)
        return size

    def tmpDown(self, mSec):
        """Button shows pushed in for mSec milliseconds.
        """
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.timerUp)
        timer.start(mSec)
        self.setDown(True)

    def timerUp(self):
        """Button up at end of timer for tmpDown.
        """
        self.setDown(False)
