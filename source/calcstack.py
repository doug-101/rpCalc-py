#!/usr/bin/env python3

#****************************************************************************
# calccore.py, provides storage and rotation for a stack of 4 numbers
#
# rpCalc, an RPN calculator
# Copyright (C) 2014, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************


class CalcStack(list):
    """Stores and rotates stack of 4 numbers.
    """
    def __init__(self, initList=None):
        if initList:
            list.__init__(self, initList)
        else:
            list.__init__(self, [0.0, 0.0, 0.0, 0.0])

    def replaceAll(self, numList):
        """Replace stack with numList.
        """
        self[:] = numList

    def replaceXY(self, num):
        """Replace X & Y registers with num, pulls stack.
        """
        del self[0]
        self[0] = num
        self.append(self[2])

    def enterX(self):
        """Push X onto stack into Y register.
        """
        self.insert(0, self[0])
        del self[4]

    def rollBack(self):
        """Roll stack so x = old y, etc..
        """
        num = self[0]
        del self[0]
        self.append(num)

    def rollUp(self):
        """Roll stack so x = old stack bottom.
        """
        num = self[3]
        del self[3]
        self.insert(0, num)
