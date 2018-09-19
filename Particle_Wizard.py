# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 07:57:37 2018

@author: brandt
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import SQL_Connect as sq


class ParticleWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(ParticleWizard, self).__init__()
        self.addPage(WizardPromptProperties(self))
        self.addPage(WizardPromptFinalData(self))
        self.setWindowTitle('Enter Particle Wizard')
        self.setGeometry(200, 200, 800, 400)
        self.insertWindows = []


class WizardPromptProperties(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(WizardPromptProperties, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.parentWindow = parent
        self.insertWindows = []
        
        dataObj= sq.InsertionWindow('particles', self)
        
        #find sampleNames
        sampleNameIndex = dataObj.columnNames.index('Sample')
        
        methodGroup = QtWidgets.QGroupBox('To which sample does the particle belong?')
        methodLayout = QtWidgets.QHBoxLayout()
        
        self.sampleList = dataObj.combos[sampleNameIndex-1]
        self.sampleList.removeItem(0)
        self.sampleList.removeItem(self.sampleList.count()-1)
        
        #retrieve all elements...
        self.sampleEdit = LinkedLineEdit(self.sampleList)
        methodLayout.addWidget(QtWidgets.QLabel('Select from: '))
        methodLayout.addWidget(self.sampleList)
        methodLayout.addWidget(QtWidgets.QLabel(' refine selction by typing here: '))
        methodLayout.addWidget(self.sampleEdit)

        methodGroup.setLayout(methodLayout)
        layout.addWidget(methodGroup)
        
        measureGroup = QtWidgets.QGroupBox('Performed Analyses')
        measureGroupLayout = QtWidgets.QGridLayout()
        headers = ['TableID', 'Use', 'IDAnalysis', 'Method*', 'Spectrum', 'Library Entry*', 'Hit Quality*', 'Result*', 'Comment (optional)']
        self.headerLabels = [QtWidgets.QLabel(header) for header in headers]
        boldfont = QtGui.QFont()
        boldfont.setBold(True)
        for label in self.headerLabels:
            if label.text().find('*') > -1:
                label.setFont(boldfont)
        
        self.analyses = [[QtWidgets.QCheckBox(), QtWidgets.QLineEdit('automatic'), QtWidgets.QComboBox(), QtWidgets.QPushButton('Select Spectrum'),
                          QtWidgets.QLineEdit(''), QtWidgets.QDoubleSpinBox(), QtWidgets.QLineEdit(''), QtWidgets.QLineEdit('')] for i in range(4)]
        
        #configure Checkboxes:
        for index, checkbox in enumerate([row[0] for row in self.analyses]):
            checkbox.stateChanged.connect(self.makeCheckBoxLambda(checkbox, index))
            if index == 0:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
            self.disableRow(checkbox, index)
        
        #disable IDAnalysis-Entries
        for row in self.analyses:
            row[1].setDisabled(True)

        #get method list
        methodList = dataObj.combos[dataObj.columnNames.index('Prefered method')-1]
        methodList.removeItem(0)
        
        for box in [row[2] for row in self.analyses]:
            for i in range(methodList.count()):
                methodText = methodList.itemText(i)
                if methodText != 'CREATE NEW':
                    box.addItem(methodText)
            
        
        for colIndex, headerlabel in enumerate(self.headerLabels):
            if colIndex > 0:
                measureGroupLayout.addWidget(headerlabel, 0, colIndex+1)
            
            for rowIndex in range(4):
                if headerlabel.text() == 'TableID':                        
                    measureGroupLayout.addWidget(QtWidgets.QLabel(str(rowIndex+1)), rowIndex+1, 0)
                else:
                    measureGroupLayout.addWidget(self.analyses[rowIndex][colIndex-1], rowIndex+1, colIndex+1)

        measureGroup.setLayout(measureGroupLayout)
        
        layout.addWidget(measureGroup)
     
    def makeCheckBoxLambda(self, box, index):
        return lambda: self.disableRow(box, index)
    
    def updateSample(self):
        self.parentWindow.page(1).sampleNameLabel.setText(self.sampleList.currentText()) 
    
    def disableRow(self, box, index):
        #disable, enable everything but the CheckBox (has to be enabled ALWAYS) and the ID-Entry (has to be disabled)
        for element in self.analyses[index][2:]:#
            
            element.setDisabled(not box.isChecked())

class WizardPromptFinalData(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(WizardPromptFinalData, self).__init__(parent)
        self.parent = parent
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        boldfont = QtGui.QFont()
        boldfont.setBold(True)
        header = QtWidgets.QLabel('Insert Summarized Data')
        header.setFont(boldfont)
        layout.addWidget(header, 0, 0)
        self.sampleNameLabel = QtWidgets.QLabel('')
        layout.addWidget(QtWidgets.QLabel('Sample Name:'), 1, 0)
        layout.addWidget(self.sampleNameLabel, 1, 1)
        
        self.summary = {QtWidgets.QLabel('ArrivalDate* (DD-MM-YYYY)'): QtWidgets.QLineEdit(),
                       QtWidgets.QLabel('Analysis Date (DD-MM-YYYY)'): QtWidgets.QLineEdit(), 
                       QtWidgets.QLabel('Amount'): QtWidgets.QDoubleSpinBox(),
                       QtWidgets.QLabel('Analyst*'): QtWidgets.QComboBox(),
                       QtWidgets.QLabel('Size fraction'): QtWidgets.QComboBox(),
                       QtWidgets.QLabel('Colour'): QtWidgets.QComboBox(),
                       QtWidgets.QLabel('Shape'): QtWidgets.QComboBox(), 
                       QtWidgets.QLabel('Size1*'): QtWidgets.QDoubleSpinBox(),
                       QtWidgets.QLabel('Size2'): QtWidgets.QDoubleSpinBox(), 
                       QtWidgets.QLabel('Image'): QtWidgets.QPushButton('Select Image'), 
                       QtWidgets.QLabel('Categorized Result'): QtWidgets.QComboBox(),
                       QtWidgets.QLabel('Indication paint'): QtWidgets.QComboBox()}
        
        for index, key in enumerate(self.summary):
            if index in [0, 1]:
                key.setToolTip('DD-MM-YYYY')
            if key.text().find('*') > -1:
                key.setFont(boldfont)
            layout.addWidget(key, index+2, 0)
            layout.addWidget(self.summary[key], index+2, 1)
            
        #add fake labels for 
        layout.addWidget(QtWidgets.QLabel(''), 0, 2)
        layout.setColumnMinimumWidth(0, 300)
        layout.setColumnMinimumWidth(1, 300)
        layout.setColumnStretch(2, 1)


class LinkedLineEdit(QtWidgets.QLineEdit):
    def __init__(self, combobox):
        super(LinkedLineEdit, self).__init__()
        
        self.combobox = combobox
        self.entries = [self.combobox.itemText(i) for i in range(self.combobox.count())]
        print(self.entries)
    
    def keyPressEvent(self, event):
        super(LinkedLineEdit, self).keyPressEvent(event)
        curString = self.text()
        self.combobox.clear()
        if len(curString) == 0:
            self.combobox.addItems(self.entries)
        else:
            matchingEntries = []
            for entry in self.entries:
                if entry.find(curString) >= 0:
                    matchingEntries.append(entry)
            self.combobox.addItems(matchingEntries)
            self.combobox.update()


if __name__ == '__main__':
    import sys
    try:
        del(app)
    except:
        pass
    
    app = QtWidgets.QApplication(sys.argv)
    mainWin = ParticleWizard()
    mainWin.show()
    app.exec_()