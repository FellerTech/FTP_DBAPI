#!/usr/bin/python3
# -*- coding: utf-8 -*-

version="0.0.1.0"

"""
Widgets

Arrays and objects require new layouts?

object.key
object.value
object.template

template:
- type: type of value 
   "type": int, string, float, list, dict, undefined

an undefined type can be anything, but it will not be included in the interface (although it may be displayed as a string)


#example for list
{
   "value":<value>,
   "template":{
      "type":"list",
      "template:"{
         "key":<name>
         "type":<type>
      }
   }

}

"""
import argparse
import sys
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QMessageBox, QApplication, QVBoxLayout, QHBoxLayout, QDesktopWidget, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSlot
from SmartType import SmartType

class SmartWidget(SmartType):
   def __init__(self):
       SmartType.__init__(self)
#       SmartType.__init__(self)
       return 

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] template Json object that defines what the object may contain
   def init(self, key, value, template):
       self.key      = key
       if not SmartType.setTemplate( self, template ):
           return False

       if not SmartType.setValue(self, value):
           return False


       #Create Label
       label = QLabel()
       label.setText(str(self.key)+" : ")

       #Determine what type of data

       #default is for it to be a text box 
       self.widget = QLineEdit()
       self.ss = self.widget.styleSheet()
       self.valid = True
       self.widget.setText(str(value))
       self.widget.editingFinished.connect( lambda: self.validate() )

       #create layout
       self.layout = QHBoxLayout()
       self.layout.addWidget( label )
       self.layout.addWidget( self.widget )
      
       return self

   ##
   # \brief Callback to handle changes
   def validate(self):
       text = self.widget.text()

       #If we failed, set background as pink and state to invalid
       if not self.setStringAsValue( text ):
           print( "Invalid field. Type not "+self.template["type"])
           self.widget.setAutoFillBackground(True)
           self.widget.setStyleSheet("QLineEdit{background:pink;}")
           self.valid = False
       else:
           self.widget.setAutoFillBackground(False)
           self.widget.setStyleSheet(self.ss)
           self.valid = True


class unitTestViewer( QWidget ):
   def __init__(self):
       ###############
       # Create viewing application
       ###############
       super().__init__()
       #Determine screen settings
       geo = self.frameGeometry()
       self.width  = QDesktopWidget().availableGeometry().width();
       self.height = QDesktopWidget().availableGeometry().height();

       #Define window parameters
       self.resize(self.width*.75, self.height*.75 )
       self.setWindowTitle("SmartWidget unit test")
       self.show()


       self.mainLayout = QVBoxLayout()
       self.setLayout( self.mainLayout )

       #Create title
       self.titleLayout = QHBoxLayout()
       self.titleLayout.addStretch(1)
       title = QLabel()
       title.setText("SmartWidget Unit Test")
       self.titleLayout.addWidget(title)
       self.titleLayout.addStretch(1)
       self.mainLayout.addLayout( self.titleLayout )


   def test(self):

       ###############
       #Test strings
       ###############
       tplate={} 
       tplate["key"] = "string"
       tplate["type"]="string"

       widget = SmartWidget()

       widget.init("string", "test", tplate)
       if widget is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget.layout)

       #Check to make sure we have the expected value
       value = widget.value
       if value != "test":
           print("String value mismatch("+str(value))
           result = false


       ###############
       #Test Integers
       ###############
       tplate2={} 
       tplate2["key"] = "integer"
       tplate2["type"]="integer"

       widget2 = SmartWidget()

       widget2.init("int", 2, tplate2)
       if widget2 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget2.layout)

       #Check to make sure we have the expected value
       value = widget2.value
       if value != 2:
           print("String value mismatch: "+str(value))
           return False


       ###############
       #Test Floats
       ###############
       tplate3={} 
       tplate3["key"] = "float"
       tplate3["type"]="float"

       widget3 = SmartWidget()

       widget3.init("float", 2.1, tplate3)
       if widget3 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget3.layout)

       #Check to make sure we have the expected value
       value = widget3.value
       if value != 2.1:
           print("String value mismatch: "+str(value))
           return False

       ###############
       #Test Bools
       ###############
       tplate={} 
       tplate["key"] = "bool"
       tplate["type"]="bool"

       widget4 = SmartWidget()
       widget4.init("bool", True, tplate)
       if widget4 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget4.layout)

       #Check to make sure we have the expected value
       value = widget4.value
       if value != True:
           print("String value mismatch: "+str(value))
           return False

       ###############
       #Test Lists
       ###############
       tplate={} 
       tplate["key"] = "list"
       tplate["type"]="bool"

       widget4 = SmartWidget()
       widget4.init("bool", True, tplate)
       if widget4 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget4.layout)

       #Check to make sure we have the expected value
       value = widget4.value
       if value != True:
           print("String value mismatch: "+str(value))
           return False

       ####
       #Add stretch to push all entries to the top
       ####
       self.mainLayout.addStretch(1)


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='AWARE Database Script') 
    parser.add_argument('-v', action='store_const', dest='version', const='True', help='Prints the software version')   
    args=parser.parse_args()
    
    #If version, print the version and exit
    if args.version:
        print("SmartWidget version: "+version)
        exit(1)
        
    app = QApplication( sys.argv )
    window = unitTestViewer()
    window.test()

    sys.exit(app.exec_())

