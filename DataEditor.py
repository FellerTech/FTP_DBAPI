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

from PyQt5.QtWidgets import QWidget, QApplication, QFrame, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QComboBox

from ADB import ADB
from SmartWidget import SmartWidget

##
# \class This class allows users to edit mongodb schemas
#
class DataEditor( QWidget ):
    def __init__(self):
        
        uriMap = {}
        self.dbs = []
        self.dbase = None
        self.collection = None

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

        s = {"bsonType":"object"}
        s["properties"] = deepcopy(self.schema)


        try:
            print("Creating object with schema:"+str(s))
            print("Creating object with value:"+str(self.value))
            self.mainWidget = SmartWidget().init("schema", self.value, s, showSchema = True )
            self.midLayout.addWidget(self.mainWidget.frame)
        except:
            print("---- "+str(self.collection)+" unable to create widget ----")

        #Get the current schema, if any
#        info = QLabel()
#        info.setText(str(schema))
#        self.midLayout.addWidget(info)
        """
        scrollArea = QScrollArea()
        scrollWidget = QWidget()

        scrollWidget.setLayout(self.mainLayout)
        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)

        lastLayout = QVBoxLayout()
        lastLayout.addWidget(scrollArea)

        self.setLayout( lastLayout)
        """

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
                self.value  = self.adb.getValue( self.collection )
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
            self.value  = self.adb.getDocuments(self.collection)

            print("Got schema2: "+str(self.schema))


            self.draw()

    ##
    # \brief handless a submit button event
    def submitButtonPressEvent(self):
        print("Submission")
        schema = self.mainWidget.getSchema()
        value  = self.mainWidget.getValue()
        print("output schema:"+str(schema))
        print("----------------------------------")
        print("output value:"+str(value))
        print("----------------------------------")

#        result = self.adb.setSchema( self.collection, schema["properties"] )

         
        self.adb.insertDocument(self.collection, value )
        
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
    window = DataEditor()
    window.init(uri)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
