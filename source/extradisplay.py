#!/usr/bin/env python3

#****************************************************************************
# extradisplay.py, provides display windows for extra data
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
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QListView, QPushButton,
                             QTabWidget, QTreeWidget, QTreeWidgetItem,
                             QVBoxLayout, QWidget)


class ExtraViewWidget(QTreeWidget):
    """Base class of list views for ExtraDisplay.
    """
    def __init__(self, calcRef, parent=None):
        QListView.__init__(self, parent)
        self.calcRef = calcRef
        self.setRootIsDecorated(False)

    def setHeadings(self, headerLabels):
        """Add headings to columns.
        """
        self.setColumnCount(len(headerLabels))
        self.setHeaderLabels(headerLabels)


class RegViewWidget(ExtraViewWidget):
    """Register list view for ExtraDisplay.
    """
    def __init__(self, calcRef, parent=None):
        ExtraViewWidget.__init__(self, calcRef, parent)
        self.setHeadings(['Name', 'Value'])
        for text in ['T', 'Y', 'Z', 'X']:
            item = QTreeWidgetItem(self)
            item.setText(0, text)
            item.setTextAlignment(0, Qt.AlignCenter)
        self.resizeColumnToContents(0)
        self.setCurrentItem(item)
        self.updateData()

    def updateData(self):
        """Update with current data.
        """
        for i in range(4):
            self.topLevelItem(i).setText(1, '{:.15g}'.
                                         format(self.calcRef.stack[3 - i]))

    def selectedValue(self):
        """Return number for selected line.
        """
        if self.selectedItems():
            pos = self.indexOfTopLevelItem(self.selectedItems()[0])
            return self.calcRef.stack[3 - pos]
        return 0.0


class HistViewWidget(ExtraViewWidget):
    """History list view for ExtraDisplay.
    """
    def __init__(self, calcRef, parent=None):
        ExtraViewWidget.__init__(self, calcRef, parent)
        self.setHeadings(['Equation', 'Value'])
        self.updateData()

    def updateData(self):
        """Update with current data.
        """
        if not self.calcRef.histChg:
            return
        maxLen = self.calcRef.option.intData('MaxHistLength',
                                             self.calcRef.minMaxHist,
                                             self.calcRef.maxMaxHist)
        for eqn, value in self.calcRef.history[-self.calcRef.histChg:]:
            item = QTreeWidgetItem(self,
                                         [eqn, self.calcRef.formatNum(value)])
            if self.topLevelItemCount() > maxLen:
                self.takeTopLevelItem(0)
        self.resizeColumnToContents(0)
        self.clearSelection()
        self.setCurrentItem(item)
        self.scrollToItem(item)
        self.calcRef.histChg = 0

    def selectedValue(self):
        """Return number for selected line.
        """
        if self.selectedItems():
            pos = self.indexOfTopLevelItem(self.selectedItems()[0])
            return self.calcRef.history[pos][1]
        return 0.0


class MemViewWidget(ExtraViewWidget):
    """Memory list view for ExtraDisplay.
    """
    def __init__(self, calcRef, parent=None):
        ExtraViewWidget.__init__(self, calcRef, parent)
        self.setHeadings(['Num', 'Value'])
        for num in range(10):
            item = QTreeWidgetItem(self)
            item.setText(0, repr(num))
            item.setTextAlignment(0, Qt.AlignCenter)
        self.resizeColumnToContents(0)
        self.setCurrentItem(self.topLevelItem(0))
        self.updateData()

    def updateData(self):
        """Update with current data.
        """
        for i in range(10):
            self.topLevelItem(i).setText(1, self.calcRef.
                                            formatNum(self.calcRef.mem[i]))

    def selectedValue(self):
        """Return number for selected line.
        """
        if self.selectedItems():
            pos = self.indexOfTopLevelItem(self.selectedItems()[0])
            return self.calcRef.mem[pos]
        return 0.0


class ExtraDisplay(QWidget):
    """Displays registers, history or memory values, allows copies.
    """
    def __init__(self, dlgRef, parent=None):
        QWidget.__init__(self, parent)
        self.dlgRef = dlgRef
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowTitle('rpCalc Extra Data')
        topLay = QVBoxLayout(self)
        self.setLayout(topLay)
        self.tab = QTabWidget()
        self.regView = RegViewWidget(dlgRef.calc)
        self.tab.addTab(self.regView, '&Registers')
        self.histView = HistViewWidget(dlgRef.calc)
        self.tab.addTab(self.histView, '&History')
        self.memView = MemViewWidget(dlgRef.calc)
        self.tab.addTab(self.memView, '&Memory')
        self.tab.setFocus()
        topLay.addWidget(self.tab)
        self.tab.currentChanged.connect(self.tabUpdate)
        buttonLay = QHBoxLayout()
        topLay.addLayout(buttonLay)
        setButton = QPushButton('&Set\nCalc X')
        buttonLay.addWidget(setButton)
        setButton.clicked.connect(self.setXValue)
        allCopyButton = QPushButton('Copy\n&Precise')
        buttonLay.addWidget(allCopyButton)
        allCopyButton.clicked.connect(self.copyAllValue)
        fixedCopyButton = QPushButton('Copy\n&Fixed')
        buttonLay.addWidget(fixedCopyButton)
        fixedCopyButton.clicked.connect(self.copyFixedValue)
        self.buttonList = [setButton, allCopyButton, fixedCopyButton]
        closeButton = QPushButton('&Close')
        topLay.addWidget(closeButton)
        closeButton.clicked.connect(self.close)
        self.enableControls()
        option = self.dlgRef.calc.option
        xSize = option.intData('ExtraViewXSize', 0, 10000)
        ySize = option.intData('ExtraViewYSize', 0, 10000)
        if xSize and ySize:
            self.resize(xSize, ySize)
        self.move(option.intData('ExtraViewXPos', 0, 10000),
                  option.intData('ExtraViewYPos', 0, 10000))

    def tabUpdate(self, index):
        """Update given tab widget.
        """
        self.tab.widget(index).updateData()
        self.enableControls()

    def updateData(self):
        """Update data in current tab.
        """
        self.tab.currentWidget().updateData()
        self.enableControls()

    def enableControls(self):
        """Enable or disable buttons depending on content available.
        """
        for button in self.buttonList:
            button.setEnabled(len(self.tab.currentWidget().selectedItems()) >
                                  0)

    def setXValue(self):
        """Copy selected value to calculator X register.
        """
        self.dlgRef.calc.newXValue(self.tab.currentWidget().selectedValue())
        self.dlgRef.updateLcd()

    def copyAllValue(self):
        """Copy selected value to clipboard.
        """
        self.copyToClip('{:.15g}'.format(self.tab.currentWidget().
                                         selectedValue()))

    def copyFixedValue(self):
        """Copy selected value to clipboard after formatting.
        """
        self.copyToClip(self.dlgRef.calc.formatNum(self.tab.currentWidget().
                                                   selectedValue()))

    def copyToClip(self, text):
        """Copy text to the clipboard.
        """
        clip = QApplication.clipboard()
        if clip.supportsSelection():
            clip.setText(text, QClipboard.Selection)
        clip.setText(text)

    def keyPressEvent(self, keyEvent):
        """Pass most keypresses to main dialog.
        """
        if keyEvent.modifiers == Qt.AltModifier:
            QWidget.keyPressEvent(self, keyEvent)
        else:
            self.dlgRef.keyPressEvent(keyEvent)

    def keyReleaseEvent(self, keyEvent):
        """Pass most key releases to main dialog.
        """
        if keyEvent.modifiers == Qt.AltModifier:
            QWidget.keyReleaseEvent(self, keyEvent)
        else:
            self.dlgRef.keyReleaseEvent(keyEvent)
