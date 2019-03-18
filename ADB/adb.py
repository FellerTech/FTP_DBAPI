#!/usr/bin/python3
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
import json

#Gets a list of databases and collections
class ADB:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri)
         
        self.getDbStructure()


    def getDbStructure(self):
        dbs = self.client.database_names()
        self.dbStructure = {}
        for item in dbs:

           try:
               self.dbStructure[item] = self.client[item].list_collection_names()
           except:
               pass
            
        return self.dbStructure;


    def getUri(self):
        return self.uri

if __name__ == '__main__':
    adb = ADB("10.0.0.177:27017")
#    adb = ADB("10.0.0.120:27017")

    print("Mongo database info at uri: "+adb.getUri())
    print( json.dumps(adb.getDbStructure(), indent = 3))
    
    """
    db = client.acos_local
    
    #list collections
    cols =  db.collections_names()
    
    print(str(cols))
    """
