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
object.schema

schema:
- type: type of value 
   "type": int, string, float, list, dict, undefined

an undefined type can be anything, but it will not be included in the interface (although it may be displayed as a string)


#example for list
{
   "value":<value>,
   "schema":{
      "type":"list",
      "schema:"{
         "key":<name>
         "type":<type>
      }
   }

}

{
   value:<value>,
   schema: {
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
class ObjectDialog(QDialog):
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
       tplate["bsonType"] = mytype
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
   # \param [in] schema Json object that defines what the object may contain
   def init(self, key, value, schema = None, parent=None):
       self.parent = parent 

       #For standard types, do the following:
       SmartType.__init__(self, key, value, schema )

       #Set our key to the appropriate value
       self.layout = QHBoxLayout()                         #!< Display out.
       self.frame = QFrame ()                              #!< Frame around entry

       self.frame.setLayout(self.layout)
       self.frame.adjustSize()
       self.frame.setFrameStyle( 1 )
       self.frame.setLineWidth(1)
       
       #DEBUG 
       self.noDraw = False

       self.setSchema(schema)
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

       #Check if we have a defined schema
       #No schema is provided
       if self.schema == None:
           if self.value == None:
              print("No value or schema provided")
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
       #We have a schema. Now we operate based on type
       else:
          """
          #Check if we have a specific editable flag
          try:
             if isinstance(self.schema["editable"], bool ):
                self.editable = self.schema["editable"]
          except:
             pass
          
          """
          #If we are a list, create a vertical layout and add subwidgets. Each subwidget
          #must have a specified type
          if self.schema["bsonType"] == "list" or self.schema["bsonType"] == "object":
              """
              #Eliminate mismatch between types
              if self.value is not None:
                 if isinstance( self.value, list) and not self.schema["type"] == "list":
                    print("Value "+self.value" type doest not match schema type of "+str(self.schema["type"])

              if self.value is not None and not isinstance(self.value,list) and not isinstance(self.value, dict):
                  print("Value "+self.value+" Type does not match schema!"+str(self.schema))
                  return False

              """
              #See if we have write permissions"
              #If we have a sub-schema, we can create objects for a layout
              dataLayout = QHBoxLayout()
              dataFrame  = QFrame()
              subLayout = QVBoxLayout()

              #Create an array of keys. For a list, the array is string represetnations of integers
              array = []
              if self.value is not None: 
                  if self.schema["bsonType"] == "list":
                      array = range( 0, len(self.value)) 
                  else:
                      array = list(self.value.keys())
              else:
                   if self.schema["bsonType"] == "list":
                       array = []
                   else:
                       try:
                           keys = list(self.schema["properties"].keys());

                           array = list(keys)
                       except:
                           print("Trying object key error")
                           array = []

              #The work is done here.
              count = 0
              print("Keys: "+str(array))
              print(self.key+" schema:"+str(self.schema))
              for item in array:
                  if self.value == None:
                     self.value = {}
                  if item not in self.value:
                      self.value[item] = None
                  #draw a dictionary item
                  if self.schema["bsonType"]== "object":
                      if item not in self.schema["properties"]:
                          self.schema["properties"][item] = {}
                      if self.value[item] == "" or self.value[item] == None:
                          print("no value")
                          widget = SmartWidget().init(item, None, self.schema["properties"][item], self)
                      else:
                          widget = SmartWidget().init(item, self.value[item], self.schema["properties"][item], self)
                  #otherwise, it's a list
                  else:
                      widget = SmartWidget().init(item, self.value[item], self.schema, self)

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
          print( "Invalid field. Type not "+self.schema["bsonType"])
          self.widget.setAutoFillBackground(True)
          self.widget.setStyleSheet("QLineEdit{background:pink;}")
          self.valid = False
       else:
          self.widget.setAutoFillBackground(False)
          self.widget.setStyleSheet(self.ss)
          self.valid = True

          #Tell our parent to update
          if self.parent != None:
             self.parent.updateChild(self.key, self.value, self.schema)

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
      if self.schema == None:
          print("Cannot add to a list without a schema")
          return

      if self.schema["bsonType"] == "list":
         self.value.append(None)
         print("New value: "+str(self.value))
         if self.parent is not None:
             self.parent.updateChild(self.key, None)
         else:
            self.draw()
      elif self.schema["bsonType"] == "object":
         objectDialog = ObjectDialog(self.updateChild)
      else:
         print("addCallback schema: "+str(self.schema))

   ##
   #\brief updates the children of this complex type
   def updateChild( self, key, value, schema=None ):
       print(self.key+" is updating child "+str(key)+" with value "+str(value)+", schema:"+str(schema))

       #if we are a list, check for the specified item
       if isinstance( self.value, list ):
           self.value[key] = value
       elif isinstance( self.value, dict ):
           self.value[key] = value

       if self.schema["bsonType"] == "object":
           if "properties" not in self.schema:
              self.schema["properties"] =  {}

           self.schema["properties"][key] = schema
       else:
           print("Not a object or list. No cannot update child")
#           return False

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
       self.testWidgets = []
       ###############
       #Test strings
       ###############
       schema = {"bsonType":"string", "description":"string test"}
       widget1 = SmartWidget().init("string", "test", schema )
       if widget1 is False:
           print( "Unable to create string widget. Failure")
           return False

       self.mainLayout.addWidget(widget1.frame)
       self.testWidgets.append(widget1)

       schema = {"bsonType":"double", "description":"double test"}
       widget2 = SmartWidget().init("double", 1.0, schema )
       if widget2 is False:
           print( "Unable to create double widget. Failure")
           return False

       self.mainLayout.addWidget(widget2.frame)
       self.testWidgets.append(widget2)

       schema = {"bsonType":"bool", "description":"bool test"}
       widget3 = SmartWidget().init("bool", True, schema )
       if widget3 is False:
           print( "Unable to create bool widget. Failure")
           return False

       self.mainLayout.addWidget(widget3.frame)
       self.testWidgets.append(widget3)

         
       schema = {"bsonType":"int", "description":"int test"}
       widget4 = SmartWidget().init("int32", 12, schema )
       if widget4 is False:
           print( "Unable to create int widget. Failure")
           return False

       self.mainLayout.addWidget(widget4.frame)
       self.testWidgets.append(widget4)


       schema = {"bsonType":"object", "properties":{ "string1": { "bsonType":"string", "description":"string 1"}}, "description":"object test" }
       widget5 = SmartWidget().init("object", None, schema )
       if widget5 is False:
           print( "Unable to create object widget. Failure")
           return False
       self.mainLayout.addWidget(widget5.frame)
       self.testWidgets.append(widget5)

       schema = {"bsonType":"array", "items":{ "bsonType":"double"}}
       widget6 = SmartWidget().init("array", None, schema )
       if widget6 is False:
           print( "Unable to create array widget. Failure")
           return False
       self.mainLayout.addWidget(widget6.frame)
       self.testWidgets.append(widget6)


   def submitButtonPressEvent(self):
       print("SUBMIT")
       i = 0
       for item in self.testWidgets:
          print(str(i) + " -  " + str( item.getValue()))
          i = i +1

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

