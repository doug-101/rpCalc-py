#!/usr/bin/env python3

#****************************************************************************
# calclcd.py, provides an LCD display
#
# rpCalc, an RPN calculator
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt5.QtCore import (QSize, Qt)
from PyQt5.QtWidgets import (QFrame, QLCDNumber)


class Lcd(QLCDNumber):
    """Main LCD Display.
    """
    def __init__(self, sizeFactor=1, numDigits=8, parent=None):
        QLCDNumber.__init__(self, numDigits, parent)
        self.sizeFactor = sizeFactor
        self.setSegmentStyle(QLCDNumber.Filled)
        self.setMinimumSize(10, 23)
        self.setFrameStyle(QFrame.NoFrame)

    def setDisplay(self, text, numDigits):
        """Update display value.
        """
        text = text.replace('e', ' E', 1)  # add space before exp
        if len(text) > numDigits:  # mark if digits hidden
            text = 'c{0}'.format(text[1-numDigits:])
        self.setNumDigits(numDigits)
        self.display(text)

    def sizeHint(self):
        """Set prefered size.
        """
        # default in Qt is 23 height & about 10 * numDigits
        size = QLCDNumber.sizeHint(self)
        return QSize(int(size.width() * self.sizeFactor),
                            int(size.height() * self.sizeFactor))


class LcdBox(QFrame):
    """Frame for LCD display.
    """
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setLineWidth(3)
 
    def mouseReleaseEvent(self, event):
        """Mouse release event for popup menus.
        """
        if event.button() == Qt.RightButton:
            popup = self.parentWidget().popupMenu
            popup.exec_(self.mapToGlobal(event.pos()))
            popup.clearFocus()
        QFrame.mouseReleaseEvent(self, event)
