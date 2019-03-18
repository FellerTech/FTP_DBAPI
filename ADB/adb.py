#!/usr/bin/python3
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
import json
import time

#Gets a list of databases and collections
class ADB:
    ##
    # \brief initialization function that specifies what mongo instance to connect to
    def __init__(self, uri, dbase=None):
        self.uri = uri
        self.client = MongoClient(self.uri)
        self.db = None

        if dbase != None:
            self.setDatabase(dbase)

    ##
    # \brief Sets the specified database
    def setDatabase( self, dbase ):
        
        self.db = self.client[dbase]

        #SDF check return code!
        self.dbase = dbase
        
    ##
    # Function to return current database name
    def getDatabase(self):
        return self.dbase 

    ##
    # \brief Function to get the specified indexes for the given database
    def getIndexes(self, collection):
        if self.db == None:
           print("A database must be selected before getIndexes call")
           return
   
        return self.db[collection].index_information()
    

    ##
    # \brief Returns the structure of the databse    
    def getDbStructure(self):
        dbs = self.client.database_names()
        dbStructure = {}
        for item in dbs:

           try:
               dbStructure[item] = self.client[item].list_collection_names()
           except:
               pass
            
        return dbStructure;

    def getProfile():
        print("No profile yet")

    def getUri(self):
        return self.uri

if __name__ == '__main__':
    adb = ADB("localhost")

    """
    print("Mongo database info at uri: "+adb.getUri())
    print( json.dumps(adb.getDbStructure(), indent = 3))
 
    #ERRORS
    print("--- Generating error messages ---")
    adb.getIndexes("files")
    print("--- Done Generating error messages ---")
    """


    #Specify the datbase to use
    adb.setDatabase("acos_local");

    #check the indices on the database
    print( json.dumps(adb.getIndexes("files"), indent = 3 ))
#    print("Indexes: "+ str(adb.getIndexes("files")))

    #start queries
    start = 1547455128795134
    end   = 1547455181751895  
    target = str(start+(end-start)/2)


    query = {
#orig   "startTime":{"$lte":"1547455075775020"},
#orig   "endTime":{"$gte":"1547455128731848"},
    "startTime":{"$gte":str(start), "$lte":str(end)},


#       "startTime":{"$lte":str(start)},
#       "endTime":{"$gte":str(end)},
#       "startTime":{"$lte":target},
#       "endTime":{"$gte":target},
#       "streamIds":"XX00000000000000070019-300729315229696-3"XX00000000000000007003-30077656104960-3
       "streamIds":"XX00000000000000007003-30077656104960-3"
    }

    print()
    print("Query1: "+str(query))

    for i in range(10):
       first = time.time()
       results = adb.db["files"].find(query).limit(2)

       ids = [] 
       for item in results:
           ids.append(item["_id"])

#       explain = results.explain()
#       print("IDs:"+str(ids)+"\tDocs: "+str(explain["executionStats"]["totalDocsExamined"])+"\ttime: "+str(explain["executionStats"]["executionTimeMillis"])+" msec\tAppTime: "+str(duration)+" msec")

       print("IDs:"+str(ids))
       second = time.time()
       duration = (second-first)*1e3
       print("\tAppTime: "+str(duration)+" msec")
       
    """
    #start queries
    query = {
#       "startTime":{"$lte":"1547455075775020"},
       "startTime":{"$gte":target},
       "streamIds":"XX00000000000000070019-300729315229696-3"
    }
    """



    print()
    print("Query2: "+str(query))
    for i in range(10):
       first = time.time()
       results = adb.db["files"].find_one(query)
       second = time.time()
       duration = (second-first)*1e3

#       print(str(results))
       try:
           ids = str(results["_id"])
       except:
           ids = []

       print("IDs:"+str(ids)+"\tAppTime: "+str(duration)+" msec")

