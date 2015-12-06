#!/usr/bin/env python3
"""
****************************************************************************
 rpcalc.py, the main program file

 rpCalc, an RPN calculator
 Copyright (C) 2015, Douglas W. Bell

 This is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License, either Version 2 or any later
 version.  This program is distributed in the hope that it will be useful,
 but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
*****************************************************************************
"""

__progname__ = 'rpCalc'
__version__ = '0.7.1'
__author__ = 'Doug Bell'

helpFilePath = None    # modified by install script if required
iconPath = None        # modified by install script if required

import sys
from PyQt4 import QtGui
import calcdlg


if __name__ == '__main__':
    userStyle = '-style' in ' '.join(sys.argv)
    app = QtGui.QApplication(sys.argv)
    if not userStyle and not sys.platform.startswith('win'):
        QtGui.QApplication.setStyle('plastique')
    win = calcdlg.CalcDlg()
    win.show()
    app.exec_()
