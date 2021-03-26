#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 13:18:29 2021

@author: dpetrovykh
"""

from PyQt5 import QtCore, QtWidgets, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        # Run Initialization of parent class
        super(MainWindow, self).__init__(parent)
        # Create a central widget which other functional widgets can be added into
        self.central_widget = QtWidgets.QStackedWidget()
        # foramlly add central widget as the centralWidget
        self.setCentralWidget(self.central_widget)
        # Create an instance of the login widget, supplying self as the parent optional argument
        login_widget = LoginWidget(self)
        # Link the button within the LoginWidget with the self.login function
        login_widget.button.clicked.connect(self.login)
        # Add the login_widget to the central widget
        self.central_widget.addWidget(login_widget)
        
    def login(self):
        # Create instance of logged widget
        logged_in_widget = LoggedWidget(self)
        # Add logged iwdget to central widget
        self.central_widget.addWidget(logged_in_widget)
        # Make the recently-added logged widget the current widget in the central widget.
        self.central_widget.setCurrentWidget(logged_in_widget)


class LoginWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        # Run Initializzation of parent class
        super(LoginWidget, self).__init__(parent)
        # Create a horizontal layout
        layout = QtWidgets.QHBoxLayout()
        # Create a button
        self.button = QtWidgets.QPushButton('Login')
        #Add button to the layout
        layout.addWidget(self.button)
        # Set the layout to be the current one.
        self.setLayout(layout)
        # you might want to do self.button.click.connect(self.parent().login) here


class LoggedWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LoggedWidget, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel('logged in!')
        layout.addWidget(self.label)
        self.setLayout(layout)



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()