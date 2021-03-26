#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 12:51:39 2021

@author: dpetrovykh
"""
1
2
3
4
5
6
	
from PyQt5.uic import loadUiType
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('TestWindow.ui')
	
class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.fig_dict = {}
        
        self.mplfigs.itemClicked.connect(self.change_fig)
        fig = Figure()
        self.addmpl(fig)
    
    def change_fig(self, item):
        text = item.text()
        self.rmmpl()
        self.addmpl(self.fig_dict[text])
        
    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()   
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.mplvl.addWidget(self.toolbar)
	
    def rmmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()
 
    def add_fig(self,name, fig):
        self.fig_dict[name] = fig
        self.mplfigs.addItem(name)
        
if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets

    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot(np.random.rand(5))   
 
    fig2 = Figure()
    ax1f2 = fig2.add_subplot(121)
    ax1f2.plot(np.random.rand(5))
    ax2f2 = fig2.add_subplot(122)
    ax2f2.plot(np.random.rand(10))   
 
    fig3 = Figure()
    ax1f3 = fig3.add_subplot(111)
    ax1f3.pcolormesh(np.random.rand(20,20))   
 
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.add_fig('One plot', fig1)
    main.add_fig('Two plots', fig2)
    main.add_fig('Pcolormesh', fig3)
    main.show()
    # input()
    # main.rmmpl()
    # main.addmpl(fig2)
    sys.exit(app.exec_())