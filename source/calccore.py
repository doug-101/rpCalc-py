#!/usr/bin/env python3

#****************************************************************************
# calccore.py, provides the non-GUI base classes
#
# rpCalc, an RPN calculator
# Copyright (C) 2014, Douglas W. Bell
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

class Mode:
    """Enum for calculator modes.
    """
    entryMode = 100  # in num entry - adds to num string
    saveMode = 101   # after result - previous result becomes Y
    replMode = 102   # after enter key - replaces X
    expMode = 103    # in exponent entry - adds to exp string
    memStoMode = 104 # in memory register entry - needs 0-9 for num to store
    memRclMode = 105 # in memory register entry - needs 0-9 for num to recall
    decPlcMode = 106 # in decimal places entry - needs 0-9 for value
    errorMode = 107  # error notification - any cmd to resume


class CalcCore:
    """Reverse Polish calculator functionality.
    """
    minMaxHist = 10
    maxMaxHist = 10000
    minNumBits = 4
    maxNumBits = 128
    def __init__(self):
        self.stack = calcstack.CalcStack()
        self.option = option.Option('rpcalc', 20)
        self.option.loadAll(optiondefaults.defaultList)
        self.restoreStack()
        self.xStr = ''
        self.updateXStr()
        self.flag = Mode.saveMode
        self.base = 10
        self.numBits = 0
        self.useTwosComplement = False
        self.history = []
        self.histChg = 0
        self.setAltBaseOptions()

    def setAltBaseOptions(self):
        """Update bit limit and two's complement use.
        """
        self.numBits = self.option.intData('AltBaseBits', CalcCore.minNumBits,
                                           CalcCore.maxNumBits)
        if not self.numBits:
            self.numBits = CalcCore.maxNumBits
        self.useTwosComplement = self.option.boolData('UseTwosComplement')

    def restoreStack(self):
        """Read stack from option file.
        """
        if self.option.boolData('SaveStacks'):
            self.stack.replaceAll([self.option.numData('Stack' + repr(x)) for
                                   x in range(4)])
            self.mem = [self.option.numData('Mem' + repr(x)) for x in
                        range(10)]
        else:
            self.mem = [0.0] * 10

    def saveStack(self):
        """Store stack to option file.
        """
        if self.option.boolData('SaveStacks'):
            [self.option.changeData('Stack' + repr(x), repr(self.stack[x]), 1)
             for x in range(4)]
            [self.option.changeData('Mem' + repr(x), repr(self.mem[x]), 1)
             for x in range(10)]
            self.option.writeChanges()

    def updateXStr(self):
        """get display string from X register.
        """
        if abs(self.stack[0]) > 1e299:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            self.stack[0] = 0.0
            if abs(self.stack[1]) > 1e299:
                self.stack.replaceXY(0.0)
        else:
            self.xStr = self.formatNum(self.stack[0])

    def formatNum(self, num):
        """Return number formatted per options.
        """
        absNum = abs(num)
        plcs = self.option.intData('NumDecimalPlaces', 0, 9)
        forceSci = self.option.boolData('ForceSciNotation')
        useEng = self.option.boolData('UseEngNotation')
        exp = 0
        if absNum != 0.0 and (absNum < 1e-4 or absNum >= 1e7 or forceSci
                              or useEng):
            exp = int(math.floor(math.log10(absNum)))
            if useEng:
                exp = 3 * (exp // 3)
            num /= 10**exp
            num = round(num, plcs)  # check if rounding bumps exponent
            if useEng and abs(num) >= 1000.0:
                num /= 1000.0
                exp += 3
            elif not useEng and abs(num) >= 10.0:
                num /= 10.0
                exp += 1
        numStr = '{: 0.{pl}f}'.format(num, pl=plcs)
        if self.option.boolData('ThousandsSeparator'):
            numStr = self.addThousandsSep(numStr)
        if exp != 0 or forceSci:
            expDigits = 4
            if self.option.boolData('TrimExponents'):
                expDigits = 1
            numStr = '{0}e{1:+0{pl}d}'.format(numStr, exp, pl=expDigits)
        return numStr

    def addThousandsSep(self, numStr):
        """Return number string with thousands separators added.
        """
        leadChar = ''
        if numStr[0] < '0' or numStr[0] > '9':
            leadChar = numStr[0]
            numStr = numStr[1:]
        numStr = numStr.replace(' ', '')
        decPos = numStr.find('.')
        if decPos < 0:
            decPos = len(numStr)
        for i in range(decPos - 3, 0, -3):
            numStr = numStr[:i] + ' ' + numStr[i:]
        return leadChar + numStr

    def sciFormatX(self, decPlcs):
        """Return X register str in sci notation.
        """
        return '{: 0.{pl}e}'.format(self.stack[0], pl=decPlcs)

    def newXValue(self, value):
        """Push X onto stack, replace with value.
        """
        self.stack.enterX()
        self.stack[0] = float(value)
        self.updateXStr()
        self.flag = Mode.saveMode
        
    def numEntry(self, entStr):
        """Interpret a digit entered depending on mode.
        """
        if self.flag == Mode.saveMode:
            self.stack.enterX()
        if self.flag in (Mode.entryMode, Mode.expMode):
            if self.base == 10:
                newStr = self.xStr + entStr
            else:
                newStr = self.numberStr(self.stack[0], self.base) + entStr
        else:
            newStr = ' ' + entStr    # space for minus sign
            if newStr == ' .':
                newStr = ' 0.'
        try:
            num = self.convertNum(newStr)
        except ValueError:
            return False
        if self.base != 10:
            newStr = self.formatNum(num)    # decimal num in main display
        self.stack[0] = num
        if self.option.boolData('ThousandsSeparator'):
            newStr = self.addThousandsSep(newStr)
        self.xStr = newStr
        if self.flag != Mode.expMode:
            self.flag = Mode.entryMode
        return True

    def numberStr(self, number, base):
        """Return string of number in given base (2-16).
        """
        digits = '0123456789abcdef'
        number = int(round(number))
        result = ''
        sign = ''
        if number == 0:
            return '0'
        if self.useTwosComplement:
            if number >= 2**(self.numBits - 1) or \
                    number < -2**(self.numBits - 1):
                return 'overflow'
            if number < 0:
                number = 2**self.numBits + number
        else:
            if number < 0:
                number = abs(number)
                sign = '-'
            if number >= 2**self.numBits:
                return 'overflow'
        while number:
            number, remainder = divmod(number, base)
            result = '{0}{1}'.format(digits[remainder], result)
        return '{0}{1}'.format(sign, result)

    def convertNum(self, numStr):
        """Convert number string to float using current base.
        """
        numStr = numStr.replace(' ', '')
        if self.base == 10:
            return float(numStr)
        num = float(int(numStr, self.base))
        if num >= 2**self.numBits:
            self.xStr = 'error 9'
            self.flag = Mode.errorMode
            self.stack[0] = num
            raise ValueError
        if self.useTwosComplement and num >= 2**(self.numBits - 1):
            num = num - 2**self.numBits
        return num

    def expCmd(self):
        """Command to add an exponent.
        """
        if self.flag == Mode.expMode or self.base != 10:
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
        """Backspace command.
        """
        if self.base != 10 and self.flag == Mode.entryMode:
            self.xStr = self.numberStr(self.stack[0], self.base)
            if self.xStr[0] != '-':
                self.xStr = ' ' + self.xStr
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
        self.stack[0] = self.convertNum(self.xStr)
        if self.base != 10:
            self.xStr = self.formatNum(self.stack[0])
        if self.option.boolData('ThousandsSeparator'):
            self.xStr = self.addThousandsSep(self.xStr)
        return True

    def chsCmd(self):
        """Change sign command.
        """
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
        self.stack[0] = float(self.xStr.replace(' ', ''))
        return True

    def memStoRcl(self, numStr):
        """Handle memMode number entry for mem & dec plcs.
        """
        if len(numStr) == 1 and '0' <= numStr <= '9':
            num = int(numStr)
            if self.flag == Mode.memStoMode:
                self.mem[num] = self.stack[0]
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
        """Return angular conversion factor from options.
        """
        type = self.option.strData('AngleUnit')
        if type == 'rad':
            return 1.0
        if type == 'grad':
            return math.pi / 200
        return math.pi / 180   # degree

    def cmd(self, cmdStr):
        """Main command interpreter - returns true/false if change made.
        """
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
                if self.base == 16 and 'A' <= cmdStr <= 'F':
                    return self.numEntry(cmdStr)
                if cmdStr in '+-*/':
                    eqn = '{0} {1} {2}'.format(self.formatNum(self.stack[1]),
                                               cmdStr,
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
                eqn = '{0}^2'.format(self.formatNum(self.stack[0]))
                self.stack[0] = self.stack[0] * self.stack[0]
            elif cmdStr == 'Y^X':          # x power of y
                eqn = '({0})^{1}'.format(self.formatNum(self.stack[1]),
                                         self.formatNum(self.stack[0]))
                self.stack.replaceXY(self.stack[1] ** self.stack[0])
            elif cmdStr == 'XRT':          # x root of y
                eqn = '({0})^(1/{1})'.format(self.formatNum(self.stack[1]),
                                             self.formatNum(self.stack[0]))
                self.stack.replaceXY(self.stack[1] ** (1/self.stack[0]))
            elif cmdStr == 'RCIP':         # 1/x
                eqn = '1 / ({0})'.format(self.formatNum(self.stack[0]))
                self.stack[0] = 1 / self.stack[0]
            elif cmdStr == 'E^X':          # inverse natural log
                eqn = 'e^({0})'.format(self.formatNum(self.stack[0]))
                self.stack[0] = math.exp(self.stack[0])
            elif cmdStr == 'TN^X':         # inverse base 10 log
                eqn = '10^({0})'.format(self.formatNum(self.stack[0]))
                self.stack[0] = 10.0 ** self.stack[0]
            else:
                eqn = '{0}({1})'.format(cmdStr, self.formatNum(self.stack[0]))
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
        """Print display string and all registers for debug.
        """
        print('x =', self.xStr)
        print('\n'.join([repr(num) for num in self.stack]))


if __name__ == '__main__':
    calc = CalcCore()
    calc.printDebug()
    while 1:
        ans = input('Entry->')
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
