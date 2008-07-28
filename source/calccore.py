#!/usr/bin/env python

#****************************************************************************
# calccore.py, provides the non-GUI base classes
#
# rpCalc, an RPN calculator
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import math
import option
import optiondefaults
import calcstack

class Mode(object):
    """Enum for calculator modes"""
    entryMode = 100  # in num entry - adds to num string
    saveMode = 101   # after result - previous result becomes Y
    replMode = 102   # after enter key - replaces X
    expMode = 103    # in exponent entry - adds to exp string
    memStoMode = 104 # in memory register entry - needs 0-9 for num to store
    memRclMode = 105 # in memory register entry - needs 0-9 for num to recall
    decPlcMode = 106 # in decimal places entry - needs 0-9 for value
    errorMode = 107  # error notification - any cmd to resume


class CalcCore(object):
    """Reverse Polish calculator functionality"""
    minMaxHist = 10
    maxMaxHist = 10000
    def __init__(self):
        self.stack = calcstack.CalcStack()
        self.option = option.Option('rpcalc', 20)
        self.option.loadAll(optiondefaults.defaultList)
        self.restoreStack()
        self.xStr = ''
        self.updateXStr()
        self.flag = Mode.saveMode
        self.history = []
        self.histChg = 0

    def restoreStack(self):
        """Read stack from option file"""
        if self.option.boolData('SaveStacks'):
            self.stack.replaceAll([self.option.numData('Stack' + repr(x)) for
                                   x in range(4)])
            self.mem = [self.option.numData('Mem' + repr(x)) for x in
                        range(10)]
        else:
            self.mem = [0.0] * 10
        self.memChg = 0

    def saveStack(self):
        """Store stack to option file"""
        if self.option.boolData('SaveStacks'):
            [self.option.changeData('Stack' + repr(x), repr(self.stack[x]), 1)
             for x in range(4)]
            [self.option.changeData('Mem' + repr(x), repr(self.mem[x]), 1)
             for x in range(10)]
            self.option.writeChanges()

    def updateXStr(self):
        """get display string from X register"""
        if abs(self.stack[0]) > 1e299:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            self.stack[0] = 0.0
            if abs(self.stack[1]) > 1e299:
                self.stack.replaceXY(0.0)
        else:
            self.xStr = self.formatNum(self.stack[0])

    def formatNum(self, num):
        """Return number formatted per options"""
        absNum = abs(num)
        plcs = self.option.intData('NumDecimalPlaces', 0, 9)
        if (1e-4 <= absNum < 1e7 or absNum == 0) and not \
                 self.option.boolData('ForceSciNotation'):
            return ('% 0.' + repr(plcs) + 'f') % num
        return ('% 0.' + repr(plcs) + 'e') % num

    def sciFormatX(self, decPlcs):
        """Return X register str in sci notation"""
        return ('% 0.' + repr(decPlcs) + 'e') % self.stack[0]

    def newXValue(self, value):
        """Push X onto stack, replace with value"""
        self.stack.enterX()
        self.stack[0] = float(value)
        self.updateXStr()
        self.flag = Mode.saveMode
        
    def numEntry(self, entStr):
        """Interpret a digit entered depending on mode"""
        newStr = ' ' + entStr    # space for minus sign
        if self.flag in (Mode.entryMode, Mode.expMode):
            newStr = self.xStr + entStr
        elif self.flag == Mode.saveMode:
            self.stack.enterX()
        if newStr == ' .':
            newStr = ' 0.'
        try:
            num = float(newStr)
        except ValueError:
            return False
        self.stack[0] = num
        self.xStr = newStr
        if self.flag != Mode.expMode:
            self.flag = Mode.entryMode
        return True

    def expCmd(self):
        """Command to add an exponent"""
        if self.flag == Mode.expMode:
            return False
        if self.flag == Mode.entryMode:
            self.xStr = self.xStr + 'e+0'
        else:
            if self.flag == Mode.saveMode:
                self.stack.enterX()
            self.stack[0]= 1.0
            self.xStr = '1e+0'
        self.flag = Mode.expMode
        return True

    def bspCmd(self):
        """Backspace command"""
        if self.flag == Mode.entryMode and len(self.xStr) > 2:
            self.xStr = self.xStr[:-1]
        elif self.flag == Mode.expMode:
            numExp = self.xStr.split('e', 1)
            if len(numExp[1]) > 2:
                self.xStr = self.xStr[:-1]
            else:
                self.xStr = numExp[0]
                self.flag = Mode.entryMode
        else:
            self.stack[0] = 0.0
            self.updateXStr()
            self.flag = Mode.replMode
            return True
        self.stack[0] = float(self.xStr)
        return True

    def chsCmd(self):
        """Change sign command"""
        if self.flag == Mode.expMode:
            numExp = self.xStr.split('e', 1)
            if numExp[1][0] == '+':
                self.xStr = numExp[0] + 'e-' + numExp[1][1:]
            else:
                self.xStr = numExp[0] + 'e+' + numExp[1][1:]
        else:
            if self.xStr[0] == ' ':
                self.xStr = '-' + self.xStr[1:]
            else:
                self.xStr = ' ' + self.xStr[1:]
        self.stack[0] = float(self.xStr)
        return True

    def memStoRcl(self, numStr):
        """Handle memMode number entry for mem & dec plcs"""
        if len(numStr) == 1 and '0' <= numStr <= '9':
            num = int(numStr)
            if self.flag == Mode.memStoMode:
                self.mem[num] = self.stack[0]
                self.memChg = 1
            elif self.flag == Mode.memRclMode:
                self.stack.enterX()
                self.stack[0] = self.mem[num]
            else:        # decimal place mode
                self.option.changeData('NumDecimalPlaces', numStr, 1)
                self.option.writeChanges()
        elif numStr == '<-':         # backspace
            pass
        else:
            return False
        self.updateXStr()
        self.flag = Mode.saveMode
        return True

    def angleConv(self):
        """Return angular conversion factor from options"""
        type = self.option.strData('AngleUnit')
        if type == 'rad':
            return 1.0
        if type == 'grad':
            return math.pi / 200.0
        return math.pi / 180.0   # degree

    def cmd(self, cmdStr):
        """Main command interpreter - returns true/false if change made"""
        if self.flag in (Mode.memStoMode, Mode.memRclMode, Mode.decPlcMode):
            return self.memStoRcl(cmdStr)
        if self.flag == Mode.errorMode:    # reset display, ignore next command
            self.updateXStr()
            self.flag = Mode.saveMode
            return True
        eqn = ''
        try:
            if len(cmdStr) == 1:
                if '0' <= cmdStr <= '9' or cmdStr == '.':
                    return self.numEntry(cmdStr)
                if cmdStr in '+-*/':
                    eqn = '%s %s %s' % (self.formatNum(self.stack[1]), cmdStr,
                                        self.formatNum(self.stack[0]))
                    if cmdStr == '+':
                        self.stack.replaceXY(self.stack[1] + self.stack[0])
                    elif cmdStr == '-':
                        self.stack.replaceXY(self.stack[1] - self.stack[0])
                    elif cmdStr == '*':
                        self.stack.replaceXY(self.stack[1] * self.stack[0])
                    elif cmdStr == '/':
                        self.stack.replaceXY(self.stack[1] / self.stack[0])
                else:
                    return False
            elif cmdStr == 'ENT':          # enter
                self.stack.enterX()
                self.flag = Mode.replMode
                self.updateXStr()
                return True
            elif cmdStr == 'EXP':
                return self.expCmd()
            elif cmdStr == 'X<>Y':         # exchange
                self.stack[0], self.stack[1] = self.stack[1], self.stack[0]
            elif cmdStr == 'CHS':          # change sign
                return self.chsCmd()
            elif cmdStr == 'CLR':          # clear
                self.stack.replaceAll([0.0, 0.0, 0.0, 0.0])
            elif cmdStr == '<-':           # backspace
                return self.bspCmd()
            elif cmdStr == 'STO':          # store to memory
                self.flag = Mode.memStoMode
                self.xStr = '0-9:'
                return True
            elif cmdStr == 'RCL':          # recall from memory
                self.flag = Mode.memRclMode
                self.xStr = '0-9:'
                return True
            elif cmdStr == 'PLCS':         # change dec plc setting
                self.flag = Mode.decPlcMode
                self.xStr = '0-9:'
                return True
            elif cmdStr == 'SCI':          # toggle fix/sci setting
                orig = self.option.boolData('ForceSciNotation')
                new = orig and 'no' or 'yes'
                self.option.changeData('ForceSciNotation', new, 1)
                self.option.writeChanges
            elif cmdStr == 'DEG':           # change deg/rad setting
                orig = self.option.strData('AngleUnit')
                new = orig == 'deg' and 'rad' or 'deg'
                self.option.changeData('AngleUnit', new, 1)
                self.option.writeChanges()
            elif cmdStr == 'R<':           # roll stack back
                self.stack.rollBack()
            elif cmdStr == 'R>':           # roll stack forward
                self.stack.rollUp()
            elif cmdStr == 'PI':           # pi constant
                self.stack.enterX()
                self.stack[0] = math.pi
            elif cmdStr == 'X^2':          # square
                eqn = '(%s)^2' % self.formatNum(self.stack[0])
                self.stack[0] = self.stack[0] * self.stack[0]
            elif cmdStr == 'Y^X':          # x power of y
                eqn = '(%s)^%s' % (self.formatNum(self.stack[1]),
                                   self.formatNum(self.stack[0]))
                self.stack.replaceXY(self.stack[1] ** self.stack[0])
            elif cmdStr == 'XRT':          # x root of y
                eqn = '(%s)^(1/%s)' % (self.formatNum(self.stack[1]),
                                       self.formatNum(self.stack[0]))
                self.stack.replaceXY(self.stack[1] ** (1.0/self.stack[0]))
            elif cmdStr == 'RCIP':         # 1/x
                eqn = '1 / (%s)' % self.formatNum(self.stack[0])
                self.stack[0] = 1.0 / self.stack[0]
            elif cmdStr == 'E^X':          # inverse natural log
                eqn = 'e^(%s)' % self.formatNum(self.stack[0])
                self.stack[0] = math.exp(self.stack[0])
            elif cmdStr == 'TN^X':         # inverse base 10 log
                eqn = '10^(%s)' % self.formatNum(self.stack[0])
                self.stack[0] = 10.0 ** self.stack[0]
            else:
                eqn = '%s(%s)' % (cmdStr, self.formatNum(self.stack[0]))
                if cmdStr == 'SQRT':         # square root
                    self.stack[0] = math.sqrt(self.stack[0])
                elif cmdStr == 'SIN':          # sine
                    self.stack[0] = math.sin(self.stack[0] *
                                             self.angleConv())
                elif cmdStr == 'COS':          # cosine
                    self.stack[0] = math.cos(self.stack[0] *
                                             self.angleConv())
                elif cmdStr == 'TAN':          # tangent
                    self.stack[0] = math.tan(self.stack[0] *
                                             self.angleConv())
                elif cmdStr == 'LN':           # natural log
                    self.stack[0] = math.log(self.stack[0])
                elif cmdStr == 'ASIN':         # arcsine
                    self.stack[0] = math.asin(self.stack[0]) \
                                    / self.angleConv()
                elif cmdStr == 'ACOS':         # arccosine
                    self.stack[0] = math.acos(self.stack[0]) \
                                    / self.angleConv()
                elif cmdStr == 'ATAN':         # arctangent
                    self.stack[0] = math.atan(self.stack[0]) \
                                    / self.angleConv()
                elif cmdStr == 'LOG':          # base 10 log
                    self.stack[0] = math.log10(self.stack[0])
                else:     
                    return False
            self.flag = Mode.saveMode
            self.updateXStr()
            if eqn:
                self.history.append((eqn, self.stack[0]))
                self.histChg += 1
                maxLen = self.option.intData('MaxHistLength',
                                             CalcCore.minMaxHist,
                                             CalcCore.maxMaxHist)
                while len(self.history) > maxLen:
                    del self.history[0]
            return True
        except (ValueError, ZeroDivisionError):
            self.xStr = 'error 0'
            self.flag = Mode.errorMode
            return True
        except OverflowError:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            return True

    def printDebug(self):
        """Print display string and all registers for debug"""
        print 'x =', self.xStr
        print '\n'.join([repr(num) for num in self.stack])


if __name__ == '__main__':
    calc = CalcCore()
    calc.printDebug()
    while 1:
        ans = raw_input('Entry->')
        if ans in ('ENT', 'X<>Y', 'CHS', 'CLR', '<-', 'X^2', 'SQRT', 'Y^X',
                   'XRT', 'RCIP', 'SIN', 'COS', 'TAN', 'LN', 'E^X', 'ASIN',
                   'ACOS', 'ATAN', 'LOG', 'TN^X', 'STO', 'RCL', 'R<', 'R>',
                   'PI'):
            calc.cmd(ans)
            calc.printDebug()
        else:
            for ch in ans:
                if ch == 'e':
                    ch = 'ENT'
                calc.cmd(ch)
                calc.printDebug()
