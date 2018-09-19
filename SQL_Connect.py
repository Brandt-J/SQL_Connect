#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 13:15:21 2018

@author: brandt
"""

import mysql.connector
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import Particle_Wizard as pw
#from time import struct_time, strftime

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(200,200, 600, 400)
        self.setWindowTitle('SQL Connect')
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        
        self.particleWizardBtn = QtWidgets.QPushButton('Particle Insertion Wizard')
        self.particleWizardBtn.clicked.connect(self.particleWizard)
        self.activateTablesBtn = QtWidgets.QPushButton('Activate Manual Table Editing')
        self.activateTablesBtn.clicked.connect(self.activateButtons)
        
        self.groupbox = QtWidgets.QGroupBox('Database tabels')
        vbox = QtWidgets.QVBoxLayout()
        self.parameters = {'particles': 'Edit Particles',
                           'analysis': 'Edit Analyses',
                           'samples': 'Edit Samples',
                           'particles2analysis': 'Edit Particle->Analysis',
                           'affiliation': 'Edit Affiliations',
                           'colors': 'Edit Color',
                           'contributor': 'Edit Contributors',
                           'equipment': 'Edit Equipments',
                           'institution': 'Add Institutions',
                           'methods': 'Edit Methods',
                           'polymer_category': 'Edit PolymerCategories',
                           'polymer_type': 'Edit Polymer Types',
                           'projects': 'Edit Projects',
                           'sampling_compartment': 'Edit Sampling Compartments',
                           'shape': 'Edit Shapes',
                           }
        
        self.btns = []
        for index, key in enumerate(self.parameters):
            self.btns.append(QtWidgets.QPushButton(self.parameters[key]))
            self.btns[-1].clicked.connect(self.makeConnectLambda(key))
            self.btns[-1].setDisabled(True)
#            self.layout.addWidget(self.btns[-1], index)
            vbox.addWidget(self.btns[-1], index)
        
        self.groupbox.setLayout(vbox)
        self.layout.addWidget(self.particleWizardBtn, 0, 1)
        self.layout.addWidget(self.activateTablesBtn, 1, 1)
        self.layout.addWidget(self.groupbox, 2, 1)
        
        self.configBtn = QtWidgets.QPushButton('Edit SQL Connection')
        self.configBtn.clicked.connect(self.setSQLConn)
        self.layout.addWidget(self.configBtn, 0, 0)
        
        self.connData = {'user': 'BrandtJ',
                  'password': 'xASEHebi',
                  'host': '192.124.245.26',
                  'database': 'micropoll',
                  'raise_on_warnings': True}
        
        self.connLabel= QtWidgets.QLabel('(Currently connected as {})'.format(self.connData['user']))
        self.layout.addWidget(self.connLabel, 1, 0)
        
        self.insertWindows = []
    
    def activateButtons(self):    
        for btn in self.btns:
            btn.setDisabled(False)
            
    def setSQLConn(self):
        self.setupConWin = SetupSQLConnection()
        self.setupConWin.show()
    
    def makeConnectLambda(self, database):
        return lambda: self.addEntry(database)

    def addEntry(self, database):
        self.insertWindows.append(InsertionWindow(database, self))
        self.insertWindows[-1].show()
        
    def handleWindowActivity(self, closedWindow):
#        if closedWindow is self.insertWindows[-1]:
#            print('correct')
#        else:
#            print('this might go wrong...')
        
        self.insertWindows.remove(closedWindow)
        if len(self.insertWindows) > 0:
            self.insertWindows[-1].update()
            self.insertWindows[-1].setDisabled(False)
    
    def particleWizard(self):
        self.wizard = pw.ParticleWizard()
        self.wizard.show()



class SetupSQLConnection(QtWidgets.QWidget):
    def __init__(self):    
        super(SetupSQLConnection, self).__init__()
        self.setGeometry(200,200, 400, 400)
        self.setWindowTitle('Setup SQL Connection')
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        
        self.formBox = QtWidgets.QGroupBox('Connection parameters')
        
        self.lineEdits = {}
        layout = QtWidgets.QFormLayout()
        
        #create LineEdits from current connection setup
        for i in mainWin.connData:
            if mainWin.connData[i] not in [True, False]:
                self.lineEdits[i] = QtWidgets.QLineEdit(mainWin.connData[i])
                layout.addRow(QtWidgets.QLabel(i), self.lineEdits[i])
            else:
                self.lineEdits[i] = QtWidgets.QCheckBox('')
                if mainWin.connData[i] == True:
                    self.lineEdits[i].setChecked(True)
                layout.addRow(QtWidgets.QLabel(i), self.lineEdits[i])
                    
        
        self.formBox.setLayout(layout)
        self.layout.addWidget(self.formBox, 0, 0)
        
        self.commitBtn = QtWidgets.QPushButton('Save and close')
        self.commitBtn.clicked.connect(self.commitData)
        
        self.layout.addWidget(self.commitBtn, 1, 0)
        
    def commitData(self):
        for i in mainWin.connData:
            if i != 'raise_on_warnings':
                mainWin.connData[i] = self.lineEdits[i].text()
            else:
                mainWin.connData[i] = self.lineEdits[i].isChecked()
        self.close()
            

class InsertionWindow(QtWidgets.QWidget):
    def __init__(self, table, parentWindow):    
        super(InsertionWindow, self).__init__()
        self.setGeometry(200,200, 1600, 600)
        self.setWindowTitle('Inserting to {}'.format(table))
        self.globalLayout = QtWidgets.QGridLayout()
        self.setLayout(self.globalLayout)
        self.tablename = table
        self.numOldEntries = 50
        self.origNumOldEntries = 50
        self.firstUpdate = True
        self.parentWindow = parentWindow
        self.update()
        
    def update(self):
        self.connectToSQL()
        cursor = self.cnx.cursor()
        cursor.execute("SHOW columns FROM {}".format(self.tablename))
        self.columnNames = [column[0] for column in cursor.fetchall()]
        
        self.numOldEntries = self.origNumOldEntries = 50

        cursor.execute("SELECT * FROM {}".format(self.tablename))
        self.data = [row for row in cursor]
        if len(self.data) < self.numOldEntries:
            self.numOldEntries = len(self.data)        
        
        width = np.clip(len(self.columnNames)*150 + 200, 400, 1600)
        height = np.clip(len(self.data)*30 + 200, 300, 1000)
        
        self.setGeometry(self.x()+10, self.y()+10, width, height)
        
        self.labels = []
        self.labels_required = []
        self.combos = []
        self.combolists = []
        self.linedts = []
        boldfont = QtGui.QFont()
        boldfont.setBold(True)
        self.delbtns = []
        self.delLambdas = []
        
        self.dataLabels = []
        
        if not self.firstUpdate:
            for i in reversed(range(self.tableLayout.count())):
                self.tableLayout.itemAt(i).widget().setParent(None)
        else:
            self.tableLayout = QtWidgets.QGridLayout()
            
        for index, column in enumerate(self.columnNames):
            #Create headers
            self.labels.append(QtWidgets.QLabel(column))
            self.labels[-1].setFont(boldfont)
            
            curCol = self.labels[-1].text()
            if self.isRequiredColumn(curCol):       #add Label with a star for required columns, but leave the label unchanged... It is referenced often and should not be altered...
                self.labels_required.append(QtWidgets.QLabel(curCol+'*'))
                self.labels_required[-1].setFont(boldfont)
                self.tableLayout.addWidget(self.labels_required[-1], 0, index+1)
            else:
                self.tableLayout.addWidget(self.labels[-1], 0, index+1)
        
            #insert last, already present entries
            for i in np.arange(len(self.data), len(self.data)-self.numOldEntries, -1):
                datarow = i-1
                tablerow = i-len(self.data)+self.numOldEntries
                
                self.dataLabels.append(QtWidgets.QLabel(str(self.data[datarow][index])))
                
                self.tableLayout.addWidget(self.dataLabels[-1], tablerow, index+1)
                #create ToolTips for 
                if self.labels[-1].text() in ['Contributor', 'Analyst']:
                    self.dataLabels[-1].setToolTip(self.getToolTip('contributor', int(self.dataLabels[-1].text())))
                elif self.labels[-1].text() == 'Method' or self.labels[-1].text() == 'Prefered method':
                    self.dataLabels[-1].setToolTip(self.getToolTip('methods', int(self.dataLabels[-1].text())))
                elif self.labels[-1].text() in ['Country', 'InstituteCountry']:
                    self.dataLabels[-1].setToolTip(self.getToolTip('countries', self.dataLabels[-1].text()))
                elif self.labels[-1].text() == 'Equipment':
                    self.dataLabels[-1].setToolTip(self.getToolTip('equipment', int(self.dataLabels[-1].text())))
                elif self.labels[-1].text() == 'Equipment_owner':
                    self.dataLabels[-1].setToolTip(self.getToolTip('institution', int(self.dataLabels[-1].text())))
                    
                if index == 0:
                    #create DeleteButtons
                    self.delbtns.append(QtWidgets.QPushButton('del.'))
                    self.delLambdas.append(self.makeDelLambda(self.labels[-1].text(), self.data[datarow][0]))      #make lambda with IDLabel and corresponding ID
                    self.delbtns[-1].clicked.connect(self.delLambdas[-1])
                    
                    self.tableLayout.addWidget(self.delbtns[-1], tablerow, 0)
                
            if index == 0:
                self.tableLayout.addWidget(QtWidgets.QLabel('New entry:'), self.numOldEntries+1, 1)
                self.addbtn = QtWidgets.QPushButton('add')
                self.addbtn.clicked.connect(self.appendLine)
                self.tableLayout.addWidget(self.addbtn, self.numOldEntries+2, 0)
                
#                self.updateBtn = QtWidgets.QPushButton('update')

            #create LineEdits
            self.linedts.append(QtWidgets.QLineEdit(self))
            if index == 0:
                self.linedts[-1].setText('automatic')
                self.linedts[-1].setDisabled(True)
            elif self.isLinkedTable(self.tablename, self.labels[-1].text()):
                self.linedts[-1].setDisabled(True)
            self.tableLayout.addWidget(self.linedts[-1], self.numOldEntries + 2, index+1)
            
            if index > 0:
                #create Comboboxes
                self.combos.append(QtWidgets.QComboBox(self))
                self.tableLayout.addWidget(self.combos[-1], self.numOldEntries + 3, index+1)
                
                #get combolists:
                self.combolists.append(self.getComboLists(self.labels[-1].text(), index))      #get available entries for given column
                self.combos[-1].addItems(self.combolists[-1])
                self.combos[-1].currentIndexChanged.connect(self.makeComboLambda(self.combos[-1], self.linedts[-1], self.labels[-1].text()))
                
                #set Stretching
                self.tableLayout.setColumnStretch(index, 1)
        
        
        self.tableLayout.setRowStretch(self.numOldEntries+1, 1)
        
        self.groupbox = QtWidgets.QGroupBox('Content from table: {}'.format(self.tablename))      
        self.groupbox.setLayout(self.tableLayout)
        
        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setMinimumHeight(self.height()-50)
        self.scrollarea.setMinimumWidth(self.width()-50)
        self.scrollarea.setWidget(self.groupbox)
        self.scrollarea.setWidgetResizable(True)
        
        if not self.firstUpdate:
            self.globalLayout.itemAt(0).widget().setParent(None)
            
        self.globalLayout.addWidget(self.scrollarea)
        
        self.firstUpdate = False
        
        self.cnx.close()
    
    def isRequiredColumn(self, columnName):
        forSample = ['Sample_name', 'Project', 'Contributor', 'Site_name', 'Country', 'Compartment', 'Date', 'Time', 'Sampling_duration',
                     'GPS_LON', 'GPS_LAT']
        forParticle = ['Sample', 'Arrival_date', 'Prefered method', 'Amount', 'Analyst', 'Size_1', 'Categorised_result']
        forInstitute = ['Institute_Name', 'Institute_Acronym', 'InstituteCountry']
        
        if columnName in forSample + forParticle + forInstitute: return True
        else: return False
        
    
    def isLinkedTable(self, tablename, columname):
        self.linkedTables = [('samples', 'Project'),
                        ('samples', 'Contributor'),
                        ('samples', 'Method'),
                        ('samples', 'Country'),
                        ('samples', 'Compartment'),
                        ('particles', 'Sample'),
                        ('particles', 'Prefered method'),
                        ('particles', 'Analyst'),
                        ('particles', 'Size_fraction'),
                        ('particles', 'Colour'),
                        ('particles', 'Shape'),
                        ('particles', 'Categorised_result'),
                        ('particles', 'Indication_paint'),
                        ('methods', 'Category'),
                        ('methods', 'Equipment'),
                        ('methods', 'Equipment_owner'),
                        ('projects', 'LeadingInstitute'),]
        
        if (tablename, columname) in self.linkedTables:
            return True
        else:
            return False
    
    def getToolTip(self, table, idnumber):
        cursor = self.cnx.cursor()
        cursor.execute("SELECT * FROM {}".format(table))
        data = [row for row in cursor]
        ids = [i[0] for i in data]
#        try: idnumber = int(idnumber)
#        except: print(table, idnumber)
        
        if table == "contributor":
            toolTip = '{} {}'.format(data[ids.index(idnumber)][1], data[ids.index(idnumber)][2])
        
        elif table in ['methods', 'institution', 'equipment']:
            toolTip = str(data[ids.index(idnumber)][1])
            
        elif table == 'countries':
            countryshorts = [i[1] for i in data]
            toolTip = str(data[countryshorts.index(idnumber)][2])
        
#        if table == 'institution':
            
        
        return toolTip
    
    def getTableContent(self, tablename):
        cursor = self.cnx.cursor()
        cursor.execute("SELECT * FROM {}".format(tablename))
        return [row for row in cursor]
                
    
    def getComboLists(self, columnName, columnIndex):
        entrylist = ['']
        

        #### external relations for SAMPLE table
#        if self.tablename == 'samples' or self.tablename == 'particles':
        takeNameFromIndex1 = {'Sample': 'samples',
                              'Compartment': 'sampling_compartment',
                              'Size_fraction': 'size_fraction',
                              'Colour': 'colors',
                              'Shape': 'shape',
                              'Categorised_result': 'polymer_category',
                              'Indication_paint': 'paint_remark',
                              'Category': 'method_category',
                              }
        
        if columnName == 'Project':
            projects = [i[1] for i in self.getTableContent('projects')]
            for index, i in enumerate(projects):
                entrylist.append(i)
            entrylist.append('CREATE NEW')
        
        elif columnName == 'Contributor' or columnName == 'Analyst':
            tmpdata = self.getTableContent('contributor')
            idContrib = [i[0] for i in tmpdata]
            names = [i[1] for i in tmpdata]
            lastnames = [i[2] for i in tmpdata]                
            for index, i in enumerate(idContrib):
                entrylist.append('{}: {} {}'.format(i, names[index], lastnames[index]))
            entrylist.append('CREATE NEW')
        
        elif columnName == 'Method' or columnName == 'Prefered method':
            tmpdata = self.getTableContent('methods')
            idmethod = [i[0] for i in tmpdata]
            methodnames = [i[1] for i in tmpdata]                
            for index, i in enumerate(idmethod):
                entrylist.append('{}: {}'.format(i, methodnames[index]))
            entrylist.append('CREATE NEW')
        
        elif columnName == 'polymer_type':
            tmpdata = self.getTableContent('polymer_type')
            idpolym = [i[0] for i in tmpdata]
            polymnames = [i[1] for i in tmpdata]                
            for index, i in enumerate(idpolym):
                entrylist.append('{}: {}'.format(i, polymnames[index]))
            entrylist.append('CREATE NEW')
        
        elif columnName == 'Equipment':
            tmpdata = self.getTableContent('equipment')
            idequip = [i[0] for i in tmpdata]
            equipnames = [i[1] for i in tmpdata]                
            for index, i in enumerate(idequip):
                entrylist.append('{}: {}'.format(i, equipnames[index]))
            entrylist.append('CREATE NEW')
        
        elif columnName == 'Equipment_owner':
            tmpdata = self.getTableContent('institution')
            idinsti = [i[0] for i in tmpdata]
            instinames = [i[1] for i in tmpdata]                
            for index, i in enumerate(idinsti):
                entrylist.append('{}: {}'.format(i, instinames[index]))
            entrylist.append('CREATE NEW')
        
        elif columnName in ['Country', 'InstituteCountry']:
            tmpdata = self.getTableContent('countries')
            countryshort = [i[1] for i in tmpdata]
            countrylong = [i[2] for i in tmpdata]
            for i in range(len(countrylong)):
                entrylist.append('{}: {}'.format(countryshort[i], countrylong[i]))
            entrylist.append('CREATE NEW')
            
#        elif columnName 
        
        elif columnName in takeNameFromIndex1:
            tmpdata = self.getTableContent(takeNameFromIndex1[columnName])
            for i in tmpdata:
                entrylist.append(i[1])
            entrylist.append('CREATE NEW')
        

        else:
            for i in self.data:
                entrylist.append(str(i[columnIndex]))
            entrylist = list(set(entrylist))        #get unique entries
#        else:
#            for i in self.data:
#                entrylist.append(str(i[columnIndex]))
#                entrylist = list(set(entrylist))        #get unique entries
                
        
    
        return entrylist
    
    def makeComboLambda(self, combobox, lineedit, tablename):
        return lambda: self.applyComboChange(combobox, lineedit, tablename, self.parentWindow)

    def applyComboChange(self, combobox, lineedit, tablename, parentWindow):
        if combobox.currentText() != 'CREATE NEW':
            lineedit.setText(combobox.currentText())
        else:
            linkedTables = {'Affiliation': 'affiliation',
                            'Analyst': 'contributor',
                            'Categorised_result': 'polymer_category',
                            'Category': 'method_category',
                            'Compartment': 'sampling_compartment',
                            'Contributor': 'contributor',
                            'Country': 'countries',
                            'Colour': 'colors',
                            'Equipment': 'equipment',
                            'Equipment_owner': 'institution',
                            'Indication_paint': 'paint_remark',
                            'Institution': 'institution',
                            'InstituteCountry': 'countries',
                            'LadingInstitute': 'institution',
                            'Method': 'methods',
                            'Project': 'projects',
                            'Sample': 'samples',
                            'Shape': 'shape',
                            'Size_fraction': 'size_fraction',}
            
            self.setDisabled(True)
            parentWindow.insertWindows.append(InsertionWindow(linkedTables[tablename], self.parentWindow))            
            parentWindow.insertWindows[-1].show()
        
    def getNewIndex(self, indexlist):
        indexlist = set(indexlist)      #finding items in set is faster than in list(?)
        indexFound = False
        index = 1
        while not indexFound:
            if index not in indexlist:
                indexFound = True
            else:
                index += 1
        return index
    
    
    def appendLine(self):
        self.connectToSQL()
        cursor = self.cnx.cursor()
        lastline = list(self.data[-1][:])

        #create list of new entries
        newline = []
        for index, entry in enumerate(self.linedts):
            if entry.text() == 'automatic':
                newline.append(self.getNewIndex([i[0] for i in self.data]))
            
            elif entry.text() == '':
                newline.append(None)
                
            else:
                newline.append(entry.text())
        
        everythingIsValid = True
        #make sure, that correct datatypes are passed
        for index, entry in enumerate(newline):
            
            #convert intentionally altered data structure of particular columns:
            colonSeparatedEntries = ['Contributor', 'Method', 'Country', 'Equipment', 'Equipment_owner', 'Analyst', 'InstituteCountry']
            column= self.labels[index].text()
            if self.isRequiredColumn(column) and entry is None:
                QtWidgets.QMessageBox.about(self, 'Error', "Missing entry in '{}'!".format(column))
                everythingIsValid = False
            
            if column in colonSeparatedEntries:
                if entry is None:
                    QtWidgets.QMessageBox.about(self, 'Error', "Missing entry in '{}'!".format(column))
                    everythingIsValid = False
                else:
                    newline[index] = entry.split(':')[0]

#            #assure correct datatype            
            else:
                try:
                    type(lastline[index])(newline[index])
                except:
                    targetType = type(lastline[index])
                    if targetType == float:
                        newline[index] = 0.0
                    elif targetType == int:
                        newline[index] = 0
                    elif targetType == str:
                        newline[index] = 'None'
        
        if everythingIsValid:
            cursor.execute("SHOW columns FROM {}".format(self.tablename))
            origcols = [column[0] for column in cursor.fetchall()]
            
            #filter out not used columns
            origcols = [col for index, col in enumerate(origcols) if newline[index] not in ['None', None, '']]
            newline = [entry for entry in newline if entry not in ['None', None, '']]

            newline = tuple(newline)
    
            colnames = ""
            #create colnames
            for index, i in enumerate(origcols):
                colnames = colnames + i
                if index != len(origcols)-1:
                    colnames = colnames + ", "

            cursorstatement = "INSERT INTO {}({}) VALUES {}".format(self.tablename, colnames, newline)
#            cursorstatement = "INSERT INTO {} VALUES{}".format(self.tablename, newline)
            print(cursorstatement)
    #        
            cursor.execute(cursorstatement)
            self.cnx.commit()
            
            self.cnx.close()
            self.update()
    
    def makeDelLambda(self, IDLabel, ID):
        return lambda: self.deleteEntry(IDLabel, ID)
    
    def deleteEntry(self, IDLabel, ID):
        qm = QtWidgets.QMessageBox.question(self, 'Confirm delete', 'Are you really sure to delete {} {}?'.format(IDLabel, ID))
        
        if qm == QtWidgets.QMessageBox.Yes:
            self.connectToSQL()
            cursor = self.cnx.cursor()
            try:
                cursor.execute("DELETE FROM {} WHERE {} = {}".format(self.tablename, IDLabel, ID))
                self.cnx.commit()
            except:
                QtWidgets.QMessageBox.about(self, 'Error', 'Entry could not be deleted... It is probably referenced from another table..')
            self.cnx.close()
            self.update()
    
    def connectToSQL(self):    
        config = {'user': 'BrandtJ',
                  'password': 'xASEHebi',
                  'host': '192.124.245.26',
                  'database': 'micropoll',
                  'raise_on_warnings': True}
        
        try:
            self.cnx = mysql.connector.connect(**config)  #port: 3306
        except mysql.connector.Error as err:
            print(err)
            QtWidgets.QMessageBox.about(self, 'Error', 'Connection to database failed')
            self.close()
    
    def closeEvent(self, event):
        try:
            self.parentWindow.handleWindowActivity(self)        #if window is child of SQL-Connect MainWindow (not the Wizard)
        except:
            pass
        event.accept()
        


if __name__ == '__main__':
    import sys
    try:
        del(app)
    except:
        pass
    
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    app.exec_()