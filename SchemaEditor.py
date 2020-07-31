#!/usr/bin/python3
import argparse
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
import json
import time
from collections import OrderedDict
from copy import deepcopy
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QFrame, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QComboBox, QFileDialog, QTextEdit

from ADB import ADB
from SmartWidget import SmartWidget

##
# \class provides the main window used by this application. 
#
# The main window is the basis for the application. In its simplest state
# it will have a drop-donw window to allow the user to select the schema 
# source.
class MainWindow( QWidget ):
    ## 
    # \brief Initialization Function
    def __init__(self):
        super(MainWindow, self).__init__()

        #Default variables
        self.valid = False                        #Field to determine if the value is valid
        self.selectorLayout = None                #Layout used for selecting a specific source
        self.sources = ["none", "text","file","database"]
        self.source = "none"
        self.sourceValue = None
        self.sourceSchema = None

        #Determine screen settings
        geo         = self.frameGeometry()
        self.width  = QDesktopWidget().availableGeometry().width();
        self.height = QDesktopWidget().availableGeometry().height();

        #Define window par meters
        self.resize(self.width*.5, self.height*.5 )
        self.setWindowTitle("Aqueti Schema Editor")
        self.show()

        self.mainLayout = QVBoxLayout()
        self.draw()
     

    def draw(self):
        #Remove existing objects
        #Remove all widgets from the current layout
        while self.mainLayout.count():
             item = self.mainLayout.takeAt(0)
             self.mainLayout.removeItem(item)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()

             try:
                 item.deleteLater()
             except:
                 pass
       
        #Create title
        self.titleLayout = QHBoxLayout()
        self.titleLayout.addStretch(1)
        title = QLabel()
        title.setText("Aqueti Schema Editor")
        self.titleLayout.addWidget(title)
        self.titleLayout.addStretch(1)
        self.mainLayout.addLayout( self.titleLayout )

        #############################################
        # Layout to select a source
        #############################################
        self.sourceLayout = QHBoxLayout()
        sourceTitle = QLabel()
        sourceTitle.setText("Schema Source:")
        self.sourceCombo = QComboBox()
        self.sourceCombo.addItems(self.sources)

        #Find what our current source is and set the appropriate index
        index = 0
        for i in range(0,self.sourceCombo.count()):
           if self.sourceCombo.itemText(i)  == self.source:
               index = i

        self.sourceCombo.setCurrentIndex(index)
#        self.sourceCombo.currentIndexChanged.connect(self.sourceChangeCallback)

        #Add a submitSource Button
        selectSourceButton = QPushButton("Select")
        selectSourceButton.clicked.connect( lambda: self.sourceChangeCallback())

        self.sourceLayout.addWidget( sourceTitle )
        self.sourceLayout.addWidget(self.sourceCombo)
        self.sourceLayout.addWidget(selectSourceButton)

        self.mainLayout.addLayout( self.sourceLayout )

        self.valueLayout = QVBoxLayout()

 
        #If we have data, let's display it
        if self.sourceSchema != None:
        
            valueTitle = QLabel()
            valueTitle.setText("Schema")

#            self.sourceSchema = {"bsonType":"object"}
           
            print("schema: "+str(self.sourceSchema))
            self.schemaWidget = SmartWidget().init("Schema", self.sourceValue, self.sourceSchema, showSchema = True)
            self.valueLayout.addWidget( self.schemaWidget.frame )
 
        self.mainLayout.addLayout( self.valueLayout )
        self.mainLayout.addStretch(1)

        #Add Button Layout
        self.buttonLayout = QHBoxLayout()
        submitButton = None
        if self.sourceSchema != None:
            #Add submit Button
            submitButton = QPushButton("Submit")
            submitButton.clicked.connect( lambda: self.submitCallback())
            self.buttonLayout.addWidget(submitButton)

        #Add cancel Button
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect( lambda: self.cancelCallback())
        self.buttonLayout.addWidget(cancelButton)

        self.mainLayout.addLayout( self.buttonLayout)
#        self.mainLayout.addStretch(1)
        self.setLayout( self.mainLayout)

    ##
    # \brief callback for when the source type changes
    #
    def sourceChangeCallback( self ):
        self.source = self.sourceCombo.itemText(self.sourceCombo.currentIndex())

        if self.source == "none":
            self.sourceSchema = {"bsonType":"object"}

        #If we are a file  read the file contents as the value
        elif self.source == "file":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.sourceName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)
            print("Loading: "+str(self.sourceName))

            with open(self.sourceName) as json_file: 
                self.sourceSchema = json.load(json_file) 

            print("Loaded Schema:"+str(self.sourceSchema))

        self.draw()

    ##
    #\brief callback to get result from SmartWidget
    #
    # This function assumes that the schema is done. It will produce a popup
    # asking where and how to save the data
    #
    def submitCallback(self):
        schema = self.schemaWidget.getSchema()

        #Use save pop-up to save data

        print(str(time.time())+"- schema:")
        print(str(schema))

    ##
    # \brief Cancels the change and exits
    #
    def cancelCallback(self):
        print("Exited. No changes were saved")
        sys.exit(1)   

    

##
# \class Widget that allows a user to select a schema from a database
#
class DatabaseWindow( QWidget ):
    def __init__(self):
        # set default values
        uriMap = {}
        self.dbs = []
        self.dbase = None
        self.collection = None


##
# \class This class allows users to edit schemas
#
class SchemaEditor( QWidget ):
    def __init__(self):
        
        uriMap = {}
        self.dbs = []
        self.dbase = None
        self.collection = None

        #This defines the informatiaon needed for an object.
        #The enums for the bsonType of the properties is added programmatically 
        #after the defintion
        self.objectSchema = {}
        self.objectSchema["bsonType"]="object"
        self.objectSchema["properties"]={}
        self.objectSchema["properties"]["bsonType"]={}
        self.objectSchema["properties"]["bsonType"]["description"] = "base type for the variable"
        self.objectSchema["properties"]["bsonType"]["enum"]=SmartWidget().types

        #This defines the information needed for an array
        #The enums for the bsonType of the items is added programmatically 
        #after the defintion
        self.arraySchema = {}
        self.arraySchema["bsonType"] = "object"
        self.arraySchema["minItems"] = {}
        self.arraySchema["minItems"]["bsonType"] = "int"
        self.arraySchema["minItems"]["description"] = "minimum number of items required"
        self.arraySchema["maxItems"] = {}
        self.arraySchema["maxItems"]["bsonType"] = "int"
        self.arraySchema["maxItems"]["description"] = "maximum number of items allowed"
        self.arraySchema["properties"] = {}
        self.arraySchema["properties"]["bsonType"]={}
        self.arraySchema["properties"]["bsonType"]["description"] = "base type for object"
        self.arraySchema["properties"]["bsonType"]["enum"] = SmartWidget().types


    def init( self, uri ):
        print("Initializing")
        #URI Value
        self.adb = ADB(uri)

        super().__init__()

        #Determine screen settings
        geo         = self.frameGeometry()
        self.width  = QDesktopWidget().availableGeometry().width();
        self.height = QDesktopWidget().availableGeometry().height();

        #Define window par meters
        self.resize(self.width*.5, self.height*.5 )
        self.setWindowTitle("Aqueti Schema Editor")
        self.show()

        self.mainLayout = QVBoxLayout()

        #Create title
        self.titleLayout = QHBoxLayout()
        self.titleLayout.addStretch(1)
        title = QLabel()
        title.setText("Aqueti Schema Editor")
        self.titleLayout.addWidget(title)
        self.titleLayout.addStretch(1)
        self.mainLayout.addLayout( self.titleLayout )

        #create the selector layout (allow user to select database / collection)
        self.dbFrame = QFrame()
        self.dbFrame.setLayout(self.genDBSelectorWidget())
        self.collFrame = QFrame()
        self.collFrame.setLayout( self.genCollSelectorWidget())

        selectorFrame = QFrame()
        selectorLayout = QHBoxLayout()
        selectorLayout.addWidget( self.dbFrame)
        selectorLayout.addWidget( self.collFrame)

        self.mainLayout.addLayout(selectorLayout)
        
        #The middle section will have a scroll area
        scrollArea = QScrollArea()
        scrollWidget = QWidget()

        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)

        scrollLayout = QVBoxLayout()
        scrollLayout.addWidget(scrollArea)
        #Create a middle section
        self.midLayout = QVBoxLayout()
        scrollWidget.setLayout(self.midLayout)
        self.mainLayout.addLayout( scrollLayout )

        #submitButton
        submitButton = QPushButton("Submit")
        submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
        self.mainLayout.addWidget(submitButton)

        self.setLayout( self.mainLayout)
        print("Finishing init")

    ##
    # \brief draw all items in the window
    def draw( self ):
      
        #Remove all widgets from the current layout
        while self.midLayout.count():
             item = self.midLayout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
       
        
        collection = self.collCombo.currentText()

#        s = {"bsonType":"object"}
#        s["properties"] = deepcopy(self.schema)

        self.schemaWidget = SmartWidget().init("schema",{}, self.sourceSchema, showSchema = True )
 
        self.midLayout.addWidget(self.schemaWidget.frame)

    ##
    #\brief callback to get result from SmartWidget
    def submitCallback(self, key, value):
        schema = self.schemaWidget.getSchema()
        print("Widget Callback")
        print(str(schema))

    ##
    #\brief Generat aa widget to select a collection
    def genCollSelectorWidget(self):
        self.dbase = self.dbCombo.currentText()
        print("Using :"+self.dbase)
        self.adb.setDatabase( self.dbase )

        #the database to use
        self.collLayout = QHBoxLayout()
        info = QLabel()
        info.setText("Collection")

        self.collCombo = QComboBox()
        self.collCombo.addItems( self.adb.getCollections())

        print("Getting collections for "+self.dbase)

        submitButton = QPushButton("UpdateColl")
        submitButton.clicked.connect( lambda: self.updateCollButtonPressEvent())

        self.collLayout.addWidget(info)
        self.collLayout.addWidget(self.collCombo)
        self.collLayout.addWidget(submitButton)

        self.collLayout.addStretch(1)
        return self.collLayout

    ##
    # \brief Generate the database selector widget
    def genDBSelectorWidget(self):
        #the database to use
        self.dbLayout = QHBoxLayout()
        info = QLabel()
        info.setText("Database")

        self.dbCombo = QComboBox()
        self.dbCombo.addItems( self.adb.getDatabaseList())

        submitButton = QPushButton("UpdateDB")
        submitButton.clicked.connect( lambda: self.updateDBButtonPressEvent())
#        self.dbLayout.addWidget(submitButton)

        self.dbLayout.addWidget(info)
        self.dbLayout.addWidget(self.dbCombo)
        self.dbLayout.addWidget(submitButton)
#        self.dbLayout.addStretch(1)

        return self.dbLayout

    ##
    # \brief handles database updates
    def updateCollButtonPressEvent(self):
        value = self.collCombo.currentText()
        if self.collection == value:
            print("collections match")
        else:
            self.collection = value    
            print("Collection: "+str(self.collection))
  
         
            try:
                self.schema = self.adb.getSchema(self.collection)
#                self.value  = self.adb.getValue( self.collection )

                print("Got schema: "+str(self.schema))
            except:
                print("No schema found for collection "+str(self.collection))
                self.schema = {}

            self.draw()

    ##
    # \brief handles database updates
    def updateDBButtonPressEvent(self):
        value = self.dbCombo.currentText()
        if self.dbase == value:
            print("Databases match")
        else:
            print("Setting database to "+value )
            self.dbase = value
            self.adb.setDatabase( self.dbase )
            self.collCombo.clear()
            self.collCombo.addItems( self.adb.getCollections())

            self.collection = self.collCombo.currentText()
            self.schema = self.adb.getSchema(self.collection)

            print("Got schema2: "+str(self.schema))


            self.draw()

    ##
    # \brief handless a submit button event
    def submitButtonPressEvent(self):
        print("Submission")
        try:
            schema = self.schemaWidget.getSchema()
            value  = self.schemaWidget.getValue()
            result = self.adb.setSchema( self.collection, schema["properties"] )
            print("output schema:"+str(schema))
        except:
            result = False
        
        if not result:
            print("Failed to set schema")
        else:
            print("Schema set")
      
        
        self.close()



def main():
    dbase = "schemas"
    uri = "localhost:27017"

    parser = argparse.ArgumentParser(description="Database Script")
    parser.add_argument('-uri', action='store', dest='uri', help='URI of the mongodb system')
    parser.add_argument('-dbase', action='store', dest='dbase', help='database to reference')
    parser.add_argument('-test', action='store_true', dest='test', help='unit test')

    args=parser.parse_args()
    if args.uri:
        uri = args.uri

    if args.dbase:
        dbase =args.dbase

    app = QApplication( sys.argv )

    print("Creating scheme editor with URI: "+str(uri))
#    window = SchemaEditor()
#    window.init(uri)
    window = MainWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
