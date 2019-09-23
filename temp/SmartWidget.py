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
   "type": int, string, float, array, object, undefined

an undefined type can be anything, but it will not be included in the interface (although it may be displayed as a string)


#example for list
{
   "value":<value>,
   "schema":{
      "type":"array",
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
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QMessageBox, QApplication, QVBoxLayout, QHBoxLayout, QDesktopWidget, QLabel, QLineEdit, QFrame, QDialog, QComboBox, QRadioButton, QCheckBox, QScrollArea
from PyQt5.QtCore import pyqtSlot
from SmartType import SmartType

class IndexButton(QPushButton):
    def __init__(self, value, index, callback):
        QPushButton.__init__(self, value)
        self.index = index
        self.callback = callback
        self.clicked.connect( lambda: self.pressEvent())

    def pressEvent(self):
        self.callback( self.index)

##
# \brief dialog for modifying dictionaries
class ObjectDialog(QDialog):
    ##
    #\brief Initialization function for the object dialog
    #\param [in] callback callback for the submit function
    def __init__(self, callback):
       super().__init__()

       self.callback = callback
       self.layout = QVBoxLayout()

       #The value layout is used to 
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

       """
       reqLayout = QHBoxLayout()
       reqLabel = QLabel()
       reqLabel.setText("required")
       self.reqCheck = QCheckBox()
       reqLayout.addWidget(reqLabel)
       reqLayout.addWidget(self.reqCheck)
       """

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
       #reqFrame = QFrame()
       #reqFrame.setLayout( reqLayout )
       controlFrame = QFrame()
       controlFrame.setLayout(controlLayout)

       self.layout = QVBoxLayout()
       self.layout.addWidget(keyFrame)
       self.layout.addWidget(typeFrame)
       #self.layout.addWidget( reqFrame )
       self.layout.addWidget( controlFrame)
       self.setLayout(self.layout)

       self.show()

       self.exec_()

    def submitButtonPressEvent(self):
       key = self.key.text()
       mytype = self.types.currentText()
       #req = self.reqCheck.isChecked()

       if key == "":
           print("Must enter a key")
           eturn
       tplate = {}
       tplate["bsonType"] = mytype
       #tplate["required"] = req
#       tplate["items"] = {}

       self.callback(key, None, tplate )

       self.done(True)

##
# \brief dialog for modifying dictionaries
#
# TODO: Know supported types from template (if possible)
#       Select only from those. 
#       Value and validate type
#
class ArrayDialog(QDialog):
    def __init__(self, callback):
       super().__init__()

       self.callback = callback

       self.layout = QVBoxLayout()

       #Create an element with a value label followed by a text box        
       self.keyLayout = QHBoxLayout()
       keyLabel = QLabel()
       keyLabel.setText("key")
       self.keyLayout.addWidget( keyLabel )

       #Create the text box. The default is for it to be a text box 
       self.keyValue = QLineEdit()
       self.ss = self.keyValue.styleSheet()
       self.keyLayout.addWidget(self.keyValue)

       #The type layout is a horizontal box 
       typeLayout = QHBoxLayout()
       typeLabel = QLabel()
       typeLabel.setText("type")
       typeLayout.addWidget(typeLabel)

       #Crate a combobox to add a list of types to select from. This may need
       #to be based on the schema in the future 
       self.types = QComboBox()
       self.types.addItems(SmartType.types)
       typeLayout.addWidget(self.types)

       """
       #Add a button to indicate if it is a required key
       reqLayout = QHBoxLayout()
       reqLabel = QLabel()
       reqLabel.setText("required")
       self.reqCheck = QCheckBox()
       reqLayout.addWidget(reqLabel)
       reqLayout.addWidget(self.reqCheck)
       """

       #Create submit button
       controlLayout = QHBoxLayout()
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
       controlLayout.addWidget(submitButton)
       cancelButton = QPushButton("cancel")
       cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
       controlLayout.addWidget(cancelButton)

       #create layout
       valueFrame = QFrame()
       valueFrame.setLayout(self.keyLayout)
       typeFrame  = QFrame()
       typeFrame.setLayout(typeLayout)
       reqFrame   = QFrame()
       #reqFrame.setLayout( reqLayout )
       controlFrame = QFrame()
       controlFrame.setLayout(controlLayout)

       self.layout = QVBoxLayout()
       self.layout.addWidget( typeFrame)
       self.layout.addWidget( valueFrame)
       self.layout.addWidget( reqFrame )
       self.layout.addWidget( controlFrame)
       self.setLayout(self.layout)

       self.show()

       self.exec_()

    ##
    # \brief Handles ArrayDialog submit button press
    def submitButtonPressEvent(self):
       #key = self.key.text()
       mytype = self.types.currentText()
       req = self.reqCheck.isChecked()

       #if key == "":
       #    print("Must enter a key")
       #    return

       tplate = {}
       tplate["bsonType"] = mytype
       tplate["required"] = req
#       tplate["items"] = {}

       self.callback(key, None, tplate )

       self.done(True)
##
#\brief This class is used to draw a widget for a smart type
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
   # \param [in] schema Json object that defines what the object may contain
   # \return self reference
   #
   # This function is used to initalize a new smart widget with a new key-value
   # pair. If a schema is provided, it is used to ensure that the value is 
   # considered correct. The valid variable is set to True when the object has
   # a valid value
   #
   def init(self, key, value, schema = None, parent=None):
       self.parent = parent
       self.valid = False 

       #Initialize the underlying SmartType with input values
       SmartType.__init__(self, key, value, schema )

       #Set our key to the appropriate value
       self.layout = QHBoxLayout()                         #!< Display out.
       self.frame = QFrame ()                              #!< Frame around entry

       self.frame.setLayout(self.layout)
       self.frame.adjustSize()
       self.frame.setFrameStyle( 1 )
       self.frame.setLineWidth(1)
       
       self.draw()

       return self

   ##
   # \brief Function to draw the frame
   # SDF - handle arrays and objects
   def draw(self):
       #Remove all widgets from the current layout
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
       #If no schema is provided, the value is represnted in uneditable text form
       if self.schema == None:
           if self.value == None:
              print("No value or schema provided")
              return
           else:
              self.widget = QLabel()
              self.widget.setText( str(self.value))
              self.layout.addWidget( self.widget )
          
       #We have a schema. Now we operate based on type
       else:
          #If we are an array, 
          if self.schema["bsonType"] == "array":
              self.widget = QFrame()
              self.valid = True
              self.subLayout = QVBoxLayout()
              self.subWidgets = []

              if self.value != None:
                  count = 0
                  for item in self.value:
                     print(str(str(self.valid)+"schema for "+str(item)+" is "+str(self.schema["items"])))
                     subWidget = SmartWidget().init(str(count), item, self.schema["items"])
                     if subWidget != False:
                         self.subLayout.addWidget(subWidget.frame)
                         self.subWidgets.append(subWidget)
                         count = count + 1
                     else:
                         print("Failed to create a widget for "+str(item))
                         self.valid = False

                  print("added " + str(count) + " items")
              self.subLayout.addStretch(1)
              self.widget.setLayout(self.subLayout)
          
          elif self.schema["bsonType"] == "object":
              self.widget = QFrame()
              self.valid = True
              self.subWidgets = []
              
              self.subLayout = QVBoxLayout()

              if self.value != None:
                  for item in self.value:
#                     print("Item: "+str(item))
                     subWidget = SmartWidget().init(str(item), self.value[item], self.schema["items"])
                     if subWidget != False:
                         self.subLayout.addWidget(subWidget.frame)
                         self.subWidgets.append(subWidget)
                     else:
                         print("Failed to create a widget for "+str(v))
                         self.valid = False
                     
              self.subLayout.addStretch(1)
              self.widget.setLayout(self.subLayout)
             
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


       #Add remove button to allow people to remove values
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
   # For complex types, this function will build the the value recursively
   def getValue(self):
       if self.type == "array":
           value = []
           for item in self.subWidgets:
               #See if we're a smart widget
               try:
                  print("Trying to get value for "+str(item.getValue()))
                  value.append( item.getValue())
               except:
                  print("Value exception for "+str(item))
                  value.append( item.value)
           return value
         
       elif self.type == "object":
           value = {}
           for item in self.subWidgets:
               #See if we're a smart widget
               try:
                  print("Trying to get value for "+str(item.getValue()))
                  myValue = item.getValue()
                  value[item.key] = item.getValue()
               except:
                  print("Value exception for "+str(item))
                  value.append( item.value)
           return value
       #Compare types to validate
       else:
           if self.type == "string":
               self.setValue( self.widget.text())
           elif self.type == "int":
               try:
                   self.setValue( int(self.widget.text()))
               except:
                   print(self.widget.key+":"+self.widget.text()+" is not an integer")
           elif self.type == "number":
               try:
                   self.setValue( float(self.widget.text()))
               except:
                   print(self.widget.key+":"+self.widget.text()+" is not a number")
           elif self.type == "bool":
               if self.widget.text() == "True":
                  self.setValue(True) 
               else: 
                  self.setValue(False) 
           return self.value

   ##
   # \brief returns the key of the object
   def getKey(self):
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
   # 
   # This callback is used used to add an item to an array or object. This
   # function creates the appropriate dialog for each type
   def addCallback(self):
      if self.schema == None:
          print("Cannot add to a array without a schema")
          return

      if self.schema["bsonType"] == "array":
         arrayDialog = ArrayDialog(self.updateChild)
      
         """
         #check if we have a value. If not, create aan empty array
         if self.value is None:
            self.value = []

         self.value.append(None)
         print("New value: "+str(self.value))
         if self.parent is not None:
             self.parent.updateChild(self.key, None)
         else:
            self.draw()
         """
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
           print("Not a object or array. No cannot update child")
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
       self.testData = ({
         "strings":[{"value":"test","schema":{"bsonType":"string"}},
                    {"value":"test2","schema":{"bsonType":"string"}}
          ],
          "integers":[{"value":1,"schema":{"bsonType":"int"}},
                     {"value":-1, "schema":{"bsonType":"int"}}
          ],
          "doubles":[{"value":1.5,"schema":{"bsonType":"double"}},
                     {"value":2,"schema":{"bsonType":"double"}}
          ],
          "booleans":[{"value":True, "schema": {"bsonType":"bool"}},
                     {"value":True, "schema": {"bsonType":"bool"}}
          ],
          "arrays":[{"value":["A","B","C"], "schema": {"bsonType":"array", "items":{"bsonType":"string"}}},
                    {"value":[1,2,3],"schema": {"bsonType":"array", "items":{"bsonType":"int"}}},
                    {"value":[1.1,2.1,3.1], "schema": {"bsonType":"array", "items":{"bsonType":"double"}}},
                    {"value":[True, False, True], "schema": {"bsonType":"array", "items":{"bsonType":"bool"}}},
#                    {"value":["A",2,True], "schema": {"bsonType":"array", "items":{"bsonType":"mixed"}}},
                    {"value":[[1,2,3],[4,5,6],[7,8,9]], "schema": {"bsonType":"array", "items":{"bsonType":"array", "items":{"bsonType":"int"}}}},
                    {"value":[{"key1":1},{"key2":2},{"key3":3}], "schema": {"bsonType":"array", "items":{"bsonType":"object","items":{"bsonType":"int"}}}}
          ],
          "objects":[{"value":{"k1":1,"k2":2,"k3":3}, "schema":{"bsonType":"object", "items":{"bsonType":"int"}}},
                     {"value":{"k1":"S1","k2":"s2","k3":"s3"}, "schema":{"bsonType":"object", "items":{"bsonType":"string"}}},
                     {"value":{"k1":1.2,"k2":2,"k3":True}, "schema":{"bsonType":"object", "items":{"bsonType":"double"}}},
                     {"value":{"k1":False,"k2":True,"k3":True}, "schema":{"bsonType":"object", "items":{"bsonType":"boo"}}},
#                     {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
#                     {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
#                     {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
                     {"value":{"k1":[1,2,3],"k2":[4,5,6]}, "schema":{"bsonType":"object", "items":{"bsonType":"array","items":{"bsonType":"int"}}}},
                     {"value":{"k1":{"k11":1,"k12":2,"k13":3},"k2":{"k21":4,"k22":5,"k23":6}}, "schema":{"bsonType":"object", "items":{"bsonType":"object","items":{"bsonType":"int"}}}}
          ]
       })

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
#       self.setLayout( self.mainLayout )

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
       #New Test
       valid = True

       keys = self.testData.keys()

       self.testWidgets = []
       for key in keys:
          itemCount = 0
          subLayout = QVBoxLayout()
          keyLabel = QLabel();
          keyLabel.setText(str(key))
          subLayout.addWidget(keyLabel)
          for item in self.testData[key]:
              print(key+":"+str(itemCount)+" - "+str(item))
              widget = SmartWidget().init(key+":"+str(itemCount),item["value"], item["schema"])
              itemCount = itemCount + 1
              if widget.valid is False:
                  print( "Unable to create string widget. Failure")
              else:
                  subLayout.addWidget(widget.frame)
                  self.testWidgets.append(widget)

          self.mainLayout.addLayout(subLayout)

       self.mainLayout.addStretch(1)
 
       #submitButton
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
       self.mainLayout.addWidget(submitButton)

       self.scrollArea = QScrollArea()
       self.scrollWidget = QWidget()
#       self.scrollWidget_layout = QVBoxLayout()

       self.scrollWidget.setLayout(self.mainLayout)
       self.scrollArea.setWidget(self.scrollWidget)
       self.scrollArea.setWidgetResizable(True)

       self.lastLayout = QVBoxLayout()
       self.lastLayout.addWidget(self.scrollArea)         

       self.setLayout( self.lastLayout )
       

   def submitButtonPressEvent(self):
       print("SUBMIT")
       widgetNum = 0 

       testValues = []
       for item in self.testData:
           testArray = self.testData[item]
           j = 0
           for subItem in testArray:
               testValues.append(subItem["value"])
       
       testWidgets = []
       for item in self.testWidgets:
          testWidgets.append(item.getValue())

       i = 0
       while i < len(testWidgets):
           if testValues[i] != testWidgets[i]:
               print("Mismatch1: "+str(i)+": "+str(testValues[i]))
               print("Mismatch2: "+str(i)+": "+str(testWidgets[i]))
           else:
               print("Value:"+str(testWidgets[i]))

           i = i +1
       
       exit()

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

