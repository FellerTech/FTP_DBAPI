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

from PyQt5.QtWidgets import QWidget, QApplication, QFrame, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QComboBox, QFileDialog, QTextEdit, QMainWindow, QSpacerItem, QSizePolicy, QLineEdit

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
        self.sources= ["none", "text","file","database"]
        self.schemaSource = {"type":None}
        self.sourceSource = {"type":None}
        self.dests = ["console", "file"]
        self.dest = {"type":"console"}
     
        self.value  = None
        self.schema = None

        #Determine screen settings
        geo         = self.frameGeometry()
        self.width  = QDesktopWidget().availableGeometry().width();
        self.height = QDesktopWidget().availableGeometry().height();

        #Define window par meters
        self.resize(self.width*.5, self.height*.5 )
        self.setWindowTitle("Aqueti Data Editor")
        self.show()

        #create Layouts in UI
        self.titleLayout  = QHBoxLayout()
        self.mainLayout   = QVBoxLayout()
        self.schemaLayout = QHBoxLayout()
        self.sourceLayout = QHBoxLayout()
        self.destLayout   = QHBoxLayout()
        self.valueLayout  = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()

        #Create frames
        self.schemaFrame = QFrame()
        self.sourceFrame = QFrame()
        self.destFrame   = QFrame()
        self.valueFrame  = QFrame()
        self.schemaFrame.setFrameStyle(QFrame.Box)
        self.sourceFrame.setFrameStyle(QFrame.Box)
        self.valueFrame.setFrameStyle(QFrame.Box)
        self.destFrame.setFrameStyle(QFrame.Box)

        self.schemaFrame.setLayout(self.schemaLayout)
        self.sourceFrame.setLayout(self.sourceLayout)
        self.destFrame.setLayout(self.destLayout)
        self.valueFrame.setLayout(self.valueLayout)
        self.schemaFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sourceFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.destFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

        #Add persistent schema items
        schemaTitle = QLabel()
        schemaTitle.setText("Schema:")
        self.schemaCombo = QComboBox()
        self.schemaCombo.addItems(self.sources)
        self.schemaCombo.currentTextChanged.connect(lambda: self.schemaChangeCallback())
        selectSchemaButton = QPushButton("Load")
        self.schemaLayout.addWidget( schemaTitle )
        self.schemaLayout.addWidget(self.schemaCombo)

        self.schemaMetaLayout = QHBoxLayout()
        self.schemaMetaLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.schemaLayout.addLayout(self.schemaMetaLayout)
        self.schemaLayout.addWidget(selectSchemaButton)

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

        #Add persistent dest items
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
        self.mainLayout.addWidget( self.schemaFrame )
        self.mainLayout.addWidget( self.sourceFrame )
        self.mainLayout.addWidget( self.destFrame )

        self.mainLayout.addWidget( self.valueScrollArea)
        self.mainLayout.addLayout( self.buttonLayout)
        self.draw()
     
    ##
    # \brief updates the schema Layout
    def updateSchemaLayout(self):
        #Remove current layout information
        #Remove all widgets from the current layout
        while self.schemaMetaLayout.count():
             item = self.schemaMetaLayout.takeAt(0)
             self.schemaMetaLayout.removeItem(item)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
             try:
                 item.deleteLater()
             except:
                 pass

        #Find what our current schema is and set the appropriate index
        index = 0
        for i in range(0,self.schemaCombo.count()):
            if self.schemaCombo.itemText(i)  == self.schemaSource["type"]:
                index = i

        self.schemaCombo.setCurrentIndex(index)

        #Add fields based on schema type
        if self.schemaSource["type"] == "file":
            #Add filename
            fileLabel = QLabel()
            fileLabel.setText("file: ")

            try:
                name = self.schemaSource["filename"]
            except:
                name = ""

            self.schemaFilenameBox = QLineEdit()
            self.schemaFilenameBox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.schemaFilenameBox.setText(name)
            self.schemaMetaLayout.addWidget(fileLabel)
            self.schemaMetaLayout.addWidget(self.schemaFilenameBox)
            
    ##
    # \brief updates the Source Layout
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
            if self.sourceCombo.itemText(i)  == self.sourceSource["type"]:
                index = i

        self.sourceCombo.setCurrentIndex(index)

        #Add fields based on source type
        if self.sourceSource["type"] == "file":
            #Add filename
            fileLabel = QLabel()
            fileLabel.setText("file: ")

            try:
                name = self.sourceSource["filename"]
            except:
                name = ""

            self.sourceFilenameBox = QLineEdit()
            self.sourceFilenameBox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.sourceFilenameBox.setText(name)
            self.sourceMetaLayout.addWidget(fileLabel)
            self.sourceMetaLayout.addWidget(self.sourceFilenameBox)

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

        #############################################
        # Layout to select a destination
        #############################################
        #Find what our current dest is and set the appropriate index
        index = 0
        for i in range(0,self.destCombo.count()):
           if self.destCombo.itemText(i)  == self.dest["type"]:
               index = i

        self.destCombo.setCurrentIndex(index)

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
            self.fileNameBox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.fileNameBox.setText(name)
            self.destMetaLayout.addWidget(fileLabel)
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
        if self.schema != None:
        
            valueTitle = QLabel()
            valueTitle.setText("Schema")

            self.schemaWidget = SmartWidget().init("Schema:", self.value, self.schema, showSchema=False)
            self.valueLayout.addWidget( self.schemaWidget.frame )

        #Disable the submit button if we don't have a schema
        if self.schema == None:
            self.submitButton.setEnabled(False)
        else:
            self.submitButton.setEnabled(True)

        self.setLayout( self.mainLayout)

    ##
    # \brief redraws all dynamic layouts
    def draw(self):
        self.updateDestLayout()
        self.updateSchemaLayout()
        self.updateValueLayout()

    ##
    # \brief callback for when the source type changes
    #
    def schemaChangeCallback( self ):

        #SDF Add popup to notify of schema loss

        #Clear the schema to disable the submit button
        self.schema = None
        self.schemaSource["type"] = self.schemaCombo.itemText(self.schemaCombo.currentIndex())

        if self.schemaSource["type"] == "none":
            self.schema = {"bsonType":"object"}


        #If we are a file  read the file contents as the value
        elif self.schemaSource["type"] == "file":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            schemaSourceName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

            self.schemaSource["filename"] = str(schemaSourceName)
            print("Loading Schema: "+str(self.schemaSource["filename"]))

            with open( self.schemaSource["filename"] ) as json_file: 
                self.schema = json.load(json_file) 


        self.updateSchemaLayout()
        self.updateValueLayout()

    ##
    # \brief callback for when the source type changes
    #
    def sourceChangeCallback( self ):

        #Clear the source to disable the submit button
        self.value = None
        self.sourceSource["type"] = self.sourceCombo.itemText(self.sourceCombo.currentIndex())

        if self.sourceSource["type"] == "none":
            self.value = {"bsonType":"object"}

        #If we are a file  read the file contents as the value
        elif self.sourceSource["type"] == "file":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            sourceName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

            self.sourceSource["filename"] = str(sourceName)
            print("Loading Data: "+str(self.sourceSource["filename"]))

            with open( self.sourceSource["filename"] ) as json_file: 
                self.value = json.load(json_file) 


        self.updateSourceLayout()
        self.updateValueLayout()

    ##
    #\brief callback to get result from SmartWidget
    #
    # This function assumes that the schema is done. It will produce a popup
    # asking where and how to save the data
    #
    def submitCallback(self):
        value = self.schemaWidget.getValue()

        if self.dest["type"] == "console":
            print()
            print("Value: ("+str(time.time())+")")
            print(json.dumps(value, indent=4))

        elif self.dest["type"] == "file":
            print("Writing to: "+str(self.dest["filename"]))
            with open( self.dest["filename"], 'w' ) as outfile: 
                json.dump(value, outfile, indent=4)
        else:
             print("Source type: "+str(self.dest["type"])+" is not currently supported")

        self.close()

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
#        destTitle = QLabel()
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
#    parser.add_argument('-uri', action='store', dest='uri', help='URI of the mongodb system')
#    parser.add_argument('-dbase', action='store', dest='dbase', help='database to reference')


#    parser.add_argument('-test', action='store_true', dest='test', help='unit test')

    args=parser.parse_args()

    """
    if args.uri:
        uri = args.uri

    if args.dbase:
        dbase =args.dbase
    """

    app = QApplication( sys.argv )

    print("Creating scheme editor with URI: "+str(uri))
    window = MainWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
