#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 12:43:25 2021

@author: dpetrovykh
"""

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)

class MplCanvas(FigureCanvas):
    
    def __init__(self, parent = None, width=10, height=10, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.ax = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)