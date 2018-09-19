# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:29:16 2018

@author: brandt
"""
from PyQt5 import QtCore, QtGui, QtWidgets

class Window(QtWidgets.QWidget):
    def __init__(self, val):
        super(Window, self).__init__()
        mygroupbox = QtWidgets.QGroupBox('this is my groupbox')
        myform = QtWidgets.QFormLayout()
        labellist = []
        combolist = []
        for i in range(val):
            labellist.append(QtWidgets.QLabel('mylabelmylabelmylabelmylabelmylabel'))
            combolist.append(QtWidgets.QComboBox())
            myform.addRow(labellist[i],combolist[i])
            
        mygroupbox.setLayout(myform)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(mygroupbox)
        scroll.setWidgetResizable(True)
#        scroll.setFixedHeight(400)
        scroll.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll)

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window(25)
    window.setGeometry(500, 300, 300, 400)
    window.show()
    sys.exit(app.exec_())