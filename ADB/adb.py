#!/usr/bin/python3
import argparse
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
import json
import time
from collections import OrderedDict

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

    def getCollections(self):
       return self.client[self.dbase].collection_names()
    ##
    # \brief Function to get the specified indexes for the given database
    def getIndexes(self, collection):
        if self.db == None:
           print("A database must be selected before getIndexes call")
           return
   
        return self.db[collection].index_information()

    ##
    # \brief Returns the structure of the mongo system
    # \return object where the keys are the databases and the values are the list of collections
    def getDbStructure(self):
        dbs = self.client.database_names()
        dbStructure = {}
        for item in dbs:

           try:
               dbStructure[item] = self.client[item].list_collection_names()
           except:
               pass
            
        return dbStructure;

    ##
    #\brief creates a collection
    def createCollection( self, name, schema = None ):
       if schema != None:
           validator = {}
           validator["validator"] = schema
           self.db.createCollection( name, validator )
       else:
           self.db.createCollection( name )

    ##
    # \brief returns the schema for the current collection
    #
    # SDF - this need to be cleaner
    def getSchema(self, collection):
#       print("getting schema for "+str(collection)+" in database: "+str(self.db))
       info = self.db.command({"listCollections":1, "filter":{"name":collection}})
       result = info["cursor"]["firstBatch"][0]["options"]["validator"]["$jsonSchema"]
       return  result

    ##
    # \brief updates the schema for the specified collection
    def setSchema( self, collection, schema ):
        query = { "$jsonSchema":{ "bsonType":"object"},
                  "valdator":schema
                }      
  
        self.db.command({"collMod": collection, "validator":query})

        s2 = self.getSchema(collection)
        
        return True
    

    ##
    # \brief return the URI of the current sesion
    def getUri(self):
        return self.uri


def test(uri):

    print("Unit test")
     
    #Create database
    #check if database exists. If so, print message and bail
    #create database object
    adb = ADB(uri)
    
    adb.setDatabase("adbTestDB")

    collections = adb.getCollections()
#    if len(collections) > 0 :
#        print("adbTest database is not empty")
#        retury False

    #create test1 collection
    collection1 = "temp"

    #create test1 schema
#    schema = { "bsonType":"object", "properties":{ "name":{"bsonType":"string"}}}
    schema = {"name":{"$bsontype":"string"}}
    adb.setSchema( collection1, schema ) 
    schema2 = adb.getSchema( collection1 )

    if schema2 != schema:
        print("Failure setting schema")
        print("schema: "+str(schema))
        print(str(schema2))
        return False

    #test test1 schema
        #Good cases

        #bad cases

    #remove test1 collection

    #remove test database

def main():
    dbase = "test"
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

    #############################################
    # Begin testing
    #############################################
    if args.test:
       return test(uri)


    #create database object
    adb = ADB(uri)

    #Specify the database to use
    adb.setDatabase(dbase);



    #start queries
    query = {}
    query["streamIds"] = "XX00000000000000070019-300729315229696-3"
    
    first = int(adb.db["files"].find().limit(1).sort('startTime',1).limit(1)[0]["startTime"])
    last  = int(adb.db["files"].find().limit(1).sort('startTime',-1).limit(1)[0]["startTime"])
    
#    first = 1547455075781943
#    last  = 1552821334105828

#    print("First: "+str(( first/1e6))+","+str(int(oldest[0]["startTime"])/1e6))
#    print("Last: "+str(( last/1e6))+","+str(int(newest[0]["startTime"])/1e6))

    print("First: "+str(datetime.utcfromtimestamp( first/1e6)))
    print("Last: "+str(datetime.utcfromtimestamp( last/1e6)))


    target = first + 100
    samples = 100

    step = ( last - first)/samples 
    print("last: "+str(last)+", target: "+str(target)+", step: "+str(step))

    count = 0

    while( target < last ):

#    start = 1547455128795134
#    end   = 1547455181751895  
#    target = str(start+(end-start)/2)

        query = {}
#        query["startTime"] = {"$lte":str(target)}
        query["endTime"] = {"$gte":str(target)}
#        query["streamIds"] = "XX00000000000000070019-300729315229696-3"
    
    
        start = time.time()
#        result = adb.db["files"].find(query).limit(1).explain()["executionStats"]
        result = adb.db["files"].find(query).limit(1)



        for item in result:
#            item["_id"] = str(item["_id"])
#            print( json.dumps(item, indent = 3))
            offset = (target - int( item["startTime"]))/1e6

            end = time.time()
            elapsed = str(end-start)

            print(str(count)+": "+elapsed+" seconds, time offset: "+str(offset)+", id:"+str(item["_id"]))
        target = target + step
        count  = count  + 1


if __name__ == "__main__":
   main()
