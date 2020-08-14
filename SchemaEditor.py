#!/usr/bin/python3
import argparse
from datetime import datetime
#from pymongo import MongoClient
#from bson import json_util
import json
import time
from collections import OrderedDict
from copy import deepcopy
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QFrame, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QComboBox, QFileDialog, QLineEdit, QMainWindow, QSpacerItem, QSizePolicy

#from ADB import ADB
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
        self.source = {"type":None}
        self.dests = ["console", "file"]
        self.dest = {"type":"console"}
     
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

        #create Layouts in UI
        self.titleLayout  = QHBoxLayout()
        self.mainLayout   = QVBoxLayout()
        self.sourceLayout = QHBoxLayout()
        self.destLayout   = QHBoxLayout()
        self.valueLayout  = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()

        #Create frames
        self.sourceFrame = QFrame()
        self.destFrame   = QFrame()
        self.valueFrame  = QFrame()
        self.sourceFrame.setFrameStyle(QFrame.Box)
        self.valueFrame.setFrameStyle(QFrame.Box)
        self.destFrame.setFrameStyle(QFrame.Box)

        self.sourceFrame.setLayout(self.sourceLayout)
        self.destFrame.setLayout(self.destLayout)
        self.valueFrame.setLayout(self.valueLayout)
        self.valueFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #Create Scoll Area for valueFrame
        self.valueScrollArea = QScrollArea()
        self.valueScrollArea.updateGeometry()
        self.valueScrollArea.setWidget( self.valueFrame)
        self.valueScrollArea.setWidgetResizable(True)

        #Create title
        title = QLabel()
        title.setText("Aqueti Schema Editor")
        self.titleLayout.addWidget(title)

        #Add persistent source items
        sourceTitle = QLabel()
        sourceTitle.setText("Source:")
        self.sourceCombo = QComboBox()
        self.sourceCombo.addItems(self.sources)
        self.sourceCombo.currentTextChanged.connect(lambda: self.sourceChangeCallback())
        selectSourceButton = QPushButton("Load")
        self.sourceLayout.addWidget( sourceTitle )
        self.sourceLayout.addWidget(self.sourceCombo)

        self.sourceMetaLayout = QHBoxLayout()
        self.sourceMetaLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.sourceLayout.addLayout(self.sourceMetaLayout)
        self.sourceLayout.addWidget(selectSourceButton)

        #Add persistent dest
        destTitle = QLabel()
        destTitle.setText("Dest:")
        self.destCombo = QComboBox()
        self.destCombo.addItems(self.dests)
        self.destCombo.currentTextChanged.connect(lambda: self.destChangeCallback())
        selectDestButton = QPushButton("Load")
        self.destLayout.addWidget( destTitle )
        self.destLayout.addWidget(self.destCombo)

        self.destMetaLayout = QHBoxLayout()
        self.destMetaLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.destLayout.addLayout(self.destMetaLayout)
        self.destLayout.addWidget(selectDestButton)

        #Add Submit Button
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect( lambda: self.submitCallback())
        self.buttonLayout.addWidget(self.submitButton)

        #Add cancel Button
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect( lambda: self.cancelCallback())
        self.buttonLayout.addWidget(cancelButton)

        #Add Layouts and draw
        self.mainLayout.addLayout( self.titleLayout )
        self.mainLayout.addWidget( self.sourceFrame )
        self.mainLayout.addWidget( self.destFrame )

#        self.mainLayout.addWidget( self.valueFrame )
        self.mainLayout.addWidget( self.valueScrollArea)
#        self.mainLayout.addStretch(1)
        self.mainLayout.addLayout( self.buttonLayout)
        self.draw()
     
    ##
    # \brief updates the source Layout
    def updateSourceLayout(self):
        #Remove current layout information
        #Remove all widgets from the current layout
        while self.sourceMetaLayout.count():
             item = self.sourceMetaLayout.takeAt(0)
             self.sourceMetaLayout.removeItem(item)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
             try:
                 item.deleteLater()
             except:
                 pass

        #Find what our current source is and set the appropriate index
        index = 0
        for i in range(0,self.sourceCombo.count()):
            if self.sourceCombo.itemText(i)  == self.source["type"]:
                index = i

        self.sourceCombo.setCurrentIndex(index)

        #Add fields based on source type
        if self.source["type"] == "file":
            #Add filename
            fileLabel = QLabel()
            fileLabel.setText("file: ")

            try:
                name = self.source["filename"]
            except:
                name = ""

            self.sourceFilenameBox = QLineEdit()
            self.sourceFilenameBox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.sourceFilenameBox.setText(name)
#            self.sourceFilenameBox.readOnly = True
#            self.sourceFilenameBox.sizeHint()
#            self.sourceFilenameBox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
 
            self.sourceMetaLayout.addWidget(fileLabel)
            self.sourceMetaLayout.addWidget(self.sourceFilenameBox)
            

#        #Add a submitSource Button
#        selectSourceButton = QPushButton("Load")
#        selectSourceButton.clicked.connect( lambda: self.sourceChangeCallback())

#        self.sourceLayout.addWidget(selectSourceButton)

#        self.sourceLayout.addStretch(1)

    ##
    # \brief updates the destination layout
    #
    def updateDestLayout(self):
        #Remove current layout information
        #Remove all widgets from the current layout
        while self.destMetaLayout.count():
             item = self.destMetaLayout.takeAt(0)
             self.destMetaLayout.removeItem(item)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
             try:
                 item.deleteLater()
             except:
                 pass
        """
        #############################################
        # Layout to select a destination
        #############################################
        destTitle = QLabel()
        destTitle.setText("Dest:")
        self.destCombo = QComboBox()
        self.destCombo.addItems(self.dests)
        """

        #Find what our current dest is and set the appropriate index
        index = 0
        for i in range(0,self.destCombo.count()):
           if self.destCombo.itemText(i)  == self.dest["type"]:
               index = i

        self.destCombo.setCurrentIndex(index)
        self.destCombo.currentTextChanged.connect(lambda: self.destChangeCallback())

#        self.destLayout.addWidget(destTitle)
#        self.destLayout.addWidget(self.destCombo)
#        self.destLayout.addStretch(1)

        ####
        # Fill in details base on dest tpye
        ####
        if self.dest["type"] == "console":
            pass
        elif self.dest["type"] == "file":
            fileLabel = QLabel()
            fileLabel.setText("file: ")

            try:
                name = self.dest["filename"]
            except:
                name = ""

            self.fileNameBox = QLineEdit()
            self.fileNameBox.setText(name)
            
#            self.destMetaLayout.addWidget(fileLabel)
            self.destMetaLayout.addWidget(self.fileNameBox)

    ##
    # \brief function that is called when the source is changed
    #
    def destChangeCallback(self):
        print("Changing dest")

        newType = self.destCombo.itemText(self.destCombo.currentIndex())

        print("New Type: "+str(newType))

        if newType != self.dest["type"]:
            self.dest = {}

        self.dest["type"] = newType

        if self.dest["type"] == "console":
            pass
        
        elif self.dest["type"] == "file":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            destName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

            self.dest["filename"] = str(destName)

        else:
            print("Unsupported Type")

        self.draw()
    ##
    # \brief Update the value layout
    def updateValueLayout(self):
        #Remove all widgets from the current layout
        while self.valueLayout.count():
             item = self.valueLayout.takeAt(0)
             self.valueLayout.removeItem(item)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
             try:
                 item.deleteLater()
             except:
                 pass

 
        #If we have data, let's display it
        if self.sourceSchema != None:
        
            valueTitle = QLabel()
            valueTitle.setText("Schema")

            self.schemaWidget = SmartWidget().init("Schema", self.sourceValue, self.sourceSchema, showSchema=False)
            self.valueLayout.addWidget( self.schemaWidget.frame )

        #Disable the submit button if we don't have a schema
        if self.sourceSchema == None:
            self.submitButton.setEnabled(False)
        else:
            self.submitButton.setEnabled(True)

        self.setLayout( self.mainLayout)

    ##
    # \brief redraws all dynamic layouts
    def draw(self):
        self.updateDestLayout()
        self.updateSourceLayout()
        self.updateValueLayout()
    


    ##
    # \brief callback for when the source type changes
    #
    def sourceChangeCallback( self ):

        #SDF Add popup to notify of schema loss

        #Clear the schema to disable the submit button
        self.sourceSchema = None
        self.source["type"] = self.sourceCombo.itemText(self.sourceCombo.currentIndex())

        if self.source["type"] == "none":
            self.sourceSchema = {"bsonType":"object"}

        #If we are a file  read the file contents as the value
        elif self.source["type"] == "file":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            sourceName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

            self.source["filename"] = str(sourceName)
            print("Loading: "+str(self.source["filename"]))

            with open( self.source["filename"] ) as json_file: 
                self.sourceSchema = json.load(json_file) 

            print("Loaded Schema:"+str(json.dumps(self.sourceSchema, indent=4)))

        self.updateSourceLayout()
        self.updateValueLayout()

    ##
    #\brief callback to get result from SmartWidget
    #
    # This function assumes that the schema is done. It will produce a popup
    # asking where and how to save the data
    #
    def submitCallback(self):
        schema = self.schemaWidget.getSchema()

        if self.dest["type"] == "console":
            print()
            print("Schema: ("+str(time.time())+")")
            print(json.dumps(schema, indent=4))

        elif self.dest["type"] == "file":
            print("Writing to: "+str(self.dest["filename"]))
            with open( self.dest["filename"], 'w' ) as outfile: 
                json.dump(schema, outfile, indent=4)
        else:
             print("Source type: "+str(self.dest["type"])+" is not currently supported")

        self.close()

        #Use save pop-up to save data
        #self.saveWindow = SaveDataWindow(self.source, schema, self.saveCallback )

     
        print(str(time.time())+"- schema:")
        print(str(schema))

    ##
    # \brief Function called after data is saved
    #
    def saveCallback(self, success):
         print("Data Result: "+str(success))


    ##
    # \brief Cancels the change and exits
    #
    def cancelCallback(self):
        print("Exited. No changes were saved")
        sys.exit(1)   

##
# \brief Class that contains the pop-up window for saving data
#
class SaveDataWindow(QWidget):
    def __init__(self, dest, schema, callback, parent = None ):   
        super(SaveDataWindow, self).__init__()

        self.dests = ["console", "text","file","database"]
        self.dest = dest  
        self.schema = schema

        #Determine screen settings
        geo         = self.frameGeometry()
        self.width  = QDesktopWidget().availableGeometry().width();
        self.height = QDesktopWidget().availableGeometry().height();

        #Define window par meters
        self.resize(self.width*.5, self.height*.5 )
        self.setWindowTitle("Aqueti Schema Editor")

        #
        self.mainLayout = QVBoxLayout()
        self.titleLayout = QHBoxLayout()
        self.destLayout = QHBoxLayout()
 
        #Create title
        title = QLabel()
        title.setText("Schema Saving Dialog")
        self.titleLayout.addWidget(title)
        self.mainLayout.addLayout(self.titleLayout)

        #Destination Layout
        self.destLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.destLayout)

        #Add Button Layout
        self.buttonLayout = QHBoxLayout()
        self.submitButton = QPushButton("Save")
        self.submitButton.clicked.connect( lambda: self.saveButtonCallback())
        self.buttonLayout.addWidget(self.submitButton)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect( lambda: self.cancelButtonCallback())
        self.buttonLayout.addWidget(cancelButton)
        self.mainLayout.addLayout( self.buttonLayout)
        self.setLayout( self.mainLayout)
        self.show()

        self.updateDestLayout()
        self.draw()

    ##
    # \brief updates the destinatino layout
    #
    def updateDestLayout(self):
        #Remove current layout information
        #Remove all widgets from the current layout
        while self.destLayout.count():
             item = self.destLayout.takeAt(0)
             self.destLayout.removeItem(item)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
             try:
                 item.deleteLater()
             except:
                 pass

        #############################################
        # Layout to select a destination
        #############################################
        destTitle = QLabel()
        destTitle.setText("OutputType:")
        self.destCombo = QComboBox()
        self.destCombo.addItems(self.dests)

        #Find what our current dest is and set the appropriate index
        index = 0
        for i in range(0,self.destCombo.count()):
           if self.destCombo.itemText(i)  == self.dest["type"]:
               index = i

        self.destCombo.setCurrentIndex(index)

        self.destLayout.addWidget(destTitle)
        self.destLayout.addWidget(self.destCombo)

        ####
        # Fill in details base on source tpye
        ####
        if self.dest["type"] == "console":
            pass
        elif self.dest["type"] == "file":
            fileLabel = QLabel()
            fileLabel.setText("file: ")

            try:
                name = self.dest["filename"]
            except:
                name = ""

            self.fileNameBox = QLineEdit()
            self.fileNameBox.setText(name)
            
            self.destLayout.addWidget(fileLabel)
            self.destLayout.addWidget(self.fileNameBox)



    ## 
    # \brief Function to draw the object
    def draw(self):

        #Add a submitDest Button
        selectDestButton = QPushButton("Select")
        selectDestButton.currentIndexChanged.connect( lambda: self.destChangeCallback())

        self.destLayout.addWidget( destTitle )
        self.destLayout.addWidget(self.destCombo)
        self.destLayout.addWidget(selectDestButton)

        self.destLayout.addLayout( self.destLayout )



    ##
    # \brief callback for the Cancel button
    #
    def cancelButtonCallback(self):
        self.close()

    ##
    # \brief callback for a save button press
    #
    def saveButtonCallback(self):   
        print("Saving:"+str(self.dest))


        if self.dest["type"] == "console":
            print()
            print("Schema ("+str(time.time())+")")
            print(str(self.schema))

        elif self.dest["type"] == "file":
            with open( self.dest["filename"], 'w' ) as outfile: 
                json.dump(self.schema, outfile)
        else:
             print("Source type: "+str(self.dest["type"])+" is not currently supported")

        self.close()

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
