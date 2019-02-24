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

{
   value:<value>,
   template: {
      type:"dict",
      items: {
         "a":{ 
         }
      }
   }
}

"""
import argparse
import sys
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QMessageBox, QApplication, QVBoxLayout, QHBoxLayout, QDesktopWidget, QLabel, QLineEdit, QFrame, QDialog, QComboBox, QRadioButton, QCheckBox
from PyQt5.QtCore import pyqtSlot
from SmartType import SmartType

class IndexButton(QPushButton):
    def __init__(self, value, index, callback):
        QPushButton.__init__(self, value)
        self.index =index
        self.callback = callback
        self.clicked.connect( lambda: self.pressEvent())


    def pressEvent(self):
        self.callback( self.index)

##
# \brief dialog for modifying dictionaries
class DictDialog(QDialog):
    def __init__(self, callback):
       super().__init__()

       self.callback = callback

       self.layout = QVBoxLayout()
       self.keyLayout = QHBoxLayout()
       keyLabel = QLabel()
       keyLabel.setText("key")
       self.keyLayout.addWidget( keyLabel )


       #default is for it to be a text box 
       self.key = QLineEdit()
       self.ss = self.key.styleSheet()
       self.keyLayout.addWidget(self.key)

       typeLayout = QHBoxLayout()
       typeLabel = QLabel()
       typeLabel.setText("type")
       typeLayout.addWidget(typeLabel)

       self.types = QComboBox()
       self.types.addItems(SmartType.types)
       typeLayout.addWidget(self.types)

       reqLayout = QHBoxLayout()
       reqLabel = QLabel()
       reqLabel.setText("required")
       self.reqCheck = QCheckBox()
       reqLayout.addWidget(reqLabel)
       reqLayout.addWidget(self.reqCheck)

       #Create submit button
       controlLayout = QHBoxLayout()
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
       controlLayout.addWidget(submitButton)
       cancelButton = QPushButton("cancel")
       cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
       controlLayout.addWidget(cancelButton)

       #create layout
       keyFrame = QFrame()
       keyFrame.setLayout(self.keyLayout)
       typeFrame = QFrame()
       typeFrame.setLayout(typeLayout)
       reqFrame = QFrame()
       reqFrame.setLayout( reqLayout )
       controlFrame = QFrame()
       controlFrame.setLayout(controlLayout)

       self.layout = QVBoxLayout()
       self.layout.addWidget(keyFrame)
#       self.layout.addWidget(valueFrame)
       self.layout.addWidget(typeFrame)
       self.layout.addWidget( reqFrame )
       self.layout.addWidget( controlFrame)
       self.setLayout(self.layout)

       self.show()

       self.exec_()

    def submitButtonPressEvent(self):
       key = self.key.text()
       mytype = self.types.currentText()
       req = self.reqCheck.isChecked()

       if key == "":
           print("Must enter a key")
           return
       tplate = {}
       tplate["type"] = mytype
       tplate["required"] = req
#       tplate["items"] = {}

       self.callback(key, None, tplate )

       self.done(True)


class SmartWidget(SmartType):
   def __init__(self):
       self.value=""
       self.widgets={}
       self.frame = QFrame()
#       self.components = {}
       return 

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] template Json object that defines what the object may contain
   def init(self, key, value, template = None, parent=None):
       self.parent = parent 

       #For standard types, do the following:
       SmartType.__init__(self, key, value, template )

       #Set our key to the appropriate value
       self.layout = QHBoxLayout()                         #!< Display out.
       self.frame = QFrame ()                              #!< Frame around entry

       self.frame.setLayout(self.layout)
       self.frame.adjustSize()
       self.frame.setFrameStyle( 1 )
       self.frame.setLineWidth(1)
       
       #DEBUG 
       self.noDraw = False

       self.setTemplate(template)
       self.setValue(value)
       self.draw()

       return self

   ##
   # \brief Function to draw the frame
   def draw(self):
       #Remove all widgets
       while self.layout.count():
           item = self.layout.takeAt(0)
           widget = item.widget()
           if widget is not None:
               widget.deleteLater()

       #Create Label
       label = QLabel()
       label.setText(str(self.key)+" : ")
       self.layout.addWidget( label )

       #Check if we have a defined template
       #No template is provided
       if self.template == None:
           if self.value == None:
              print("No value or template provided")
              return
           else:
              self.widget = QLabel()
              self.widget.setText( str(self.value))
              self.layout.addWidget( self.widget )
          
           """
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

           else:
              #Generate all basic types. If no value provided, leave field blank
              self.widget = QLabel()
              if self.value is not None:
                  print("None value detected")
                  self.widget.setText( str(self.value))
              self.layout.addWidget( self.widget )
          
          """
       #We have a template. Now we operate based on type
       else:
          """
          #Check if we have a specific editable flag
          try:
             if isinstance(self.template["editable"], bool ):
                self.editable = self.template["editable"]
          except:
             pass
          
          """
          #If we are a list, create a vertical layout and add subwidgets. Each subwidget
          #must have a specified type
          if self.template["type"] == "list" or self.template["type"] == "dict":
              """
              #Eliminate mismatch between types
              if self.value is not None:
                 if isinstance( self.value, list) and not self.template["type"] == "list":
                    print("Value "+self.value" type doest not match template type of "+str(self.template["type"])

              if self.value is not None and not isinstance(self.value,list) and not isinstance(self.value, dict):
                  print("Value "+self.value+" Type does not match template!"+str(self.template))
                  return False

              """
              #See if we have write permissions"
              #If we have a sub-template, we can create objects for a layout
              dataLayout = QHBoxLayout()
              dataFrame  = QFrame()
              subLayout = QVBoxLayout()

              #Create an array of keys. For a list, the array is string represetnations of integers
              array = []
              if self.value is not None: 
                  if self.template["type"] == "list":
                      array = range( 0, len(self.value)) 
                  else:
                      array = list(self.value.keys())
              else:
                   if self.template["type"] == "list":
                       array = []
                   else:
                       print("It's a dict, type is not a list"+str(self.template))
                       try:
                           print("Trying to get dict keys from the template"+str(self.template))
                           keys = list(self.template["items"].keys());
                           print("Keys: "+str(keys))

                           array = list(keys)
                       except:
                           print("Trying dict key error")
                           array = []

              #The work is done here.
              count = 0
              print("Keys: "+str(array))
              print(self.key+" template:"+str(self.template))
              for item in array:
                  if self.value == None:
                     self.value = {}
                  if item not in self.value:
                      self.value[item] = None
                  #draw a dictionary item
                  if self.template["type"]== "dict":
                      if item not in self.template["items"]:
                          self.template["items"][item] = {}
                      if self.value[item] == "" or self.value[item] == None:
                          print("no value")
                          widget = SmartWidget().init(item, None, self.template["items"][item], self)
                      else:
                          widget = SmartWidget().init(item, self.value[item], self.template["items"][item], self)
                  #otherwise, it's a list
                  else:
                      widget = SmartWidget().init(item, self.value[item], self.template, self)

                  if widget == False:
                      print("List Error!")
                  else:
                      #Add item to the component list
                      subLayout.addWidget(widget.frame)

                  #Create subframe
                  subFrame = QFrame()
                  subFrame.setLayout( subLayout)
                  subFrame.setFrameStyle( 1 )
                  subFrame.setLineWidth(1)

                  dataLayout.addWidget(subFrame)

              #Add a add button
              addButton = QPushButton("+")
              addButton.clicked.connect( lambda: self.addButtonPressEvent())
              dataLayout.addWidget(addButton)

              #Add remove button
              removeButton = IndexButton("-", self.key, self.removeCallback)
#             subLayout.addWidget( removeButton )
              count = count + 1
                     
              dataFrame.setLayout(dataLayout)
              self.layout.addWidget(dataFrame)

          # We're a basic type
          else:
              #default is for it to be a text box 
              self.widget = QLineEdit()
              self.ss = self.widget.styleSheet()
              self.valid = True
              if self.value != None:
                  self.widget.setText(str(self.value))
              self.widget.editingFinished.connect( lambda: self.validate() )

              #create layout
              self.layout.addWidget( self.widget )


       #Add remove button
       removeButton = IndexButton("-", self.key, self.removeCallback)
       self.layout.addWidget( removeButton )
                     
       self.layout.addStretch(1)

       return self


   ##
   # \brief Callback to handle changes
   def validate(self):
       text = self.widget.text()
       print("-----Validating "+self.key+" with text "+text)

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

          #Tell our parent to update
          if self.parent != None:
             self.parent.updateChild(self.key, self.value, self.template)

   ##
   #\brief function to get the value.
   #
   # For complex types, this function will build hte the value recursively
   def getValue(self):
       return self.value

   ##
   # \brief returns the key of the object
   def getKey():
       return self.key

   ##
   # \brief callback called by a child to remove itself
   def removeCallback(self, key ):
       print(self.key+" remove callback for "+str(key))

#       print("Removing key "+str(key)+" in "+str(self.components))
#       del self.components[str(key)]

       #remove key
       if isinstance( self.value, list ):
          del self.value[key]
 
       elif isinstance( self.value, dict ):
          print("Removing key: "+key)
          self.value.pop(key)
       else:
          print("Cannot remove item from unknown type")

       print(str(self.value))

       #Call the parents remove callback if available. If not, draw
       if self.parent is not None:
           self.parent.removeCallback(key)
#       if self.callback is not None:
#          self.callback(key)
       else:
           print(str(self.key)+" is drawing")
           self.draw()

       return 

   ##
   # \brief Callback to add an item to a list
   def addCallback(self):
      if self.template == None:
          print("Cannot add to a list without a template")
          return

      if self.template["type"] == "list":
         self.value.append(None)
         print("New value: "+str(self.value))
         if self.parent is not None:
             self.parent.updateChild(self.key, None)
         else:
            self.draw()
      elif self.template["type"] == "dict":
         dictDialog = DictDialog(self.updateChild)
      else:
         print("addCallback template: "+str(self.template))

   ##
   #\brief updates the children of this complex type
   def updateChild( self, key, value, template=None ):
       print(self.key+" is updating child "+str(key)+" with value "+str(value)+", template:"+str(template))

       #if we are a list, check for the specified item
       if isinstance( self.value, list ):
           self.value[key] = value
       elif isinstance( self.value, dict ):
           self.value[key] = value

       if self.template["type"] == "dict":
           if "items" not in self.template:
              self.template["items"] =  {}

           print("Old template: "+str(self.template))
           self.template["items"][key] = template
           print( "\nNewer template: "+str(self.template)+"\n")
       else:
           print("Not a dict or list. No cannot update child")
#           return False

       print("Draw template: "+str(self.template))
       self.draw()

   ##
   # Callback for removing an element frmo an array or a dictionary
   def removeButtonPressEvent( self, index):
       print("Request to remove "+str(index))

       print("Callback to remove "+str(self.key))
       if self.parent != None:
           self.frame.deleteLate()
           self.parent.removeCallback( self.key)
       else:
          print("No callback specified. Unable to remove")

   ##
   #\brief handle the addButton press event
   def addButtonPressEvent(self):
       self.addCallback()

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

       #Define window par meters
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
       """
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
       self.widget6 = SmartWidget().init("list", data2, {"type":"list","template":{"type":"integer"}})
#       self.mainLayout.addLayout( widget6.layout)
       self.mainLayout.addWidget(self.widget6.frame)

       """
       ###############
       #Test Dicts
       ###############
       #Test uneditable list
#       data = {"key1":"test1", "key2":1}
       data = {}
       template = {}
       template["type"] = "dict"
       t = {}
#       t["type"] = "string"
       tplate = None
#       tplate["key1"] = t
#       t["type"] = "integer"
#       tplate["key2"] = t
#       template["template"] = tplate


#       self.widget7 = SmartWidget().init("read only dict", data)
#       self.mainLayout.addWidget(self.widget7.frame)
       #Test editable
       self.widget8 = SmartWidget().init("NewDict", None, template)
       self.mainLayout.addWidget(self.widget8.frame)


       ###############
       # Check all
       ###############
       """
       print("Creating widget 9")
       template= { "type":"list", "template":{ "type":"dict", "template":{ "value1":"integer", "value2":"integer" } } }
       value = [{"value1":1, "value2":2},{"value3":3, "value4":4}]
       self.widget9 = SmartWidget().init("Test2",value,template)
       self.mainLayout.addLayout( self.widget9.layout )
       """

       ####
       #Add stretch to push all entries to the top
       ####
       self.mainLayout.addStretch(1)

       ###
       # Add a check button
       ###
       self.testButton = QPushButton('Submit',self)
       self.testButton.clicked.connect( lambda: self.submitButtonPressEvent())
       self.mainLayout.addWidget( self.testButton )

   def submitButtonPressEvent(self):
       print("SUBMIT")
       print( self.widget8.getValue())



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

