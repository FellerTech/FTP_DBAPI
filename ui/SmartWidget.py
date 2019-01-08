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
       self.value=""
       return 

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] template Json object that defines what the object may contain
   def init(self, key, value, template = None):
       #For standard types, do the following:
       SmartType.__init__(self, key, value, template )


       #Set our key to the appropriate value
       self.key = key                                      #!< The is the key descriptor for object
       self.layout = QHBoxLayout()                         #!< Display out.
       self.components = []                                #!< Sub components

       #Create Label
       label = QLabel()
       label.setText(str(self.key)+" : ")
       self.layout.addWidget( label )

       #Check if we have a defined template
       if template != None:
          #If we are a list, create a vertical layout and add subwidgets. Each subwidget
          #must have a specified type
          if template["type"] == "list":
              #If we have a sub-template, we can create objects for a layout
              subLayout = QVBoxLayout()
              if "template" in template:
                  count = 0
                  for item in value:
                      widget = SmartWidget().init(count, item, template["template"])

                      if widget == False:
                          print("Error!")
                      else:
                          self.components.append(widget) 
                          subLayout.addLayout( widget.layout ) 
                          self.layout.addLayout( subLayout) 
                          self.components.append(widget) 
                          count = count + 1

          #If we are a dict, create a vertical layout and add subwidgets
          elif template["type"] == "dict":
              self.subLayout = QVBoxLayout()

              #If we have a sub-template, we can create objects for a layout
              subLayout = QVBoxLayout()
              if "template" in template:
                  for k,v in value.items():
                      print("ADDING LAYOUT: "+k+" with value: "+ str(v))
                      self.widget = SmartWidget().init(k, v, template["template"])
                      self.components.append(self.widget)
                      subLayout.addLayout( self.widget.layout )
                      self.layout.addLayout( subLayout)

          else:
              #default is for it to be a text box 
              self.widget = QLineEdit()
              self.ss = self.widget.styleSheet()
              self.valid = True
              self.widget.setText(str(value))
              self.widget.editingFinished.connect( lambda: self.validate() )

              #create layout
              self.layout.addWidget( self.widget )
       else:
           if( isinstance( value, list )):
              subLayout = QVBoxLayout()
              count = 0
              for item in value:
                  widget = SmartWidget().init(count, item)
                  if widget is False:
                      print( "Unable to create string widget. Failure")
                      return False

                  subLayout.addLayout( widget.layout)
                  count = count + 1
              subLayout.addStretch(1)
              self.layout.addLayout( subLayout)

           if( isinstance( value, dict)):
              subLayout = QVBoxLayout()
              print( str(value))
              for k, v in value.items():
                 widget = SmartWidget().init(k,v, )
                 if widget is False:
                     print( "Unable to create string widget. Failure")
                     return False

                 subLayout.addLayout( widget.layout)
              subLayout.addStretch(1)
              self.layout.addLayout( subLayout)

           else:
              #TODO: Iterate through and generate sub items
              self.value = value;
              self.widget = QLabel()
              self.widget.setText( str(value))
              self.layout.addWidget( self.widget )
       self.layout.addStretch(1)

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

   ##
   #\brief function to get the value.
   #
   # For complex types, this function will build hte the value recursively
   def getValue(self):
       if self.template == None:
          try:
              return self.value
          except:
              return ""
       elif self.template["type"] == "dict":
           print(str(self.key)+" dict value")
           value = {}
           for item in self.components:
               print("Getting for: "+item.key)
               value[item.key] = item.getValue()
           return value
       elif self.template["type"] == "list":
           value = []
           for item in self.components:
               value.append(item.getValue())
           return value
       else:
           print(self.key+" Returning: "+str(self.value))
           return self.value


class unitTestViewer( QWidget ):
   def __init__(self):
       ###############
       # Create viewing application
       ###############
       super().__init__()
       #Determine screen settings
       geo         = self.frameGeometry()
       self.width  = QDesktopWidget().availableGeometry().width();
       self.height = QDesktopWidget().availableGeometry().height();

       #Define window parameters
       self.resize(self.width*.5, self.height*.5 )
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

   ###
   # \brief Test function
   def test(self):

       ###############
       #Test strings
       ###############
       widget = SmartWidget().init("string", "test", {"type":"string"})
       if widget is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget.layout)

       #Check to make sure we have the expected value
       value = widget.getValue()
       if value != "test":
           print("String value mismatch("+str(value))
           result = false


       ###############
       #Test Integers
       ###############
       widget2 = SmartWidget().init("integer", 2, {"type":"integer"})
       if widget2 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget2.layout)

       #Check to make sure we have the expected value
       value = widget2.getValue()
       if value != 2:
           print("Integer value mismatch: "+str(value))
           return False

       ###############
       #Test Floats
       ###############
       widget3 = SmartWidget().init("float", 2.1, {"type":"float"})
       if widget3 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addLayout( widget3.layout)

       #Check to make sure we have the expected value
       value = widget3.getValue()
       if value != 2.1:
           print("Float value mismatch: "+str(value))
           return False

       ###############
       #Test Bools
       ###############
       widget4 = SmartWidget().init("bool", True, {"type":"bool"})
       self.mainLayout.addLayout( widget4.layout)

       #Check to make sure we have the expected value
       value = widget4.getValue()
       if value != True:
           print("Bool value mismatch: "+str(value))
           return False
  
       ###############
       #Test Lists
       ###############
       #Test uneditable list
       data = ["abc", 2, 3.2, 4]
       widget5 = SmartWidget().init("list", data)
       self.mainLayout.addLayout( widget5.layout)

       #Test editable
       data2 = [1,2,3,4]
       widget6 = SmartWidget().init("list", data2, {"type":"list","template":{"type":"integer"}})
       self.mainLayout.addLayout( widget6.layout)
       #Check to make sure we have the expected value
#       value = widget5.getValue()
#       if value != data:
#           print("List value mismatch: "+str(value))
#           return False
      

       ###############
       #Test Dicts
       ###############
       #Test uneditable list
       data = {"key1":"test1", "key2":"test2"}
       self.widget7 = SmartWidget().init("read only dict", data)
       self.mainLayout.addLayout( self.widget7.layout)

       #Test editable
       self.widget8 = SmartWidget().init("dict", data, {"type":"dict","template":{"type":"string"}})
       self.mainLayout.addLayout( self.widget8.layout)


       ###############
       # Check all
       ###############
       print("Creating widget 9")
       template={"type":"list","template":{"type":"dict","template":{"type":"integer"}}}
       value = [{"value1":1, "value2":2},{"value3":3, "value4":4}]
       self.widget9 = SmartWidget().init("Test2",value,template)
       self.mainLayout.addLayout( self.widget9.layout )
    

       ####
       #Add stretch to push all entries to the top
       ####
       self.mainLayout.addStretch(1)

       ###
       # Add a check button
       ###
       self.testButton = QPushButton('Test',self)
       self.testButton.clicked.connect( lambda: self.submitButtonPressEvent())
       self.mainLayout.addWidget( self.testButton )

   def submitButtonPressEvent(self):
       print("SUBMIT")
       print( self.widget9.getValue())





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

    #Check individual components
    window.test()



    

    sys.exit(app.exec_())

