#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Steps:
    - Draw items
    - Handle remove requests
    - redraw items 
    - extract data
"""

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
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QMessageBox, QApplication, QVBoxLayout, QHBoxLayout, QDesktopWidget, QLabel, QLineEdit, QFrame
from PyQt5.QtCore import pyqtSlot
from SmartType import SmartType

class SmartWidget(SmartType):
   def __init__(self):
       self.value=""
       self.widgets={}
       self.frame = QFrame()
       return 

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] template Json object that defines what the object may contain
   def init(self, key, value, template = None, removeCallback=None):
       self.callback = removeCallback

       #For standard types, do the following:
       SmartType.__init__(self, key, value, template )


       #Set our key to the appropriate value
       self.key = key                                      #!< The is the key descriptor for object
       self.editable = True                                #!< Flag to indicate if editing is ok
       self.layout = QHBoxLayout()                         #!< Display out.
       self.frame = QFrame ()                              #!< Frame around entry

       self.draw()
       self.template = template
       self.value = value;

       return self

   def draw(self):
       #Create Label
       label = QLabel()
       label.setText(str(self.key)+" : ")
       self.layout.addWidget( label )

       #Check if we have a defined template
       if self.template != None:
          #Check if we have a specific editable flag
          try:
             if isinstance(self.template["editable"], bool ):
                self.editable = self.template["editable"]
          except:
             pass

          #If we are a list, create a vertical layout and add subwidgets. Each subwidget
          #must have a specified type
          if self.template["type"] == "list":
              #See if we have write permissions"
              #If we have a sub-template, we can create objects for a layout
              self.subLayout = QVBoxLayout()
              if "template" in self.template:
                  count = 0
                  for item in self.value:
                      widget = SmartWidget().init(count, item, self.template["template"], self.removeCallback)

                      if widget == False:
                          print("Error!")
                      else:
#                          self.components.append(widget) 

                          self.subLayout.addWidget( widget.frame ) 
                          self.layout.addLayout( self.subLayout) 
#                          self.layout.addWidget(widget.frame)

                          #If editable, this each sub-component can be removed
#                          self.components.append(widget) 
                          count = count + 1

          #If we are a dict, create a vertical layout and add subwidgets
          elif self.template["type"] == "dict":
              if "template" in self.template:
                  subLayout = QVBoxLayout()
                  for k,v in self.value.items():
                      widget = SmartWidget().init(k, v, self.template["template"], self.removeCallback )
                      subLayout.addWidget(widget.frame)
                  subFrame = QFrame()
                  subFrame.setLayout(subLayout)
                  self.layout.addWidget(subFrame)
                      
          else:
              #default is for it to be a text box 
              self.widget = QLineEdit()
              self.ss = self.widget.styleSheet()
              self.valid = True
              self.widget.setText(str(self.value))
              self.widget.editingFinished.connect( lambda: self.validate() )

              #create layout
              self.layout.addWidget( self.widget )


          #Add remove button
          self.removeButton = QPushButton("-")
          self.removeButton.clicked.connect( lambda: self.removeButtonPressEvent())
          self.layout.addWidget( self.removeButton )
       else:
           if( isinstance( self.value, list )):
              self.subLayout = QVBoxLayout()
              count = 0
              for item in self.value:
                  widget = SmartWidget().init(count, item)
                  if widget is False:
                      print( "Unable to create string widget. Failure")
                      return False

                  self.subLayout.addLayout( widget.layout)
                  count = count + 1
              self.subLayout.addStretch(1)
              self.layout.addLayout( self.subLayout)

           if( isinstance( self.value, dict)):
              self.subLayout = QVBoxLayout()
              print( str(self.value))
              for k, v in value.items():
                 widget = SmartWidget().init(k,v, )
                 if widget is False:
                     print( "Unable to create string widget. Failure")
                     return False

              self.draw()


           else:
              #TODO: Iterate through and generate sub items
              self.widget = QLabel()
              self.widget.setText( str(self.value))
              self.layout.addWidget( self.widget )

       self.layout.addStretch(1)

       #Create frame
       self.frame.setLayout(self.layout)
       self.frame.adjustSize()
       self.frame.setFrameStyle( 1 )
       self.frame.setLineWidth(1)
       
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

   def getKey():
       return self.key

   ##
   # \brief callback called by a child to remove itself
   def removeCallback(self, key ):
       print(self.key+" remove callback for "+str(key))

       #remove key
       del self.widgets[key]
       del self.value[key]

       #recreate the layout
       self.draw()

       return 

   ##
   # Callback for removing an element frmo an array or a dictionary
   def removeButtonPressEvent( self):
       print("Request to remove "+str(self.key))

       if self.callback != None:
          print("Callback to remove "+str(self.key))
          self.frame.deleteLater()
          self.callback( self.key)
       else:
          print("No callback specified. Unable to remove")

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

#       self.mainLayout.addLayout( widget.layout)
       self.mainLayout.addWidget(widget.frame)

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

#       self.mainLayout.addLayout( widget2.layout)
       self.mainLayout.addWidget( widget2.frame)

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

       #self.mainLayout.addLayout( widget3.layout)
       self.mainLayout.addWidget(widget3.frame)

       #Check to make sure we have the expected value
       value = widget3.getValue()
       if value != 2.1:
           print("Float value mismatch: "+str(value))
           return False

       ###############
       #Test Bools
       ###############
       widget4 = SmartWidget().init("bool", True, {"type":"bool"})
#       self.mainLayout.addLayout( widget4.layout)
       self.mainLayout.addWidget(widget4.frame)

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
#       self.mainLayout.addLayout( widget5.layout)
       self.mainLayout.addWidget(widget5.frame)

       #Test editable
       data2 = [1,2,3,4]
       widget6 = SmartWidget().init("list", data2, {"type":"list","template":{"type":"integer"}})
#       self.mainLayout.addLayout( widget6.layout)
       self.mainLayout.addWidget(widget6.frame)

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
#       self.mainLayout.addLayout( self.widget7.layout)
       self.mainLayout.addWidget(self.widget7.frame)

       #Test editable
       self.widget8 = SmartWidget().init("dict", data, {"type":"dict","template":{"type":"string"}})
#       self.mainLayout.addLayout( self.widget8.layout)
       self.mainLayout.addWidget(self.widget8.frame)


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

