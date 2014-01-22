#!/usr/bin/env python3

#****************************************************************************
# icons.py, provides xpm icons
#
# rpCalc, an RPN calculator
# Copyright (C) 2014, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import sys
from PyQt4 import QtCore, QtGui


calc = [
    "16 16 4 1",
    "       c None",
    ".      c #0B442A",
    "+      c #5CE0A0",
    "@      c #8DA3C9",
    "                ",
    " .........      ",
    "...........     ",
    "..+++++++..     ",
    " ..+++++++..    ",
    " ...........    ",
    "  .@@.@@.@@..   ",
    "  ...........   ",
    "   .@@.@@.@@..  ",
    "   ...........  ",
    "    .@@.@@.@@.. ",
    "    ........... ",
    "     .@@.@@.@@..",
    "     ...........",
    "      ......... ",
    "                "]

helpback = [
    "16 14 2 1",
    "       c None",
    "+      c #0000A0",
    "                ",
    "     ++         ",
    "    ++          ",
    "   ++           ",
    "  ++            ",
    " ++             ",
    "++++++++++++++  ",
    "++++++++++++++  ",
    " ++             ",
    "  ++            ",
    "   ++           ",
    "    ++          ",
    "     ++         ",
    "                "]

helpforward = [
    "16 14 2 1",
    "       c None",
    "+      c #0000A0",
    "                ",
    "         ++     ",
    "          ++    ",
    "           ++   ",
    "            ++  ",
    "             ++ ",
    "  ++++++++++++++",
    "  ++++++++++++++",
    "             ++ ",
    "            ++  ",
    "           ++   ",
    "          ++    ",
    "         ++     ",
    "                "]

helphome = [
    "16 14 2 1",
    "       c None",
    "+      c #0000A0",
    "       ++       ",
    "      ++++      ",
    "     ++  ++     ",
    "    ++    ++    ",
    "   ++      ++   ",
    "  ++        ++  ",
    " ++          ++ ",
    " ++          ++ ",
    " ++          ++ ",
    " ++          ++ ",
    " ++          ++ ",
    " ++          ++ ",
    " ++++++++++++++ ",
    " ++++++++++++++ "]

iconList = ['calc', 'helpback', 'helpforward', 'helphome']
iconDict = {}

def setupIcons():
    """Create icons from xpm data.
        """
    global iconDict
    for name in iconList:
        iconDict[name] = QtGui.QIcon(QtGui.QPixmap(globals()[name]))
