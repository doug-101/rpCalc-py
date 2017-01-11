#!/usr/bin/env python3

#****************************************************************************
# calcbutton.py, provides a smaller, text activated button
#
# rpCalc, an RPN calculator
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt5.QtCore import (QTimer, Qt, pyqtSignal)
from PyQt5.QtWidgets import (QPushButton, QSizePolicy)


class CalcButton(QPushButton):
    """Calculator button class - size change & emits clicked text signal.
    """
    activated = pyqtSignal(str)
    def __init__(self, text, parent=None):
        QPushButton.__init__(self, text, parent)
        self.setMinimumSize(38, 16)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
                                             QSizePolicy.Preferred))
        self.setFocusPolicy(Qt.NoFocus)
        self.clicked.connect(self.clickEvent)

    def clickEvent(self):
        """Emits signal with button text.
        """
        self.activated.emit(self.text())

    def sizeHint(self):
        """Set prefered size.
        """
        size = QPushButton.sizeHint(self)
        size.setWidth(size.width() // 2)
        return size

    def tmpDown(self, mSec):
        """Button shows pushed in for mSec milliseconds.
        """
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.timerUp)
        timer.start(mSec)
        self.setDown(True)

    def timerUp(self):
        """Button up at end of timer for tmpDown.
        """
        self.setDown(False)
