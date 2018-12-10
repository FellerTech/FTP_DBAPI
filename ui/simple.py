#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Interactive DB Application

This app uses PyQt5 to generate an interactive database interface. It
assumes that a template is provided with the following format

types: int, double, string, dictionary, array

Author: Steve Feller
Last edited: November 2018
"""

import sys
import argparse
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QMessageBox, QApplication, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import pyqtSlot

version = "0.0.1.0"

##
# \brief This class makes a generic viewer. 
#
"""
-------------------------------
| URI              Collection | Header
-------------------------------
|                             |
|                             |
|                             | Body
|                             |
|                             |
-------------------------------
|                    EXIT     | Footer
-------------------------------
"""
##
# \brief This is the main viewer.
class Viewer( QWidget ):
    def __init__(self):
        super().__init__()

        self.init()

    ##
    # \brief creates a view based on the available information
    def createView(self):
        print("Create a view here")

    ##
    # \brief creates the top line in the window
    # This includes the URI of the database and collection
    def createHeader(self):
        #Create the header layout
        self.headerLayout = QHBoxLayout()

    ##
    # \brief Function that handles an exit event
    def exitButtonPressEvent( self ):
        self.close()

    ##
    # \brief creates the bottom of the window.
    # This includes the exit button
    def createFooter(self):
        #This button will exit when pressed
        self.exitBtn = QPushButton('Exit', self )
        self.exitBtn.setToolTip('Exit Application')
        self.exitBtn.resize(self.exitBtn.sizeHint())
        self.exitBtn.clicked.connect( lambda: self.exitButtonPressEvent())

        #The footer contains the exit button
        self.footerLayout = QHBoxLayout()
        self.footerLayout.addStretch(1)
        self.footerLayout.addWidget(self.exitBtn);


    ##
    # \brief update the UI on given info
    #
    # The UI has three parts
    #  - header - This is the top line of the UI including title, etc.
    #  - body   - This is where the work is done
    #  - footer - Theis contains the top-level interactions (exit button)
    def createBody(self):
        #Create the body layout
        self.bodyLayout  = QVBoxLayout()
        self.bodyLayout.addStretch(1)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addLayout(self.bodyLayout)
        self.mainLayout.addLayout(self.footerLayout)
        self.setLayout( self.mainLayout )

    ##
    # \brief initialization function
    def init(self):
        #Determine screen settings
        geo = self.frameGeometry()
        self.width  = QDesktopWidget().availableGeometry().width();
        self.height = QDesktopWidget().availableGeometry().height();

        #creat the header and the footer
        self.createHeader()
        self.createFooter()

        self.createBody()

        #Define window parameters
        self.resize(self.width, self.height )
        self.setWindowTitle("Aqueti Database Viewer")
        self.show()


def main():
    
    # parse command line arguments
    parser = argparse.ArgumentParser(description='AWARE Database Script') 
    parser.add_argument('-v', action='store_const', dest='version', const='True', help='Prints the software version and exits') 
    parser.add_argument('-test', action='store_const', dest='test', const='True', help='run unit tests') 
    args=parser.parse_args()

    #If version, print the version and exit
    if args.version:
        print("SmartWidget version: "+version)
        exit(1)
   
    app = QApplication( sys.argv )
    window = Viewer()

    #If test, use the integrated test file
    if args.test:
        print("Test application")





    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
