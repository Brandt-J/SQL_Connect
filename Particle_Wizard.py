# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 07:57:37 2018

@author: brandt
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import SQL_Connect as sq
import os
import cv2
#import numpy as np

class ParticleWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(ParticleWizard, self).__init__()
        self.addPage(WizardPromptProperties(self))
        self.addPage(WizardPromptFinalData(self))
        self.setWindowTitle('Enter Particle Wizard')
        self.setGeometry(200, 200, 800, 400)
        self.insertWindows = []
        
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.checkResults)
    
    def checkResults(self):
        everythingValid = True
        #retrieve data
        analyses = []
        for analysis in self.page(0).analyses:
            if analysis[0].isChecked():
                analyses.append(analysis[1:])
        
        #summarize analyses
        numAnalyses = len(analyses)
        
        #get sql connection
        dataObj = sq.InsertionWindow('analysis', self)
        currentIndices = [i[0] for i in dataObj.data]
        newIndices = self.getNewIndices(numAnalyses, currentIndices)
        
        
        self.finalanalyses = analyses
        
        for i in range(numAnalyses):
            self.finalanalyses[i][0] = int(newIndices[i])                                   #analysis id    
            self.finalanalyses[i][1] = int(analyses[i][1].currentText().split(':')[0])      #method id
            self.finalanalyses[i][2] = analyses[i][3].text()                                #library entry
            self.finalanalyses[i][3] = analyses[i][4].value()                               #HQI
            self.finalanalyses[i][4] = self.page(0).spectraList[i]                          #spectrum
            self.finalanalyses[i][5] = int(analyses[i][5].currentText().split(':')[0])      #result id
            self.finalanalyses[i][6] = analyses[i][6].text()                                #comment
        
        
        #summarize particleInfo
        dataObj = sq.InsertionWindow('particles', self)
        currentIndices = [i[0] for i in dataObj.data]
        summary = list(self.page(1).summary.values())
        requiredColumns = ['IDParticles', 'Sample', 'Prefered method', 'Arrival_date']
        
        self.particleInfo = []
        self.particleInfo.append(int(self.getNewIndices(1, currentIndices)[0]))                 #particle id
        self.particleInfo.append(self.page(0).sampleList.currentText())                         #sample name
        self.particleInfo.append(int(summary[10].currentText().split(':')[0]))                  #method id
        self.particleInfo.append(self.verifyDateInput(summary[0].text()))                       #arrival date
        if summary[1].text() != '':                                                             #analysis date (optional)
            self.particleInfo.append(summary[1].text())
            requiredColumns.append('Analysis_date')
        requiredColumns.append('Amount')
        requiredColumns.append('Analyst')
        self.particleInfo.append(float(summary[2].value()))                                     #Amount
        self.particleInfo.append(int(summary[3].currentText().split(':')[0]))                   #Analyst ID
        if summary[4].currentText() != '':                                                      #Size_fraction (optional)
            self.particleInfo.append(summary[4].currentText())
            requiredColumns.append('Size_fraction') 
        if summary[5].currentText() != '':                                                      #Colour (optional)
            self.particleInfo.append(summary[5].currentText())
            requiredColumns.append('Colour')
        if summary[6].currentText() != '':                                                      #Shape (optional)
            self.particleInfo.append(summary[6].currentText())
            requiredColumns.append('Shape')
        requiredColumns.append('Size_1')                                                        #Size_1
        self.particleInfo.append(summary[7].value())
        if summary[8].value() != 0.0:                                                           #Size_2 (optional)
            self.particleInfo.append(summary[8].value())
            requiredColumns.append('Size_2')
        if self.page(1).image is not None:                                                      #Image
            self.particleInfo.append(self.page(1).image)
            requiredColumns.append('Image')
        requiredColumns.append('Categorised_result')                                            #categorized_result
        self.particleInfo.append(summary[11].currentText())
        if summary[12].currentText() != '':
            requiredColumns.append('Indication_paint')
            self.particleInfo.append(summary[12].currentText())
        
        print(requiredColumns)
        print(self.particleInfo)
            
        
        
        
        
#        
#        
#        self.summary = 0{QtWidgets.QLabel('ArrivalDate* (DD-MM-YYYY)'): QtWidgets.QLineEdit(),
#                       1QtWidgets.QLabel('Analysis Date (DD-MM-YYYY)'): QtWidgets.QLineEdit(), 
#                       2QtWidgets.QLabel('Amount*'): QtWidgets.QSpinBox(),
#                       3QtWidgets.QLabel('Analyst*'): analystList,
#                       4QtWidgets.QLabel('Size fraction'): sizeFracList,
#                       5QtWidgets.QLabel('Colour'): colorList,
#                       6QtWidgets.QLabel('Shape'): shapeList, 
#                       7QtWidgets.QLabel('Size1*'): QtWidgets.QDoubleSpinBox(),
#                       8QtWidgets.QLabel('Size2'): QtWidgets.QDoubleSpinBox(), 
#                       9QtWidgets.QLabel('Image'): self.selectImageButton,
#                       10QtWidgets.QLabel('Preferred Method*'): methodList,
#                       11QtWidgets.QLabel('Categorized Result*'): categoryList,
#                       12QtWidgets.QLabel('Indication paint'): paintList}

    def verifyDateInput(self, date_string):
        def getStringInput():
            text, ok = QtWidgets.QInputDialog.getText(self, 'MISSING ARRIVAL DATE', 'Please provide date as DD-MM-YYYY:')
            if ok:
                return text
            else:
                return None
        
        if date_string == '':
            date_string = getStringInput()
            
        return date_string
    
    def getNewIndices(self, numberOfIndices, presentIndices):
        indexlist = presentIndices
        newIndices = []
        for i in range(numberOfIndices):
            indexFound = False
            index = 1
            while not indexFound:
                if index not in indexlist:
                    indexFound = True
                else:
                    index += 1
            newIndices.append(index)
            indexlist.append(index)
        return newIndices
    

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
        self.sampleList.currentTextChanged.connect(self.updateSample)
        
        #retrieve all elements...
        self.sampleEdit = LinkedLineEdit(self.sampleList)
        methodLayout.addWidget(QtWidgets.QLabel('Select from: '))
        methodLayout.addWidget(self.sampleList)
        methodLayout.addWidget(QtWidgets.QLabel(' refine selection by typing here: '))
        methodLayout.addWidget(self.sampleEdit)

        methodGroup.setLayout(methodLayout)
        layout.addWidget(methodGroup)
        
        measureGroup = QtWidgets.QGroupBox('Performed Analyses')
        measureGroupLayout = QtWidgets.QGridLayout()
        headers = ['TableID', 
                   'Use', 
                   'IDAnalysis', 
                   'Method*', 
                   'Spectrum', 
                   'Library Entry*', 
                   'Hit Quality*', 
                   'Result*', 
                   'Comment (optional)']
        tooltips = ['', 
                    'Check for adding more analayses', 
                    'ID will be generated automatically', 
                    'The method of analysis', 
                    'Select ASCII spectrum file',
                    'Name of the hit in the spectra database', 
                    'Hit quality of indicated library entry', 
                    'Select unambiguos entry from result list', 
                    'optional free text comment']
        
        self.headerLabels = [QtWidgets.QLabel(header) for header in headers]
        for index, header in enumerate(self.headerLabels):
            header.setToolTip(tooltips[index])
            
        boldfont = QtGui.QFont()
        boldfont.setBold(True)
        for label in self.headerLabels:
            if label.text().find('*') > -1:
                label.setFont(boldfont)
        
        #get method list
        methodList = dataObj.combos[dataObj.columnNames.index('Prefered method')-1]
        methodList.removeItem(0)
        
        #retrieve possible results:
        dataObj= sq.InsertionWindow('polymer_type', self)
        polymResultList = dataObj.combos[dataObj.columnNames.index('polymer_type')-1]
        polymResultList = [polymResultList.itemText(i) for i in range(polymResultList.count()) if i > 0]
        polymResultList.remove('CREATE NEW')

        #get polymer Results and Spectra Buttons        
        self.polymResults = []
        self.spectraList = [None]*4
        self.spectraBtns = []
       
        for i in range(4):
            curComboBox = QtWidgets.QComboBox()
            curComboBox.addItems(polymResultList)
            self.polymResults.append(curComboBox)
            
            self.spectraBtns.append(QtWidgets.QPushButton('Select Spectrum'))
            self.spectraBtns[-1].clicked.connect(self.makeFileDialogLambda(i, self.spectraList))
        
        self.analyses = [[QtWidgets.QCheckBox(), QtWidgets.QLineEdit('automatic'), QtWidgets.QComboBox(), self.spectraBtns[i],
                          QtWidgets.QLineEdit(''), QtWidgets.QDoubleSpinBox(), self.polymResults[i], QtWidgets.QLineEdit('')] for i in range(4)]
        
        for row in self.analyses:
            row[-1].setMinimumWidth(250)
            
        
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
    
    def disableRow(self, box, index):
        #disable, enable everything but the CheckBox (has to be enabled ALWAYS) and the ID-Entry (has to be disabled)
        for element in self.analyses[index][2:]:#
            
            element.setDisabled(not box.isChecked())
    
    def makeFileDialogLambda(self, index, spectraList):
        return lambda: self.setSpectrumFile(index, spectraList)
    
    def isNumber(self, string):
        try:
            float(string)
            return True
        except:
            return False
    
    def setSpectrumFile(self, index, spectraList):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Select ASCII Spectrum', os.getcwd(), 'ASCII Text file (*.txt)')[0]
        curSpec = []
        #read the file and get its properties:
        with open(fname) as file:
            for line in file:
                line = line.split('\t')
                if len(line) > 1:
                    if self.isNumber(line[0]) and self.isNumber(line[1]):
                        curSpec.append((float(line[0]), float(line[1])))
        
        spectraList[index] = curSpec
        
        shortName = fname.split('/')[-1]
        self.spectraBtns[index].setText(shortName)
    
    def updateSample(self):
        self.parentWindow.page(1).sampleNameLabel.setText(self.sampleList.currentText()) 
    

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
        
        self.selectImageButton = QtWidgets.QPushButton('SelectImage')
        self.selectImageButton.clicked.connect(self.loadImage)
        self.image = None
        
        #retrieve further Data:
        dataObj= sq.InsertionWindow('particles', self)
        analystList = dataObj.combos[dataObj.columnNames.index('Analyst')-1]
        sizeFracList = dataObj.combos[dataObj.columnNames.index('Size_fraction')-1]
        colorList = dataObj.combos[dataObj.columnNames.index('Colour')-1]
        shapeList = dataObj.combos[dataObj.columnNames.index('Shape')-1]
        methodList = dataObj.combos[dataObj.columnNames.index('Prefered method')-1]
        categoryList = dataObj.combos[dataObj.columnNames.index('Categorised_result')-1]
        paintList = dataObj.combos[dataObj.columnNames.index('Indication_paint')-1]
        
        for i in [analystList, sizeFracList, colorList, shapeList, methodList, categoryList, paintList]:
            i.removeItem(i.count()-1)
            if i in [analystList, methodList, categoryList]:
                i.removeItem(0)
            

        self.summary = {QtWidgets.QLabel('ArrivalDate* (DD-MM-YYYY)'): QtWidgets.QLineEdit(),
                       QtWidgets.QLabel('Analysis Date (DD-MM-YYYY)'): QtWidgets.QLineEdit(), 
                       QtWidgets.QLabel('Amount*'): QtWidgets.QSpinBox(),
                       QtWidgets.QLabel('Analyst*'): analystList,
                       QtWidgets.QLabel('Size fraction'): sizeFracList,
                       QtWidgets.QLabel('Colour'): colorList,
                       QtWidgets.QLabel('Shape'): shapeList, 
                       QtWidgets.QLabel('Size1*'): QtWidgets.QDoubleSpinBox(),
                       QtWidgets.QLabel('Size2'): QtWidgets.QDoubleSpinBox(), 
                       QtWidgets.QLabel('Image'): self.selectImageButton,
                       QtWidgets.QLabel('Preferred Method*'): methodList,
                       QtWidgets.QLabel('Categorized Result*'): categoryList,
                       QtWidgets.QLabel('Indication paint'): paintList}
        
        tooltips = ['When did the sample arrive?',
                    'When was the particle finally analyzed?',
                    'How many of these particles were in the sample?\ne.g. 5, if 5 completely identical particles were present',
                    'Who did the analysis?',
                    'Size fraction, to which the particle belongs',
                    'Select color from list',
                    'Select shape from list',
                    'Long Size in µm',
                    'Short Size in µm',
                    'Upload an image file',
                    'What method is the finally preferred one?',
                    'Select type category from list',
                    'In case of paint appearance, select more detailed description']
        
        for index, element in enumerate(self.summary):
            element.setToolTip(tooltips[index])
            if index == 2:
                self.summary[element].setValue(1)
            
        
        for index, key in enumerate(self.summary):
            if index in [0, 1]:
                key.setToolTip('DD-MM-YYYY')
            if key.text().find('*') > -1:
                key.setFont(boldfont)
            layout.addWidget(key, index+2, 0)
            layout.addWidget(self.summary[key], index+2, 1)
            
        layout.addWidget(QtWidgets.QLabel(''), 0, 2)
        layout.setColumnMinimumWidth(0, 300)
        layout.setColumnMinimumWidth(1, 300)
        layout.setColumnStretch(2, 1)

    
    def loadImage(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image File', os.getcwd(), 'image files (*.jpg *.jpeg *.bmp *.png *.tiff *.tif)')[0]
        if len(fname) > 0:
            try:
                self.image = cv2.imread(fname)
                shortName = fname.split('/')[-1]
                self.selectImageButton.setText(shortName)
            except:
                QtWidgets.QMessageBox.about(self, 'Error', 'Failed loading image file')
    

class LinkedLineEdit(QtWidgets.QLineEdit):
    def __init__(self, combobox):
        super(LinkedLineEdit, self).__init__()
        self.combobox = combobox
        self.entries = [self.combobox.itemText(i) for i in range(self.combobox.count())]
    
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