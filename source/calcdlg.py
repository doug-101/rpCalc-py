#!/usr/bin/env python3

#****************************************************************************
# calcdlg.py, the main dialog view
#
# rpCalc, an RPN calculator
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import sys
import os.path
from PyQt5.QtCore import (QPoint, QTimer, Qt)
from PyQt5.QtGui import (QColor, QPalette)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
                             QHBoxLayout, QLCDNumber, QLabel, QMenu,
                             QMessageBox, QSizePolicy, QVBoxLayout, QWidget,
                             qApp)
try:
    from __main__ import __version__, __author__, helpFilePath, iconPath
except ImportError:
    __version__ = __author__ = '??'
    helpFilePath = None
    iconPath = None
from calccore import CalcCore, Mode
from calclcd import Lcd, LcdBox
from calcbutton import CalcButton
import extradisplay
import altbasedialog
import optiondlg
import icondict
import helpview


class CalcDlg(QWidget):
    """Main dialog for calculator program.
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.calc = CalcCore()
        self.setWindowTitle('rpCalc')
        modPath = os.path.abspath(sys.path[0])
        if modPath.endswith('.zip') or modPath.endswith('.exe'):
            modPath = os.path.dirname(modPath)  # for py2exe/cx_freeze
        iconPathList = [iconPath, os.path.join(modPath, 'icons/'),
                         os.path.join(modPath, '../icons')]
        self.icons = icondict.IconDict()
        self.icons.addIconPath(filter(None, iconPathList))
        self.icons.addIconPath([path for path in iconPathList if path])
        try:
            QApplication.setWindowIcon(self.icons['calc_lg'])
        except KeyError:
            pass
        self.setFocusPolicy(Qt.StrongFocus)
        self.helpView = None
        self.extraView = None
        self.regView = None
        self.histView = None
        self.memView = None
        self.altBaseView = None
        self.optDlg = None
        self.popupMenu = QMenu(self)
        self.popupMenu.addAction('Registers on &LCD', self.toggleReg)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('Show &Register List', self.viewReg)
        self.popupMenu.addAction('Show &History List', self.viewHist)
        self.popupMenu.addAction('Show &Memory List', self.viewMem)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('Show Other &Bases', self.viewAltBases)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('Show Help &File', self.help)
        self.popupMenu.addAction('&About rpCalc', self.about)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction('&Quit', self.close)
        topLay = QVBoxLayout(self)
        self.setLayout(topLay)
        topLay.setSpacing(4)
        topLay.setContentsMargins(6, 6, 6, 6)
        lcdBox = LcdBox()
        topLay.addWidget(lcdBox)
        lcdLay = QGridLayout(lcdBox)
        lcdLay.setColumnStretch(1, 1)
        lcdLay.setRowStretch(3, 1)
        self.extraLabels = [QLabel(' T:',), QLabel(' Z:',),
                            QLabel(' Y:',)]
        for i in range(3):
            lcdLay.addWidget(self.extraLabels[i], i, 0, Qt.AlignLeft)
        self.extraLcds = [Lcd(1.5, 13), Lcd(1.5, 13), Lcd(1.5, 13)]
        lcdLay.addWidget(self.extraLcds[2], 0, 1, Qt.AlignRight)
        lcdLay.addWidget(self.extraLcds[1], 1, 1, Qt.AlignRight)
        lcdLay.addWidget(self.extraLcds[0], 2, 1, Qt.AlignRight)
        if not self.calc.option.boolData('ViewRegisters'):
            for w in self.extraLabels + self.extraLcds:
                w.hide()
        self.lcd = Lcd(2.0, 13)
        lcdLay.addWidget(self.lcd, 3, 0, 1, 2, Qt.AlignRight)
        self.setLcdHighlight()
        self.updateLcd()
        self.updateColors()

        self.cmdLay = QGridLayout()
        topLay.addLayout(self.cmdLay)
        self.cmdDict = {}
        self.addCmdButton('x^2', 0, 0)
        self.addCmdButton('sqRT', 0, 1)
        self.addCmdButton('y^X', 0, 2)
        self.addCmdButton('xRT', 0, 3)
        self.addCmdButton('RCIP', 0, 4)
        self.addCmdButton('SIN', 1, 0)
        self.addCmdButton('COS', 1, 1)
        self.addCmdButton('TAN', 1, 2)
        self.addCmdButton('LN', 1, 3)
        self.addCmdButton('e^X', 1, 4)
        self.addCmdButton('ASIN', 2, 0)
        self.addCmdButton('ACOS', 2, 1)
        self.addCmdButton('ATAN', 2, 2)
        self.addCmdButton('LOG', 2, 3)
        self.addCmdButton('tn^X', 2, 4)
        self.addCmdButton('STO', 3, 0)
        self.addCmdButton('RCL', 3, 1)
        self.addCmdButton('R<', 3, 2)
        self.addCmdButton('R>', 3, 3)
        self.addCmdButton('x<>y', 3, 4)
        self.addCmdButton('SHOW', 4, 0)
        self.addCmdButton('CLR', 4, 1)
        self.addCmdButton('PLCS', 4, 2)
        self.addCmdButton('SCI', 4, 3)
        self.addCmdButton('DEG', 4, 4)
        self.addCmdButton('EXIT', 5, 0)
        self.addCmdButton('Pi', 5, 1)
        self.addCmdButton('EXP', 5, 2)
        self.addCmdButton('CHS', 5, 3)
        self.addCmdButton('<-', 5, 4)

        self.mainLay = QGridLayout()
        topLay.addLayout(self.mainLay)
        self.mainDict = {}
        self.addMainButton(0, 'OPT', 0, 0)
        self.addMainButton(Qt.Key_Slash, '/', 0, 1)
        self.addMainButton(Qt.Key_Asterisk, '*', 0, 2)
        self.addMainButton(Qt.Key_Minus, '-', 0, 3)
        self.addMainButton(Qt.Key_7, '7', 1, 0)
        self.addMainButton(Qt.Key_8, '8', 1, 1)
        self.addMainButton(Qt.Key_9, '9', 1, 2)
        self.addMainButton(Qt.Key_Plus, '+', 1, 3, 1, 0)
        self.addMainButton(Qt.Key_4, '4', 2, 0)
        self.addMainButton(Qt.Key_5, '5', 2, 1)
        self.addMainButton(Qt.Key_6, '6', 2, 2)
        self.addMainButton(Qt.Key_1, '1', 3, 0)
        self.addMainButton(Qt.Key_2, '2', 3, 1)
        self.addMainButton(Qt.Key_3, '3', 3, 2)
        self.addMainButton(Qt.Key_Enter, 'ENT', 3, 3, 1, 0)
        self.addMainButton(Qt.Key_0, '0', 4, 0, 0, 1)
        self.addMainButton(Qt.Key_Period, '.', 4, 2)

        self.mainDict[Qt.Key_Return] = \
                     self.mainDict[Qt.Key_Enter]
        # added for european keyboards:
        self.mainDict[Qt.Key_Comma] = \
                     self.mainDict[Qt.Key_Period]
        self.cmdDict['ENT'] = self.mainDict[Qt.Key_Enter]
        self.cmdDict['OPT'] = self.mainDict[0]

        self.entryStr = ''
        self.showMode = False

        statusBox = QFrame()
        statusBox.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        statusBox.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
                                                  QSizePolicy.Preferred))
        topLay.addWidget(statusBox)
        statusLay = QHBoxLayout(statusBox)
        self.entryLabel = QLabel(statusBox)
        statusLay.addWidget(self.entryLabel)
        statusLay.setContentsMargins(1, 1, 1, 1)
        self.statusLabel = QLabel(statusBox)
        self.statusLabel.setAlignment(Qt.AlignRight)
        statusLay.addWidget(self.statusLabel)

        if self.calc.option.boolData('ExtraViewStartup'):
            self.viewReg()
        if self.calc.option.boolData('AltBaseStartup'):
            self.viewAltBases()

        xSize = self.calc.option.intData('MainDlgXSize', 0, 10000)
        ySize = self.calc.option.intData('MainDlgYSize', 0, 10000)
        if xSize and ySize:
            self.resize(xSize, ySize)
        self.move(self.calc.option.intData('MainDlgXPos', 0, 10000),
                  self.calc.option.intData('MainDlgYPos', 0, 10000))

        self.updateEntryLabel('rpCalc Version {0}'.format(__version__))
        QTimer.singleShot(5000, self.updateEntryLabel)

    def updateEntryLabel(self, subsText=''):
        """Set entry & status label text, use entryStr or subsText, options.
        """
        numFormat = self.calc.option.boolData('ForceSciNotation') and 'sci' \
                    or 'fix'
        decPlcs = self.calc.option.intData('NumDecimalPlaces', 0, 9)
        angle = self.calc.option.strData('AngleUnit')
        self.statusLabel.setText('{0} {1}  {2}'.format(numFormat, decPlcs,
                                                       angle))
        self.entryLabel.setText(subsText or '> {0}'.format(self.entryStr))

    def setOptions(self):
        """Starts option dialog, called by option key.
        """
        oldViewReg = self.calc.option.boolData('ViewRegisters')
        self.optDlg = optiondlg.OptionDlg(self.calc.option, self)
        self.optDlg.startGroupBox('Startup', 8)
        optiondlg.OptionDlgBool(self.optDlg, 'SaveStacks',
                                'Save previous entries')
        optiondlg.OptionDlgBool(self.optDlg, 'ExtraViewStartup',
                                'Auto open extra data view')
        optiondlg.OptionDlgBool(self.optDlg, 'AltBaseStartup',
                                'Auto open alternate base view')
        self.optDlg.startGroupBox('Display', 8)
        optiondlg.OptionDlgInt(self.optDlg, 'NumDecimalPlaces',
                               'Number of decimal places', 0, 9)
        optiondlg.OptionDlgBool(self.optDlg, 'ThousandsSeparator',
                                'Separate thousands with spaces')
        optiondlg.OptionDlgBool(self.optDlg, 'ForceSciNotation',
                                'Always show exponent')
        optiondlg.OptionDlgBool(self.optDlg, 'UseEngNotation',
                                'Use engineering notation')
        optiondlg.OptionDlgBool(self.optDlg, 'TrimExponents',
                                'Hide exponent leading zeros')
        optiondlg.OptionDlgBool(self.optDlg, 'ViewRegisters',
                                'View Registers on LCD')
        optiondlg.OptionDlgBool(self.optDlg, 'HideLcdHighlight',
                                'Hide LCD highlight')
        self.optDlg.startNewColumn()
        optiondlg.OptionDlgRadio(self.optDlg, 'AngleUnit', 'Angular Units',
                                 [('deg', 'Degrees'), ('rad', 'Radians')])
        self.optDlg.startGroupBox('Alternate Bases')
        optiondlg.OptionDlgInt(self.optDlg, 'AltBaseBits', 'Size limit',
                               CalcCore.minNumBits, CalcCore.maxNumBits,
                               True, 4, False, ' bits')
        optiondlg.OptionDlgBool(self.optDlg, 'UseTwosComplement',
                                'Use two\'s complement\nnegative numbers')
        self.optDlg.startGroupBox('Extra Views',)
        optiondlg.OptionDlgPush(self.optDlg, 'View Extra Data', self.viewExtra)
        optiondlg.OptionDlgPush(self.optDlg, 'View Other Bases',
                                self.viewAltBases)
        optiondlg.OptionDlgPush(self.optDlg, 'View Help file', self.help)
        optiondlg.OptionDlgInt(self.optDlg, 'MaxHistLength',
                               'Saved history steps', CalcCore.minMaxHist,
                               CalcCore.maxMaxHist, True, 10)
        if self.optDlg.exec_() == QDialog.Accepted:
            self.calc.option.writeChanges()
            newViewReg = self.calc.option.boolData('ViewRegisters')
            if newViewReg != oldViewReg:
                if newViewReg:
                    for w in self.extraLabels + self.extraLcds:
                        w.show()
                else:
                    for w in self.extraLabels + self.extraLcds:
                        w.hide()
                qApp.processEvents()
                self.adjustSize()
            if self.altBaseView:
                self.altBaseView.updateOptions()
            self.setLcdHighlight()
            self.calc.updateXStr()
        self.optDlg = None

    def setLcdHighlight(self):
        """Set lcd highlight based on option.
        """
        opt = self.calc.option.boolData('HideLcdHighlight') and \
              QLCDNumber.Flat or QLCDNumber.Filled
        self.lcd.setSegmentStyle(opt)
        for lcd in self.extraLcds:
            lcd.setSegmentStyle(opt)

    def updateColors(self):
        """Adjust the colors to the current option settings.
        """
        if self.calc.option.boolData('UseDefaultColors'):
            return
        pal = QApplication.palette()
        background = QColor(self.calc.option.intData('BackgroundR',
                                                           0, 255),
                                  self.calc.option.intData('BackgroundG',
                                                           0, 255),
                                  self.calc.option.intData('BackgroundB',
                                                           0, 255))
        foreground = QColor(self.calc.option.intData('ForegroundR',
                                                           0, 255),
                                  self.calc.option.intData('ForegroundG',
                                                           0, 255),
                                  self.calc.option.intData('ForegroundB',
                                                           0, 255))
        pal.setColor(QPalette.Base, background)
        pal.setColor(QPalette.Text, foreground)
        QApplication.setPalette(pal)

    def viewExtra(self, defaultTab=0):
        """Show extra data view.
        """
        if self.optDlg:
            self.optDlg.reject()   # unfortunately necessary?
        if not self.extraView:
            self.extraView = extradisplay.ExtraDisplay(self)
        self.extraView.tabUpdate(defaultTab)
        self.extraView.tab.setCurrentIndex(defaultTab)
        self.extraView.show()

    def viewReg(self):
        """Show extra data view with register tab open.
        """
        self.viewExtra(0)

    def viewHist(self):
        """Show extra data view with history tab open.
        """
        self.viewExtra(1)

    def viewMem(self):
        """Show extra data view with memory tab open.
        """
        self.viewExtra(2)

    def updateExtra(self):
        """Update current extra and alt base views.
        """
        if self.extraView and self.extraView.isVisible():
            self.extraView.updateData()
        if self.altBaseView:
            self.altBaseView.updateData()

    def toggleReg(self):
        """Toggle register display on LCD.
        """
        viewReg = not self.calc.option.boolData('ViewRegisters')
        self.calc.option.changeData('ViewRegisters',
                                    viewReg and 'yes' or 'no', 1)
        if viewReg:
            for w in self.extraLabels + self.extraLcds:
                w.show()
        else:
            for w in self.extraLabels + self.extraLcds:
                w.hide()
        self.adjustSize()
        self.calc.updateXStr()

    def viewAltBases(self):
        """Show alternate base view.
        """
        if self.optDlg:
            self.optDlg.reject()   # unfortunately necessary?
        if not self.altBaseView:
            self.altBaseView = altbasedialog.AltBaseDialog(self)
        self.altBaseView.updateData()
        self.altBaseView.show()

    def findHelpFile(self):
        """Return the path to the help file.
        """
        modPath = os.path.abspath(sys.path[0])
        if modPath.endswith('.zip') or modPath.endswith('.exe'):
            modPath = os.path.dirname(modPath)  # for py2exe/cx_freeze
        pathList = [helpFilePath, os.path.join(modPath, '../doc/'),
                    modPath, 'doc/']
        for path in pathList:
            if path:
                try:
                    fullPath = os.path.join(path, 'README.html')
                    with open(fullPath, 'r', encoding='utf-8') as f:
                        pass
                    return fullPath
                except IOError:
                    pass
        return ''

    def help(self):
        """View the ReadMe file.
        """
        if self.optDlg:
            self.optDlg.reject()   # unfortunately necessary?
        if not self.helpView:
            path = self.findHelpFile()
            if not path:
                QMessageBox.warning(self, 'rpCalc',
                                          'Read Me file not found')
                return
            self.helpView = helpview.HelpView(path, 'rpCalc README File',
                                              self.icons, self)
        self.helpView.show()

    def about(self):
        """About this program.
        """
        QMessageBox.about(self, 'rpCalc',
                                'rpCalc, Version {0}\n by {1}'.
                                format(__version__, __author__))

    def addCmdButton(self, text, row, col):
        """Adds a CalcButton for command functions.
        """
        button = CalcButton(text)
        self.cmdDict[text.upper()] = button
        self.cmdLay.addWidget(button, row, col)
        button.activated.connect(self.issueCmd)

    def addMainButton(self, key, text, row, col, extraRow=0, extraCol=0):
        """Adds a CalcButton for number and 4-function keys.
        """
        button = CalcButton(text)
        self.mainDict[key] = button
        self.mainLay.addWidget(button, row, col, 1+extraRow, 1+extraCol)
        button.activated.connect(self.issueCmd)

    def updateLcd(self):
        """Sets display back to CalcCore string.
        """
        numDigits = int(self.calc.option.numData('NumDecimalPlaces', 0, 9)) + 9
        if self.calc.option.boolData('ThousandsSeparator') or \
                self.calc.option.boolData('UseEngNotation'):
            numDigits += 2
        self.lcd.setDisplay(self.calc.xStr, numDigits)
        if self.calc.option.boolData('ViewRegisters'):
            nums = [self.calc.formatNum(num) for num in self.calc.stack[1:]]
            for num, lcd in zip(nums, self.extraLcds):
                lcd.setDisplay(num, numDigits)
        self.updateExtra()

    def issueCmd(self, text):
        """Sends command text to CalcCore - connected to button signals.
        """
        mode = self.calc.flag
        text = str(text).upper()
        if text == 'OPT':
            self.setOptions()
        elif text == 'SHOW':
            if not self.showMode:
                valueStr = self.calc.sciFormatX(11).replace('e', ' E', 1)
                self.lcd.setNumDigits(19)
                self.lcd.display(valueStr)
                self.showMode = True
                return
        elif text == 'EXIT':
            self.close()
            return
        else:
            self.calc.cmd(text)
        if text in ('SCI', 'DEG', 'OPT') or mode == Mode.decPlcMode:
            self.updateEntryLabel()
        self.showMode = False
        self.updateLcd()

    def textEntry(self, ch):
        """Searches for button match from text entry.
        """
        if not ch:
            return False
        if ord(ch) == 8:   # backspace key
            self.entryStr = self.entryStr[:-1]
        elif ord(ch) == 27:  # escape key
            self.entryStr = ''
        elif ch == '\t':     # tab key
            cmds = [key for key in self.cmdDict.keys() if
                    key.startswith(self.entryStr.upper())]
            if len(cmds) == 1:
                button = self.cmdDict[cmds[0]]
                button.clickEvent()
                button.tmpDown(300)
                self.entryStr = ''
            else:
                QApplication.beep()
        elif ch == ':' and not self.entryStr:
            self.entryStr = ':'   # optional command prefix
        else:
            newStr = (self.entryStr + ch).upper()
            if newStr == ':Q':    # vim-like shortcut
                newStr = 'EXIT'
            button = self.cmdDict.get(newStr.lstrip(':'))
            if button:
                button.clickEvent()
                button.tmpDown(300)
                self.entryStr = ''
            else:
                if [key for key in self.cmdDict.keys() if
                    key.startswith(newStr.lstrip(':'))]:
                    self.entryStr += ch
                else:
                    QApplication.beep()
                    return False
        self.updateEntryLabel()
        return True

    def keyPressEvent(self, keyEvent):
        """Event handler for keys - checks for numbers and typed commands.
        """
        button = self.mainDict.get(keyEvent.key())
        if not self.entryStr and button:
            button.clickEvent()
            button.setDown(True)
            return
        letter = str(keyEvent.text()).upper()
        if keyEvent.modifiers() == Qt.AltModifier:
            if self.altBaseView and self.altBaseView.isVisible():
                if letter in ('X', 'O', 'B', 'D'):
                    self.altBaseView.setCodedBase(letter, False)
                elif letter == 'V':
                    self.altBaseView.copyValue()
                elif letter == 'C':
                    self.altBaseView.close()
        elif not self.entryStr and self.calc.base == 16 and \
                 'A' <= letter <= 'F':
            self.issueCmd(keyEvent.text())
        elif self.altBaseView and self.altBaseView.isVisible() and \
                (self.calc.xStr == ' 0' or \
                 (self.calc.stack[0] == 0.0 and self.calc.base != 10)) and \
                self.calc.flag == Mode.entryMode and \
                letter in ('X', 'O', 'B', 'D'):
            self.altBaseView.setCodedBase(letter, True)
        elif not self.entryStr and keyEvent.key() == Qt.Key_Backspace:
            button = self.cmdDict['<-']
            button.clickEvent()
            button.tmpDown(300)
        elif not self.entryStr and keyEvent.key() == Qt.Key_Escape:
            self.popupMenu.popup(self.mapToGlobal(QPoint(0, 0)))
        elif not self.textEntry(str(keyEvent.text())):
            QWidget.keyPressEvent(self, keyEvent)

    def keyReleaseEvent(self, keyEvent):
        """Event handler for keys - sets button back to raised position.
        """
        button = self.mainDict.get(keyEvent.key())
        if not self.entryStr and button:
            button.setDown(False)

    def closeEvent(self, event):
        """Saves the stack prior to closing.
        """
        self.calc.saveStack()
        self.calc.option.changeData('MainDlgXSize', self.width(), True)
        self.calc.option.changeData('MainDlgYSize', self.height(), True)
        self.calc.option.changeData('MainDlgXPos', self.x(), True)
        self.calc.option.changeData('MainDlgYPos', self.y(), True)
        if self.extraView:
            self.calc.option.changeData('ExtraViewXSize',
                                        self.extraView.width(), True)
            self.calc.option.changeData('ExtraViewYSize',
                                        self.extraView.height(), True)
            self.calc.option.changeData('ExtraViewXPos',
                                        self.extraView.x(), True)
            self.calc.option.changeData('ExtraViewYPos',
                                        self.extraView.y(), True)
        if self.altBaseView:
            self.calc.option.changeData('AltBaseXPos',
                                        self.altBaseView.x(), True)
            self.calc.option.changeData('AltBaseYPos',
                                        self.altBaseView.y(), True)
        self.calc.option.writeChanges()
        QWidget.closeEvent(self, event)
