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
#
# TODO: Know supported types from template (if possible)
#       Select only from those. 
#       Value and validate type
#
class ObjectDialog(QDialog):
    ##
    #\brief Initialization function for the object dialog
    #\param [in] callback callback for the submit function
    #
    # The Object Dialog is used to add a new object to a dictionary. The callback is
    # the SmartWidget updateChild function which require a key, value, and optional
    # childSchema argument
    #
    #def updateChild( self, key, value, childSchema=None ):
    def __init__(self, callback):
        super().__init__()

        self.callback = callback


        #The enums for the bsonType of the properties is added programmatically 
        #after the defintion
        self.objectSchema = {}
        self.objectSchema["bsonType"] =  "object"
        self.objectSchema["required"] = ["key", "bsonType"]
        self.objectSchema["properties"]={}
        self.objectSchema["properties"]["key"]={}
        self.objectSchema["properties"]["key"]["bsonType"]="string"
        self.objectSchema["properties"]["key"]["description"]="key or name of the new value"
        self.objectSchema["properties"]["bsonType"]={}
        self.objectSchema["properties"]["bsonType"]["description"]="base type for the variable"
        self.objectSchema["properties"]["bsonType"]["enum"] = SmartType.types
        self.objectSchema["properties"]["description"]={}
        self.objectSchema["properties"]["description"]["bsonType"]="string"
#        self.objectSchema["properties"]["description"]["description"]="option description of the value"
#        self.objectSchema["properties"]["description"]["description"]="option description of the value"

        self.layout = QVBoxLayout()

        title = QLabel()
        title.setText("Object Dialog")
        self.layout.addWidget(title)


        self.subWidget = SmartWidget().init("New Object", {} ,self.objectSchema )
        if self.subWidget == False:
            print("----Failed to create object widget for "+str(key)+" with schema "+str(self.objectSchema))

        self.layout.addWidget(self.subWidget.frame)

        #Create submit button
        controlLayout = QHBoxLayout()
        submitButton = QPushButton("submit")
        submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
        controlLayout.addWidget(submitButton)
        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
        controlLayout.addWidget(cancelButton)

        controlFrame = QFrame()
        controlFrame.setLayout(controlLayout)
        self.layout.addWidget( controlFrame)
        self.setLayout(self.layout)

        self.show()

        self.setLayout(self.layout)
        self.show()
        self.exec_()
    
    ##
    # \brief handles submission
    def submitButtonPressEvent(self):
        values = self.subWidget.getValue()
        key = values["key"]
        self.key = key
#SDF        self.subWidget.key = self.key
       
        del values["key"]
    
        print("ooooooo "+str(key)+ ", values: "+str(values))

#        print("Creating an object dialog with schema: "+str(self.objectSchema))
       
#        self.callback("test", None, schema)
        self.callback(key, values)
        self.done(True)
##
# \brief dialog for modifying dictionaries
#
# TODO: Know supported types from template (if possible)
#       Select only from those. 
#       Value and validate type
#
class ObjectDialog2(QDialog):
    ##
    #\brief Initialization function for the object dialog
    #\param [in] callback callback for the submit function
    def __init__(self, callback):
       super().__init__()

       self.callback = callback
       self.layout = QVBoxLayout()

       title = QLabel()
       title.setText("Object Dialog")
#       titleLayout.addWidget(title)
#       titleFrame = QFrame()
#       titleFrame.setLayout(titleLayout)
       self.layout.addWidget(title)

       #The value layout is used to 
       self.keyLayout = QHBoxLayout()
       keyLabel = QLabel()
       keyLabel.setText("key")
       self.keyLayout.addWidget( keyLabel )
       keyFrame = QFrame()
       keyFrame.setLayout(self.keyLayout)
       self.layout.addWidget(keyFrame)

       #default is for it to be a text box 
       self.key = QLineEdit()
       self.ss = self.key.styleSheet()
       self.keyLayout.addWidget(self.key)

       #Layout to specify the type of object 
       typeLayout = QHBoxLayout()
       typeLabel = QLabel()
       typeLabel.setText("type")
       typeLayout.addWidget(typeLabel)

       self.types = QComboBox()
       self.types.addItems(SmartType.types)
       typeLayout.addWidget(self.types)

       #Checkbox to see if we are required
       reqLayout = QHBoxLayout()
       reqLabel = QLabel()
       reqLabel.setText("required")
       self.reqCheck = QCheckBox()
       reqLayout.addWidget(reqLabel)
       reqLayout.addWidget(self.reqCheck)
       
       #Create a description pane
       #The value layout is used to 
       descLayout = QHBoxLayout()
       descLabel = QLabel()
       descLabel.setText("description")
       descLayout.addWidget( descLabel )
       
       #default is for it to be a text box 
       self.desc = QLineEdit()
       self.ss = self.desc.styleSheet()
       descLayout.addWidget(self.desc)

       #Create submit button
       controlLayout = QHBoxLayout()
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
       controlLayout.addWidget(submitButton)
       cancelButton = QPushButton("cancel")
       cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
       controlLayout.addWidget(cancelButton)


       #create layout
       typeFrame = QFrame()
       typeFrame.setLayout(typeLayout)
       reqFrame = QFrame()
       reqFrame.setLayout( reqLayout )
       descFrame = QFrame()
       descFrame.setLayout( descLayout )
       controlFrame = QFrame()
       controlFrame.setLayout(controlLayout)

       self.layout.addWidget(typeFrame)
       self.layout.addWidget( reqFrame )
       self.layout.addWidget( descFrame )
       self.layout.addWidget( controlFrame)
       self.setLayout(self.layout)

       self.show()

       self.exec_()

    ##
    # \brief Object Dialog submit button press event
    def submitButtonPressEvent(self):
       key = self.key.text()
       mytype = self.types.currentText()
       req = self.reqCheck.isChecked()
       desc = self.desc.text()

       if key == "":
           print("Must enter a key")
           return
       tplate = {}
       tplate["bsonType"] = mytype
#       tplate["required"] = req
       tplate["description"] = desc
       if mytype == "array":
           arrayDialog = AddArrayDialog(self.arrayCallback)

           tplate["items"] = self.arraySchema  
 
           try:
               tplate["minItems"] = self.mods["minItems"]
           except:
               print("Unable to set minItems from "+str(key))
          
           try:
               tplate["maxItems"] = self.mods["maxItems"]
           except:
               print("Unable to set maxItems from "+str(key))
       elif mytype == "object":
           tplate["properties"] = {}

       self.callback(key, None, tplate )

       self.done(True)

    ##
    # \brief a callback for a new array type. Must specify sub-types
    def arrayCallback( self, schema, mods ):
        self.arraySchema = schema
        self.mods = mods
 


##
# \brief dialog for modifying dictionaries
class AddArrayDialog(QDialog):
    ##
    #\brief Initialization function for the object dialog
    #\param [in] callback callback for the submit function
    def __init__(self, callback):
       super().__init__()

       self.callback = callback
       self.layout = QVBoxLayout()

       title = QLabel()
       title.setText("Array Dialog")
       self.layout.addWidget(title)

       #Layout to specify the type of object 
       typeLayout = QHBoxLayout()
       typeLabel = QLabel()
       typeLabel.setText("type")
       typeLayout.addWidget(typeLabel)

       self.types = QComboBox()
       self.types.addItems(SmartType.types)
       typeLayout.addWidget(self.types)

       #Checkbox to see if we are required
       reqLayout = QHBoxLayout()
       reqLabel = QLabel()
       reqLabel.setText("required")
       self.reqCheck = QCheckBox()
       reqLayout.addWidget(reqLabel)
       reqLayout.addWidget(self.reqCheck)

       #SDF add support for minItems, maxItems
       #Text box to get min value
       minLayout = QHBoxLayout()
       minLabel = QLabel()
       minLabel.setText("minValue")
       self.minEdit = QLineEdit()
       self.minEdit.setText("0")
       minLayout.addWidget(minLabel)
       minLayout.addWidget(self.minEdit)
       
       #Text box to get max value
       maxLayout = QHBoxLayout()
       maxLabel = QLabel()
       maxLabel.setText("maxValue")
       self.maxEdit = QLineEdit()
       self.maxEdit.setText("0")
       maxLayout.addWidget(maxLabel)
       maxLayout.addWidget(self.maxEdit)

       #Create submit button
       controlLayout = QHBoxLayout()
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
       controlLayout.addWidget(submitButton)
       cancelButton = QPushButton("cancel")
       cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
       controlLayout.addWidget(cancelButton)

       #create layout
       typeFrame = QFrame()
       typeFrame.setLayout(typeLayout)
       reqFrame = QFrame()
       reqFrame.setLayout(reqLayout)
       minFrame = QFrame()
       minFrame.setLayout( minLayout)
       maxFrame = QFrame()
       maxFrame.setLayout( maxLayout)
       controlFrame = QFrame()
       controlFrame.setLayout(controlLayout)

       self.layout.addWidget(typeFrame)
       self.layout.addWidget( reqFrame )
       self.layout.addWidget( minFrame )
       self.layout.addWidget( maxFrame )
       self.layout.addWidget( controlFrame)
       self.setLayout(self.layout)

       self.show()
       self.exec_()

    ##
    # \brief Handles the submit button press event for an Array Dialog
    def submitButtonPressEvent(self):
       mytype = self.types.currentText()
       req = self.reqCheck.isChecked()
       minItems = str(self.minEdit.text())
       maxItems = str(self.maxEdit.text())
   
       tplate = {}
       tplate["bsonType"] = mytype

       #SDF This should belong in the parent
       parentMods = {}
       parentMods["minItems"] = int(minItems)
       parentMods["maxItems"] = int(maxItems)
        

       if mytype == "array":
           arrayDialog = ObjectDialog(self.arrayCallback)
           tplate["items"] = self.arraySchema  
       elif mytype == "object":
           tplate["properties"] = {}

       self.callback(tplate, parentMods)
       self.done(True)

    ##
    # \brief a callback for a new array type. Must specify sub-types
    def arrayCallback( self, key, value, schema ):
        self.arraySchema = schema
 
##
# \brief dialog for adding an array to either object or an array.
#
class ArrayDialog(QDialog):
    ##
    #\brief Initialization function for the object dialog
    #\param [in] callback callback for the submit function
    def __init__(self, callback):
       super().__init__()

       self.callback = callback
       self.layout = QVBoxLayout()

       title = QLabel()
       title.setText("Array Dialog")
       self.layout.addWidget(title)

       #Layout to specify the type of object 
       typeLayout = QHBoxLayout()
       typeLabel = QLabel()
       typeLabel.setText("type")
       typeLayout.addWidget(typeLabel)

       self.types = QComboBox()
       self.types.addItems(SmartType.types)
       typeLayout.addWidget(self.types)

       #Checkbox to see if we are required
       reqLayout = QHBoxLayout()
       reqLabel = QLabel()
       reqLabel.setText("required")
       self.reqCheck = QCheckBox()
       reqLayout.addWidget(reqLabel)
       reqLayout.addWidget(self.reqCheck)

       #SDF add support for minItems, maxItems

       #Create submit button
       controlLayout = QHBoxLayout()
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
       controlLayout.addWidget(submitButton)
       cancelButton = QPushButton("cancel")
       cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
       controlLayout.addWidget(cancelButton)

       #create layout
       typeFrame = QFrame()
       typeFrame.setLayout(typeLayout)
       reqFrame = QFrame()
       reqFrame.setLayout(reqLayout)
       controlFrame = QFrame()
       controlFrame.setLayout(controlLayout)

       self.layout.addWidget(typeFrame)
       self.layout.addWidget( reqFrame )
       self.layout.addWidget( controlFrame)
       self.setLayout(self.layout)

       self.show()
       self.exec_()

    ##
    # \brief Handles the submit button press event for an Array Dialog
    def submitButtonPressEvent(self):
       mytype = self.types.currentText()
       req = self.reqCheck.isChecked()

       tplate = {}
       tplate["bsonType"] = mytype
#       tplate["required"] = req
       if mytype == "array":
           arrayDialog = ObjectDialog(self.arrayCallback)
           tplate["items"] = self.arraySchema  
       elif mytype == "object":
           tplate["properties"] = {}

       self.callback(tplate)

       self.done(True)

    ##
    # \brief a callback for a new array type. Must specify sub-types
    def arrayCallback( self, key, value, schema ):
        self.arraySchema = schema

##
#\brief This class is used to draw a widget for a smart type
class SmartWidget(SmartType):
   def __init__(self):
        self.value=None
        self.widgets={}
        self.frame = QFrame()
        self.showSchema = False

        #This defines the informatiaon needed for an object.
        #The enums for the bsonType of the properties is added programmatically 
        #after the defintion
        self.objectSchema = {}
        self.objectSchema["bsonType"] =  "object"
        self.objectSchema["properties"]={}
        self.objectSchema["properties"]["bsonType"]={}
        self.objectSchema["properties"]["bsonType"]["enum"] = SmartType.types
        self.objectSchema["properties"]["description"]={}
        self.objectSchema["properties"]["description"]["bsonType"]="string"
       

            
        #This defines the information needed for an array
        #The enums for the bsonType of the items is added programmatically 
        #after the defintion
        self.arraySchema =  """{
            "bsonType": "object",
            "minItems":{"bsonType":"int", "description":"minimum number of items required",
            "maxItems":{"bsonType":"int", "description":"maximum number of items required",
            "properties": { 
                "bsonType":"object",
                "properties": {
                    "bsonType": { "description": "base type for the objects in the array" },
                    "description":{"bsonType":"string","description":"Optional description of what the variable repres
                }
            }
            """
            #SDF: Do we need an items entry for arrays?
        #self.arraySchema["properties"]["bsonType"]["enum"] = SmartType.types

        return 

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] schema Json object that defines what the object may contain
   # \param [in] parent reference to object that instantiated this class
   # \param [in] showSchema flag to indicate if the schemaShould be displayed (default=False)
   # \return self reference to this object
   #
   # This function is used to initalize a new smart widget with a new key-value
   # pair. If a schema is provided, it is used to ensure that the value is 
   # considered correct. The valid variable is set to True when the object has
   # a valid value.
   #
   def init(self, key, value, schema = None, parent = None, showSchema = False):
       self.parent = parent
       self.valid = False 
       self.showSchema = showSchema

       #Initialize the underlying SmartType with input values
       SmartType.__init__(self, key, value, schema)

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
       
       label.setText(str(self.key)+":")
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
          #Check for enum first. If we have that, handle then exit
          #We assume enum and bsonTypes are mutally exclusive
          if "enum" in self.schema:
              self.type = "enum"
              self.widget = QComboBox()
              self.widget.insertItems(0, self.schema["enum"])

              self.value =self.widget.currentText() 
              self.ss = self.widget.styleSheet()
              self.valid = True

              self.widget.currentIndexChanged.connect( lambda: self.validate())
             
          #If we are an array, create a subwidget for each item. Add one extra 
          #for a new value if editable is an option
          elif self.schema["bsonType"] == "array":
              self.widget = QFrame()
              self.valid = True
              self.subLayout = QVBoxLayout()
              self.subWidgets = []

              count = 0
              if self.value != None:
                  for item in self.value:
                     try:
                         subWidget = SmartWidget().init("item: "+str(count), item, self.schema["items"], self, self.showSchema )
                     except:
                         self.valid = False
                         subWidget = False
                     if subWidget != False:
                         self.subLayout.addWidget(subWidget.frame)
                         self.subWidgets.append(subWidget)
                         count = count + 1
                     else:
                         print("+++++ Failed to create an array widget for "+str(item))
                         exit()
                         self.valid = False
              #else:
              #    print("~~~~~~~ No value")

              #SDF Need to modify to limit to min and max elements in schema
              #Add new, empty element
              subWidget = SmartWidget().init("item: "+str(count), "", self.schema["items"], self, self.showSchema )
              if subWidget == False:
                  print("Failed to create array widget for "+str(key))

              self.subLayout.addWidget(subWidget.frame)
              self.subWidgets.append(subWidget)
              count = count + 1

              #create an extra with an add button
              addLayout = QHBoxLayout()

              #SDF We are failing here. We need to add an item when it makes sense
              addButton = QPushButton("+")
              addButton.clicked.connect( lambda: self.addButtonPressEvent())
              self.subLayout.addWidget(addButton)

              self.subLayout.addStretch(1)
              self.widget.setLayout(self.subLayout)
          
          elif self.schema["bsonType"] == "object":
              self.widget = QFrame()
              self.valid = True
              self.subWidgets = []
              
              self.subLayout = QVBoxLayout()

              if self.schema != None:
                  #If we don't have properties, create them
                  if not "properties" in self.schema.keys():
                       self.schema["properties"] = {}

                  for k  in self.schema["properties"]:
                     subWidget = False
                     try:
                         if self.value == None or self.value == {}:
                             print("No value")
                             subWidget = SmartWidget().init(str(k), None, self.schema["properties"][k], self, self.showSchema )
                         elif k in self.value.keys():
                             print("Creating subwidget "+str(k)+" with value "+str(self.value[k])+" and schema:"+str(self.schema["properties"]))
                             subWidget = SmartWidget().init(str(k), self.value[k], self.schema["properties"][k], self, self.showSchema)
                         else:
                             print("no object")
                             subWidget = SmartWidget().init(str(k), None, self.schema["properties"][k], self, self.showSchema )
                     except:
                         print("Exception: Failed to create widget for object key: "+str(k)+" and schema:"+str(self.schema["properties"][k]))
                         print("Exception: Failed to create widget for object key: "+str(k)+" and schema:"+str(self.schema))
                         self.valid = False
                     
                     if subWidget != False:
                         self.subLayout.addWidget(subWidget.frame)
                         self.subWidgets.append(subWidget)
                     else:
                         #SDF ERROR here
                         print("++++Failed to create a widget for object key "+str(k)+" with schema")
                         print(str(self.schema))
                         print(nnn)
                         exit()
                         self.valid = False

              #addButton
              addButton = QPushButton("+")
              addButton.clicked.connect( lambda: self.addButtonPressEvent())
              self.subLayout.addWidget(addButton)

              self.subLayout.addStretch(1)
              self.widget.setLayout(self.subLayout)
           
          else:
              #default is for it to be a text box 
              self.widget = QLineEdit()
              self.ss = self.widget.styleSheet()
              self.valid = True

              if self.value != None:
                  self.widget.setText(str(self.value))

              self.widget.editingFinished.connect( lambda: self.validate())

          #create layout
          self.layout.addWidget( self.widget )
      
       #If we're showing schema, show type
       if self.showSchema:
           if "bsonType" in self.schema:
               typeLabel = QLabel()  
               typeLabel.setText( "type:"+str(self.schema["bsonType"]))
               self.layout.addWidget( typeLabel )
      
           if "required" in self.schema:
               reqCheck = QCheckBox("required")
               reqCheck.setChecked(self.schema["required"])
               self.layout.addWidget( reqCheck )

           descLabel = QLabel()  
           if "description" in self.schema:
               descLabel.setText( "description: "+str(self.schema["description"]))
           else:
               descLabel.setText( "description: None")
           self.layout.addWidget( descLabel )


       #Add remove button to allow people to remove values
       removeButton = IndexButton("-", self.key, self.removeCallback)
       self.layout.addWidget( removeButton )
       self.layout.addStretch(1)

       return self


   ##
   # \brief Callback to handle changes
   def validate(self):
       self.value = self.getValue()
        

       #If it's an object or an array pass the value forward
       if self.type == "object" or self.type == "array":
           if self.parent != None:
               self.parent.updateChild(self.key, self.value, self.schema)
           else:
               print("No parent in validate for object/array "+str(self.key))
               print("----Value: "+str(self.value))
           return
       
       #We are a standard type
       if self.type == "enum":
           text = self.widget.currentText()
           self.value = text
 
           if self.parent != None:
               self.parent.updateChild(self.key, self.value, self.schema)
           else:
               print("No parent in validate for enum "+str(self.key))
           return
       else:
           text = self.widget.text()

       #If we failed, set background as pink and state to invalid

       result = self.setStringAsValue( text )
       if not result:
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
       return self.value
 
   ##
   # \brief returns the key of the object
   def getKey(self):
       return self.key

   ##
   # \brief callback called by a child to remove itself
   def removeCallback(self, key ):
       #remove key
#       if self.type == "array":
       if self.type == "object":
          del self.value[key]
 
       elif isinstance( self.value, dict ):
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
          #Need an ArrayDialog
          self.draw()
      elif self.schema["bsonType"] == "object":
          print("Calling Object Dialog")
          objectDialog = ObjectDialog(self.updateChild)
          print("Called Object Dialog")
      else:
         #This should never happen...
         print("ERROR!!!!! addCallback schema: "+str(self.schema))
#         self.validate()
         

   ##
   #\brief updates the children of this complex type
   #\param [in] key name of the child to update.
   #\param [in] value new value for the child
   #\param [in] schema the new schema for the child. Default=None
   #
   #This function is called when a child is updated
   def updateChild( self, key, value, childSchema=None ):
       print(self.key+" updating child from "+key+" with value "+str(value))

       #If we're an object, we have to update the child
       if self.schema["bsonType"] == "object":
           print(self.key+" is updating children")
           if "properties" not in self.schema:
              self.schema["properties"] =  {}

           if self.value == None:
               self.value = {}

           if value != None:
               self.value[key] = value

           self.schema["properties"][key] = childSchema

       elif self.schema["bsonType"] == "array":
           if "items" not in self.schema:
              self.schema["items"] =  {}

           if self.value == None:
               self.value = []

           self.schema["items"] = childSchema
           #SDF I think this should be treated as an object
           #self.value.append(value)
           
           index = key[len("item:"):]

           try:
               self.value[int(index)] = str(value)
           except:
               self.value.append(value)

       else:
           print("Not an object or array. No cannot update child")
           return False

       self.validate()

       #If we don't have a parent, draw
       if self.parent == None:
           self.draw()

#SDF remove?
       else: 
           print("Key "+str(self.key)+" is updating its parent with "+str(self.value)+":"+str(self.schema))
           self.parent.updateChild( self.key, self.value, self.schema )



   ##
   # Callback for removing an element frmo an array or a dictionary
   def removeButtonPressEvent( self, index):
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
   def __init__(self ):

       self.testData = ({
         "enums":[{"value":{"key":"test"}, "schema":{"key":{"enum":["e1","e2"], "bsonType":"string"}}}
         ],
         "strings":[{"value":{"key":"test"},"schema":{"key":{"bsonType":"string"}}},
                    {"value":{"key":"test2"},"schema":{"key":{"bsonType":"string"}}}
         ],
         "integers":[{"value":{"key":1},"schema":{"key":{"bsonType":"int"}}},
                     {"value":{"key":-1}, "schema":{"key":{"bsonType":"int"}}}
         ],
         "doubles":[{"value":{"key":1.5},"schema":{"key":{"bsonType":"double"}}},
                    {"value":{"key":2.0},"schema":{"key":{"bsonType":"double"}}}
         ],
         "booleans":[{"value":{"key":True}, "schema": {"key":{"bsonType":"bool"}}},
                    {"value":{"key":True}, "schema": {"key":{"bsonType":"bool"}}}
         ],
         "arrays":[{"value":{"key":["A","B","C"]}, "schema":{"key":{"bsonType":"array", "items":{"bsonType":"string"}}}},
                   {"value":{"key":[1,2,3]},"schema": {"key":{"bsonType":"array", "items":{"bsonType":"int"}}}},
                   {"value":{"key":[1.1,2.1,3.1]}, "schema":{"key": {"bsonType":"array", "items":{"bsonType":"double"}}}},
                   {"value":{"key":[True, False, True]}, "schema":{"key": {"bsonType":"array", "items":{"bsonType":"bool"}}}},
#                   {"value":{"key":["A",2,True]}, "schema":{"key": {"bsonType":"array", "items":{"bsonType":"mixed"}}}},
                   {"value":{"key":[[1,2,3],[4,5,6],[7,8,9]]}, "schema":{"key": {"bsonType":"array", "items":{"bsonType":"array", "items":{"bsonType":"int"}}}}},
                   {"value":{"key":[{"key1":1},{"key2":2},{"key3":3}]}, "schema":{"key": {"bsonType":"array", "items":{"bsonType":"object","properties":{"key1":{"bsonType":"int"},"key2":{"bsonType":"int"},"key3":{"bsonType":"int"}, }}}}}
         ],
         "objects":[
                    {"value":{"key":{"k1":1,"k2":2,"k3":3}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"int"},"k2":{"bsonType":"int"},"k3":{"bsonType":"int"}}}}},
                    {"value":{"key":{"k1":"S1","k2":"s2","k3":"s3"}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"string"},"k2":{"bsonType":"string"},"k3":{"bsonType":"string"} }}}},
#                    {"value":{"key":{"k1":1.2,"k2":2,"k3":True}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":"double"}}}}},
                    {"value":{"key":{"k1":1.2,"k2":2,"k3":True}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"double"},"k2":{"bsonType":"double"},"k3":{"bsonType":"double"} }}}},
                    {"value":{"key":{"k1":False,"k2":True,"k3":True}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"bool"},"k2":{"bsonType":"bool"},"k3":{"bsonType":"bool"}}}}},
##                    {"value":{"key":{"k1":False,"k2":"test","k3":2.0}}, "schema":{"key":{"bsonType":"object", "items":{"bsonType":"mixed"}}}},
##                    {"value":{"key":{"k1":False,"k2":"test","k3":2.0}}, "schema":{"key":{"bsonType":"object", "items":{"bsonType":"mixed"}}}},
##                    {"value":{"key":{"k1":False,"k2":"test","k3":2.0}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":"mixed"}}},
                    {"value":{"key":{"k1":[1,2,3],"k2":[4,5,6]}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"array","items":{"bsonType":"int"}},"k2":{"bsonType":"array","items":{"bsonType":"int"}},"k3":{"bsonType":"array","items":{"bsonType":"int"}}}}}},
                    {"value":{"key":{"k1":{"k11":1,"k12":2,"k13":3},"k2":{"k21":4,"k22":5,"k23":6}}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"object","properties":{"k11":{"bsonType":"int"},"k12":{"bsonType":"int"},"k13":{"bsonType":"int"}}}, "k2":{"bsonType":"object","properties":{"k21":{"bsonType":"int"},"k22":{"bsonType":"int"},"k23":{"bsonType":"int"}}}, "k3":{"bsonType":"object","properties":{"k11":{"bsonType":"int"},"k12":{"bsonType":"int"},"k13":{"bsonType":"int"}}}}}}}
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
   # \brief Unit function
   #
   # This function creates a window for every type in the testData object. The user can go through
   # and manually test each supported type
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
              for k in item["value"]:
                  #If were an object need to pass in the properties
                  widget = SmartWidget().init(k, item["value"][k], item["schema"][k], showSchema = True)

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
       
   def test2( self ):
#       base = {"bsonType":"object", "properties":{}}
#       base = {'bsonType': 'object', 'properties': {'o1': {'bsonType': 'object', 'properties': {'k1': {'bsonType': 'string'}}}}}
#       base = {'bsonType': 'object', 'properties': {'key': {'bsonType': 'string'}, 'type': {'enum': ['string', 'int', 'double', 'bool', 'array', 'object']}}}

#       base={'bsonType': 'object', 'properties': {'name': {'bsonType': 'object', 'description': 'An alphanumeric  sequence of characters', 'properties': {'bsonType': {'description': 'base type for the variable', 'bsonType': 'string'}, 'description': {'bsonType': 'string', 'description': 'provides a description of the value'}}}}}
#       self.test2Widget = SmartWidget().init("test2",{},base)
       base={"bsonType":"object"}

       self.test2Widget = SmartWidget().init("test2",{},base)
       self.mainLayout.addWidget(self.test2Widget.frame)

       #submitButton
       submitButton = QPushButton("submit")
       submitButton.clicked.connect( lambda: self.test2SubmitButtonPressEvent())
       self.mainLayout.addWidget(submitButton)
       self.setLayout( self.mainLayout )

   def test2SubmitButtonPressEvent(self):
       value = self.test2Widget.getValue()
       schema = self.test2Widget.getSchema()

   def submitButtonPressEvent(self):
       testPass = True
       widgetNum = 0 

       testValues = []
       for item in self.testData:
           testArray = self.testData[item]
           j = 0
           for subItem in testArray:
               testValues.append(subItem["value"])
       
       testWidgets = []
       for item in self.testWidgets:
          value = {}
          value[item.key] = item.getValue()
          testWidgets.append(value)
#          testWidgets.append(item.getValue())

       i = 0
       while i < len(testWidgets):
           if testValues[i] != testWidgets[i]:
               testPass = False
           else:
               pass

           i = i +1
       
       if testPass:
           print("Submitted values match")
       exit()

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='AWARE Database Script') 
    parser.add_argument('-t2', action='store_const', dest='t2', const='True', help='select test to run (test or test2)')
    parser.add_argument('-v', action='store_const', dest='version', const='True', help='Prints the software version')   
    args=parser.parse_args()
    
    #If version, print the version and exit
    if args.version:
        print("SmartWidget version: "+version)
        exit(1)


    testType = "t1"

    if args.t2:
        testType = "t2"
        
    app = QApplication( sys.argv )
    window = unitTestViewer()

    #Check individual components
    if testType == "t1":
        window.test()
    elif testType == "t2":
        window.test2()

    sys.exit(app.exec_())

