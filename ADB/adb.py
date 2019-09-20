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
    # \brief Removes a database
    # \param [in] dbase name of the database to remove
    def removeDatabase( self, dbase ):
#        self.db["client"].dropDatabase( dbase )
        self.db.client.drop_database(dbase)

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
       #required to hold database open
       self.db[name].insert_one({"t":1})

       if schema != None:
           self.setSchema( name, schema )
    ##
    # \brief removes the specified collectoin
    def removeCollection( self, name ):
        self.db[name].drop()
   

    ##
    # \brief returns the schema for the current collection
    #
    # SDF - this need to be cleaner
    def getSchema(self, collection):
       info = self.db.command({"listCollections":1, "filter":{"name":collection}})
       result = info["cursor"]["firstBatch"][0]["options"]["validator"]["$jsonSchema"]["properties"]
       return  result

    def setValue( self, collection, value ):
       print("Collection " + str(collection) + " setting value to :"+str(value))
       try:
           result = self.db[collection].insert_one(value)
           output = result.acknowledged
       except:
           output = False

       return output

    ##
    # \brief updates the schema for the specified collection
    def setSchema( self, collection, schema ):
        query = { 
            "$jsonSchema":{ 
                "bsonType":"object", 
                "properties": schema
            }
        }
        
        print("Setting query:" +str(query))
        try:
            self.db.command({"collMod": collection, "validator":query})
        except:
            print("Failed to setSchema")
            print("Collection: "+str(collection))
            print("Query:" +str(query))
            exit(1)

        s2 = self.getSchema(collection)
        print()
        print("Returned Schema:"+str(s2))
        
        return True
    

    ##
    # \brief return the URI of the current sesion
    def getUri(self):
        return self.uri


def test(uri, testDB = "adbTestDB" ):

    print("Unit test")
    testData = ({
         "strings":[{"value":"test","schema":{"bsonType":"string"}},
                    {"value":"test2","schema":{"bsonType":"string"}}
         ],
         "integers":[{"value":1,"schema":{"bsonType":"int"}},
                     {"value":-1, "schema":{"bsonType":"int"}}
         ],
         "doubles":[{"value":1.5,"schema":{"bsonType":"double"}},
                    {"value":2.0,"schema":{"bsonType":"double"}}
         ],
         "booleans":[{"value":True, "schema": {"bsonType":"bool"}},
                    {"value":True, "schema": {"bsonType":"bool"}}
         ],
         "arrays":[{"value":["A","B","C"], "schema": {"bsonType":"array", "items":{"bsonType":"string"}}},
                   {"value":[1,2,3],"schema": {"bsonType":"array", "items":{"bsonType":"int"}}},
                   {"value":[1.1,2.1,3.1], "schema": {"bsonType":"array", "items":{"bsonType":"double"}}},
                   {"value":[True, False, True], "schema": {"bsonType":"array", "items":{"bsonType":"bool"}}},
#                   {"value":["A",2,True], "schema": {"bsonType":"array", "items":{"bsonType":"mixed"}}},
                   {"value":[[1,2,3],[4,5,6],[7,8,9]], "schema": {"bsonType":"array", "items":{"bsonType":"array", "items":{"bsonType":"int"}}}},
                   {"value":[{"key1":1},{"key2":2},{"key3":3}], "schema": {"bsonType":"array", "items":{"bsonType":"object","items":{"bsonType":"int"}}}}
         ],
         "objects":[
                    {"value":{"k1":1,"k2":2,"k3":3}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"int"}}}},
                    {"value":{"k1":"S1","k2":"s2","k3":"s3"}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"string"}}}},
#                    {"value":{"k1":1.2,"k2":2,"k3":True}, "schema":{"bsonType":"object", "properties":{"k1":"double"}}},
                    {"value":{"k1":1.2,"k2":2,"k3":True}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"double"}}}},
                    {"value":{"k1":False,"k2":True,"k3":True}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"bool"}}}},
##                    {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
##                    {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
##                    {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "properties":{"k1":"mixed"}}},
                    {"value":{"k1":[1,2,3],"k2":[4,5,6]}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"array","items":{"bsonType":"int"}}}}},
                    {"value":{"k1":{"k11":1,"k12":2,"k13":3},"k2":{"k21":4,"k22":5,"k23":6}}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"object","properties":{"k11":{"bsonType":"int"}}}}}}
         ]
    })

     
    #Create database
    #check if database exists. If so, print message and bail
    #create database object
    adb = ADB(uri)
    
    adb.setDatabase(testDB)

    collections = adb.getCollections()
    if len(collections) > 0 :
        print("adbTest database is not empty")
#        return False

    #create test1 collection
    collection1 = "temp"

#    print("Creating collection: "+str(collection1)) 
#    adb.createCollection( collection1 )

    keys = testData.keys()

    # Loop through all items in testData
    for key in keys:
        adb.createCollection( collection1 )

        #Loop through each entry for the specified key
        for item in testData[key]:
            value = item["value"]

            #Set the schema to the specified item schema
            schema = {key:item["schema"]}
            print("Setting schema to "+str(schema))
            adb.setSchema( collection1, schema )

            #Loop through all testData values and try to set. Should only
            #success if schemas match
            for key2 in keys:
                for item2 in testData[key2]:
#                   print("Creating collection: "+str(collection1)) 
#                   adb.createCollection( collection1 )

                   print("Key:"+str(key))
                   result = adb.setValue( collection1, {key:item2["value"] })
                   if result and item2["schema"] != item["schema"]:
                       print("Error: Succeeded with schema mismatch for "+str(key)+":")
                       print("schema:"+str(item["schema"]))
                       print("schema2:"+str(item2["schema"]))
                       return False
                   elif not result and item2["schema"] == item["schema"]:
                       print("Error: Failed with schema match "+str(key))
                       print("schema:"+str(item["schema"]))
                       print("schema2:"+str(item2["schema"]))
                       return False
   
    
        print("Removing collection: "+str(collection1)) 
        adb.removeCollection( collection1 )

    """
    #create test1 schema
    # SDF - need to make sure this approach will support required and other fields
    schema1 = {"name":{"bsonType":"string"}}
                
        "strings":[{"value":"test","schema":{"bsonType":"string"}},
    adb.createCollection( collection1, schema1 )
    adb.setSchema( collection1, schema1 )

    #Compare set schema with returned schema
    schema2 = adb.getSchema( collection1 )
    if schema2 != schema1:
        print("Schema mismatch")
        print("expected: "+str(schema1))
        print("actual: "+str(schema2))
        return False

    #test test1 schema
    
        #Good cases

        #bad cases
    """

    #remove test1 collection
    adb.removeCollection( collection1 )

    #remove test database
    adb.removeDatabase(testDB)

    return True

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
        result = test(uri)
        if result:
            print("Unit test successfully passed")
        else:
            print("Unit test failed")
        return result

    """
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
    """


if __name__ == "__main__":
   main()
