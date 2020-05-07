#!/usr/bin/python3
# -*- coding: utf-8 -*-

version="0.0.1.0"

import sys
import argparse
import collections
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QMessageBox, QApplication, QVBoxLayout, QHBoxLayout, QDesktopWidget, QLabel, QLineEdit, QFrame, QDialog, QComboBox, QRadioButton, QCheckBox, QScrollArea
from PyQt5.QtCore import pyqtSlot
from SmartType import SmartType

#Global comparator
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)


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
    # the SmartWidget updateChild function which requires a key, value.
    #
    def __init__(self, callback):
        super().__init__()

        #create the internal callback reference
        self.callback = callback

        #The schema for an object is defined here. It determines what fields 
        #show up in the dialog box
        #The enums for the bsonType of the properties is added programmatically 
        #after the defintion
        self.objectSchema = {}
        self.objectSchema["bsonType"] =  "object"
        self.objectSchema["readOnly"] =  True
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
        self.objectSchema["properties"]["required"]={}
        self.objectSchema["properties"]["required"]["bsonType"]="bool"

        #The Object Dialog will use a Vertical layout. 
        self.layout = QVBoxLayout()

        #Add the title to the layout
        title = QLabel()
        title.setText("Object Dialog")
        self.layout.addWidget(title)

        #create a new smart widget based on the object schema without a value
        self.subWidget = SmartWidget().init("New Object", {} ,self.objectSchema, showSchema=True)
  
        #Return on failure
        if self.subWidget == False:
            #SDF May wannt to modify content to have a message in the window
            print("ERROR: Failed to create object with schema "+str(self.objectSchema))
            return

        self.layout.addWidget(self.subWidget.frame)

        #Create submit button
        controlLayout = QHBoxLayout()
        submitButton = QPushButton("submit")
        submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
        controlLayout.addWidget(submitButton)

        #Add cancel button
        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect( lambda: self.cancelButtonPressEvent())
        controlLayout.addWidget(cancelButton)

        controlFrame = QFrame()
        controlFrame.setLayout(controlLayout)
        self.layout.addWidget( controlFrame)
        self.setLayout(self.layout)

        self.show()
#        self.exec_()
    
    ##
    #  \brief handles a submit event
    #
    #  This function converts the dialog box values into the object values. 
    #
    def submitButtonPressEvent(self):
        #Extract the values from the object
        values = self.subWidget.getValue()

        #Try to extract a key from the values. 
        try:
            key = values["key"]
            del values["key"]
          
            if key != "":
                self.callback(key, values)
            else:
               print("Invalid key!. Unable to update")
        except:
            print("Error: No key value entered. Cancelling")
    
        self.done(True)

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
#  \brief Class is used to draw a widget for a smart type
#
#  A smartwidget creates a PyQt5 Widget based on a value and schema provided on 
#  initialization. This class can handle any schema type support by MongoDB 3.6.3
#  include simple types as well as complex types such as arrays and object. For
#  these complex types, the output will be a widget with one or more subwidgets.
#
#  The value for each type is maintained at the highet level. For complex types
#  such as arrays and objects, parent widgets will be notified of changes to a
#  SubWidget through a callback. 
#
class SmartWidget(SmartType):
   ##
   #  \brief Initialization function.
   #  
   #  This function does not take any input parameters and is used to establish 
   #  default values. The object will be created when the intialization function
   #  is called.
   def __init__(self):
        self.value          = None          # value for this widget
        self.required       = False         # Flag to indicate this object is required
        self.valid          = False         # Flag to indicate that this object has valid data
        self.initialized    = False         # Indicate if the widget has been initialized
        self.valueChanged   = False         # The value has changed from initialization
        self.updateCallback = None
        self.removeCallback = None
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
   #  \brief Init function
   #  \param [in] key            name of the item
   #  \param [in] value          value to set the item to
   #  \param [in] schema         JSON object that defines what the object may contain. Default = None
   #  \param [in] updateCallback function that is called when the value changes. Default = None
   #  \param [in] showSchema     flag to indicate if schema info is shown with data. Defaut = True
   #  \return A reference to itself on success, or None on failure.
   #
   #  This function is used to initalize a new smart widget with a new key-value
   #  pair. If a schema is provided, it is used to ensure that the value is 
   #  considered correct. If the schema is set to None, a SmartWidget will be 
   #  created with a non-editable text representation of the value. The valid 
   #  variable is set to True when the value is consistent with the provided 
   #  schema. 
   #
   #  The updateCallback isn't assigned until the last step to allow the validate
   #  function to be called before updates can occur.
   #
   def init(self, key, value, schema = None, updateCallback=None, showSchema = True):
       self.showSchema     = showSchema
       self.updateCallback = updateCallback
       self.required       = False
       
       #Initialize the underlying SmartType with input variables
       SmartType.__init__(self, key, value, schema)

       #Create a frame and apply a horizontal layout. This is the basic form of
       #all SmartWidgets
       self.frame = QFrame ()                              #!< Frame around entry
       self.layout = QHBoxLayout()                         #!< Display out.
       self.frame.setLayout(self.layout)
       self.frame.adjustSize()
       self.frame.setFrameStyle( 1 )
       self.frame.setLineWidth(1)

       self.valid = False 
       self.showSchema = showSchema

       if value == {}:
           value = None

       self.draw(value)

       #Validate to check for schema mismatches.
       self.valid = self.validate()

       self.initialized = True

       if self.valueChanged == True and self.updateCallback != None:
           self.updateCallback( self.key, self.value)

       return self

   ##
   #  \brief Creates all SubWidgets that are applied to the widget layout
   #
   #  This internal function clears the internal layout of all SubWidgets and then
   #  redraws the widget based on the given value and schema. This function 
   #  should only be called on created or when a new value or schema is applied
   #  to this object.
   #
   def draw(self, value = None):

       #Remove all widgets from the current layout
       while self.layout.count():
           item = self.layout.takeAt(0)
           widget = item.widget()
           if widget is not None:
               widget.deleteLater()

       #Create a label based on the object key
       label = QLabel()
       label.setText(str(self.key)+":")
       self.layout.addWidget( label )


       #Check if we have a defined schema
       #If no schema is provided, the value is represented as uneditable text 
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
              #If we already have a defined value, use it
              if self.value != None:
                  value = self.value

              self.type = "enum"
              self.widget = QComboBox()

              #insert items into the list
              self.widget.insertItems(0, self.schema["enum"])

              #See get index of value if it's in the list 
              try:
                  #Get index of value
                  index = self.schema["enum"].index(value)
                  self.widget.setCurrentIndex(index)
              #Not in list, then we are not valid
              except:
                  self.valid = False

              #Extract text to set value
              #SDF Need to handle invalid enum  
              text = self.widget.currentText() 
              self.setStringAsValue(text)

              #If we are successful, update callback
              self.ss = self.widget.styleSheet()
              self.widget.currentIndexChanged.connect( lambda: self.valueChange())

             
          #If we are an array, create a subwidget for each item. Add one extra 
          #for a new value if editable is an option
          elif self.schema["bsonType"] == "array":
              self.widget = QFrame()
              self.valid = True
              self.subLayout = QVBoxLayout()
              self.subWidgets = []

              self.ss = self.widget.styleSheet()

              count = 0
              if self.value != None:
                  for item in self.value:
                     if True:
#SDF                  try:
                        subWidget = SmartWidget().init("item: "+str(count), item, self.schema["items"], self.update)
                     else:
#                     except:
                        self.valid = False
                        subWidget = False

                     if subWidget != False:
                         self.subLayout.addWidget(subWidget.frame)
                         self.subWidgets.append(subWidget)
                         count = count + 1
                     else:
                         print("+++++ Failed to create an array widget for "+str(item))
                         print("with schema: "+str(self.schema["items"]))
                         exit()
                         self.valid = False
              #else:
              #    print("~~~~~~~ No value")

              #SDF Need to modify to limit to min and max elements in schema
              #Add new, empty element
              subWidget = SmartWidget().init("item: "+str(count), "", self.schema["items"], self.update )
              if subWidget == False:
                  print("Failed to create array widget for "+str(self.key))

              self.subLayout.addWidget(subWidget.frame)
              self.subWidgets.append(subWidget)
              count = count + 1

              #create an extra with an add button
              addLayout = QHBoxLayout()

              #If we are not read only, include an add button
              readOnly = False
              try:
                  print("Trying readOnly")
                  readOnly = self.schema["readOnly"]
              except:
                  print("Failed")
                  pass

              if readOnly:
                 #SDF We are failing here. We need to add an item when it makes sense
                 addButton = QPushButton("+")
                 addButton.clicked.connect( lambda: self.addButtonPressEvent())
                 self.subLayout.addWidget(addButton)

              self.subLayout.addStretch(1)
              self.widget.setLayout(self.subLayout)
          
          #We are an object schema
          elif self.schema["bsonType"] == "object":
              #Create a frame and Vertical Layout for the Widget
              self.widget = QFrame()
              self.valid = True
              self.subWidgets = []
              self.subLayout = QVBoxLayout()

              self.ss = self.widget.styleSheet()

              #If we ahve a schema pupulate the layout with sub widgets
              if self.schema != None:
                  #If we don't have properties, create them
                  if not "properties" in self.schema.keys():
                       self.schema["properties"] = {}

                  #Loop through all of the properties
                  for k  in self.schema["properties"]:
                     #Set the subWidget to false to we know if we are successful creating a new widget
                     subWidget = False
                     try:
                         #SDF If we're an enum, we need to set a default if it doesn't exist.
                         if "enum" in self.schema["properties"][k].keys():
                             if not k in self.value.keys():
                                 self.value[k] = self.schema["properties"][k]["enum"][0]
                             

                         if self.value == None or self.value == {}:
                             subWidget = SmartWidget().init(str(k), {}, self.schema["properties"][k], self.update )
                         elif k in self.value.keys():
                             subWidget = SmartWidget().init(str(k), self.value[k], self.schema["properties"][k], self.update)
                         else:
                             subWidget = SmartWidget().init(str(k), None, self.schema["properties"][k], self.update )
                     except:
                         print("Exception: Failed to create widget for object key: "+str(k)+" and schema:"+str(self.schema["properties"][k]))
                         self.valid = False
                     
                     #If a subWidget was created, add the widget to the frame
                     if subWidget != False:
                         self.subLayout.addWidget(subWidget.frame)
                         self.subWidgets.append(subWidget)
                     else:
                         #SDF ERROR here
                         print("++++Failed to create a widget for object key "+str(k)+" with schema")
                         print(str(self.schema))
                         self.valid = False

              #If we are not read only, include an add button
              readOnly = False
              try:
                  readOnly = self.schema["readOnly"]
              except:
                  pass

              if not readOnly:
                  #addButton
                  addButton = QPushButton("+")
                  addButton.clicked.connect( lambda: self.addButtonPressEvent())
                  self.subLayout.addWidget(addButton)

              self.subLayout.addStretch(1)
              self.widget.setLayout(self.subLayout)
           
          #Bool schema
          elif self.schema["bsonType"] == "bool":
              self.widget = QRadioButton()
              self.valid = True
              
              #to set the value
              if self.value != None:
                  self.widget.setChecked(self.value)
              else:
                  self.widget.setChecked(False)

              self.setValue(self.widget.isChecked())
              self.valid = True
              self.widget.toggled.connect( lambda: self.valueChange())

              #If we are successful, update callback
              self.ss = self.widget.styleSheet()
             
          else:
              #default is for it to be a text box 
              self.widget = QLineEdit()
              self.ss = self.widget.styleSheet()
              self.valid = True

              if self.value != None:
                  self.widget.setText(str(self.value))

              self.widget.editingFinished.connect( lambda: self.valueChange())

          #create layout
          self.layout.addWidget( self.widget )
      
       #If we're showing schema, show type
       if self.showSchema:
           if "bsonType" in self.schema:
               typeLabel = QLabel()  
               typeLabel.setText( "type:"+str(self.schema["bsonType"]))
               self.layout.addWidget( typeLabel )
      
           """
           if "required" in self.schema:
               reqCheck = QCheckBox("required")
               reqCheck.setChecked(self.schema["required"])
               self.layout.addWidget( reqCheck )
           """

           descLabel = QLabel()  
           if "description" in self.schema:
               descLabel.setText( "description: "+str(self.schema["description"]))
           else:
               descLabel.setText( "description: None")
           self.layout.addWidget( descLabel )

       #Add remove button to allow people to remove values
       removeButton = IndexButton("-", self.key, self.remove)
       self.layout.addWidget( removeButton )
       self.layout.addStretch(1)

       return self

   ##
   #  \brief Function to ensure that the value is consistent with the schema
   #  \return True on success, False on faliure.
   #
   #  If the value and the schema are consistent, the internal valid variable
   #  will be set to true. If not, the variable will be set to False. For 
   #  complex types, each SubWidget will be independently validated.
   #
   def validate(self):
       text = ""
        
       #If it's an object or an array check if all children are valid. If so
       # this object is valid
       if self.type == "object":
           result = True

           #Any subwidgets are invalid, this object is not valid
           for w in self.subWidgets:
               if w.valid == False:
                  print("Invalid widget: "+str(w.getKey())+"!")
                  result = False

       #If it's an object or an array check if all children are valid. If so
       # this object is valid
       elif self.type == "array":
           result = True

           #Any subwidgets are invalid, this object is not valid
           for w in self.subWidgets:
               if w.valid == False:
                  print("Invalid widget: "+str(w.getKey())+"!")
                  result = False

       #Enum values are represented at the widget. If we are an enum, translate
       #the selection to our value using the setStringAsValue function.
       elif self.type == "enum":
           text = self.widget.currentText()
           result = self.setValue(text)

       #Bool type
       elif self.type == "bool":
           text = str(self.widget.isChecked())
           if text == "True":
               result = self.setValue(True)
           else:
               result = self.setValue(False)

       else:
           #Handle a basic type. For these cases, we verify the text can be
           #represented as the basic type. 
           text = self.widget.text()

           #Use the SmartWidget function to validate text.
           result = self.setStringAsValue( text )

       # On failure, set the valid variable to false and create a pink background
       if not result:
          print("Req: "+str(self.required)+", A"+str(text)+"A")
          if self.required == False and text == "":
              self.widget.setAutoFillBackground(False)
              self.widget.setStyleSheet(self.ss)
          else:
              print( "Invalid field. Type not "+self.schema["bsonType"])
              self.widget.setAutoFillBackground(True)
              self.widget.setStyleSheet("QLineEdit{background:pink;}")
              self.valid = False


       # On success, set the valid variable as true and call the updateCallback.
       else:
          if self.type != "bool":
              self.widget.setAutoFillBackground(False)
              self.widget.setStyleSheet(self.ss)
          self.valid = True

       return result

   ##
   #  \brief Function to specify if this schema elemet is required
   #
   def setRequired(self, value ):
      if isinstance( value, bool):
          self.required = value
      else:
          print("SmartType Error: Invalid value of "+str(value)+" for setRequired")

   
   ##
   #  \brief Function that is notified when the Widget Value changes through the UI
   #
   #  This functional validates the results and notified the updateCallback

   def valueChange(self):
      result = self.validate()

      #only update if we have a valid result and have been initialized 
      if self.initialized and self.updateCallback != None:
          if result:
              self.updateCallback( self.key, self.value)
          else:
              self.updateCallback( self.key, None )

   ##
   #  \brief function to get the value of the widget. 
   #  \return value of the object if it is valid, None if it is not.
   #
   #  This function returns the value of the widget as the appropriate type. 
   #  For complex types, this function will build the the 
   #  value recursively from any subwidgets. 
   #
   #  Since subwidgets use callbacks on value changes, this function should
   #  only be called at the top-level from an external application.  
   # 
   def getValue(self):
       #If we are not valid, return No value
       if not self.valid:
           return None

       return self.value
 
   ##
   # \brief returns the key of the object
   def getKey(self):
       return self.key

   ##
   # \brief callback called by a child to remove itself
   #  
   #  This funciton remove these child with teh specified key
   def remove(self, key ):
       self.updateCallback( key, None, remove=True )


       """
       #remove key
       if self.type == "object":
          del self.value[key]
 
       elif isinstance( self.value, dict ):
          self.value.pop(key)
       else:
          print("Cannot remove item from unknown type: "+str(self.type))

       print(str(self.value))

       #Call the removeCallback if available. If not, draw
       if self.removeCallback is not None:
           self.removeCallback(key)
       else:
           print(self.key+" Remove Draw")
           self.draw()
       """

       return 

   ##
   #  \brief Function to add an item to a complex type
   # 
   #  This function create a pop-up window used to add an item to a complex
   #  object. The Dialog window will trigger the update function as a callback
   #  on submit.
   #
   def addButtonPressEvent(self):
      if self.schema == None:
          print("Cannot add an item without a schema")
          return

      if self.schema["bsonType"] == "array":
           #SDF Arry add not supported
          self.draw()
      elif self.schema["bsonType"] == "object":
          objectDialog = ObjectDialog(self.objectUpdate)
      else:
         #This should never happen...
         print("ERROR!!!!!  addButtonPressEvent for a non-complex type: "+str(self.schema))

   ##
   #  \brief function for updating an object
   #  \param [in] key   unique identified for the object
   #  \param [in] value new value for the object
   #
   #  The object update is handled separately since changing the contents requires
   #  schema modifications
   def objectUpdate( self, key, value ):
       #Check if the key exists in the schema
       try:
           if key in self.schema["properties"].keys:
               print("Must remove existing obejct to change it")
               return
       except:
           self.schema["properties"][key] = value

       self.draw()

   ##
   #\brief This function notifies the object that one of its values has changed
   #\param [in] key name of the child
   #\param [in] value new value for the child
   #
   #This function is called when a child is updated
   def update( self, key, value, remove=False):
       self.valueChanged = True

       #Remove object
       if remove:
           print("Removing item "+str(key)+" of type: "+str(self.type))

           if self.type == "object":
               try:
                   del self.value[key]
               except:
                   print(str(key)+" is not in "+self.key+": "+str(self.value))
           elif isinstance( self.value, dict ):
               self.value.pop(key)
           else:
               print("Cannot remove item from unknown type: "+str(self.type))

       elif value == None:
           self.value[key] = value
           return

       #If we're an object, we have to update the child
       elif self.schema["bsonType"] == "object":
           if "properties" not in self.schema:
              self.schema["properties"] =  {}

           if self.value == None:
               self.value = {}

           #Check if we actually change the value
           try:
               #This if the key is already in value and its value matched, no change
               if self.value[key] == value:
                   self.valueChanged = False

               #Otherwise, set the new value
               else:
                   self.value[key] = value

           #The exception occures when the key did not exist
           except:
               self.value[key] = value

       #Array processing
       elif self.schema["bsonType"] == "array":
           if "items" not in self.schema:
              self.schema["items"] =  {}

           if self.value == None:
               self.value = []

           
           index = key[len("item:"):]

           try:
               self.value[int(index)] = str(value)
           except:
               self.value.append(value)

       else:
           print("SmartWidget error: "+str(self.type)+" invalide for updates")
           return False

       #Once we have traversed back to the root widget, redraw all subwidgets
       if self.updateCallback == None and self.valueChanged == True:
           self.draw()
       #If we are initialized, we need to call the update callback
       elif self.initialized == True and self.valueChanged == True:
           self.updateCallback( self.key, self.value)
       else:
           #No changes to the current value, carry on
           pass


   ##
   # Callback for removing an element frmo an array or a dictionary
   def removeButtonPressEvent( self, index):
       if self.removeCallback != None:
           self.frame.deleteLate()
           self.removeCallback( self.key)
       else:
          print("No callback specified. Unable to remove")


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
#                  widget = SmartWidget().init(k, item["value"][k], item["schema"][k], showSchema = True)
                  widget = SmartWidget().init(k, item["value"][k], item["schema"][k], self.testUpdate, showSchema=True)

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

   def testUpdate(self, key, value):
      print("Updating "+str(key)+" with value: "+str(value))
       
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
       print("Value: "+str(value))

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

