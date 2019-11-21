#!/usr/bin/python3
import argparse
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
from bson import ObjectId
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
        self.dbase = None

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
    def getCurrentDatabase(self):
        return self.dbase 

    ##
    # \brief returns a list of databases
    def getDatabaseList(self):
        return self.client.database_names()

    def getCollections(self):
       if self.dbase is None:
           return []

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
       try:
           result = info["cursor"]["firstBatch"][0]["options"]["validator"]["$jsonSchema"]["properties"]
       except:
           result = {}
#       result = info["cursor"]["firstBatch"][0]["options"]["validator"]["$jsonSchema"]
       return  result


    ##
    # \brief updates the schema for the specified collection
    def setSchema( self, collection, schema ):
        validator = { 
            "$jsonSchema":{ 
                "bsonType":"object", 
                "properties": schema
            }
        }
        
        try:
            self.db.command({"collMod": collection, "validator": validator})
        except:
            print("Collection: "+str(collection)+" failed to setSchema ")
            print("schema: "+str(schema) )
            return False

#        s2 = self.getSchema(collection)
        
        return True
    

    ##
    # \brief return the URI of the current sesion
    def getUri(self):
        return self.uri


    ##
    # \brief queries based on the given query
    # \param [in] collection the collection to perform the query on
    # \param [in] query query to perform
    # \param [in] limit number of items to return
    def getDocuments( self, collection, query={}, limit=1 ):
        docs = []
      
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])
        for doc in self.db[collection].find(query).limit(limit):
            if "_id" in doc.keys():
                #All "_id" fields are converted to strings on queries. They must
                #be re-converted on insert
                doc["_id"] = str(doc["_id"])
           
                docs.append(doc)
             
        return docs

    ##
    # \brief inserts a document into the database
    # \return False on failure. On success, new object as entered into database
    def insertDocument( self, collection, doc, update = True ):
       duplicate = False

       #to object Ids
       if "_id" in doc.keys():
            doc["_id"] = ObjectId(doc["_id"])
            print("new id on insert:"+str(doc["_id"]))

            #If there is a key, see if it exists
            matches = self.getDocuments(collection, {"_id":doc["_id"]})
            if len(matches) > 0:
                duplicate = True

       if duplicate and not update:
            print("Document exists with update disabled. Unable to insert")
            return False

       elif duplicate and update:
            print("Updating an existing record")
            try:
                query = {"_id":ObjectId(doc["_id"])}
                self.db[collection].update(query, doc)
                doc["_id"] = str(doc["_id"])
            except:
                print("Failed to update and existing docuement")
                doc["_id"] = str(doc["_id"])
                return False
       else:
            print("Inserting a new document"+str(doc))
            try:
                print("Inserting: "+str(doc))

                #Extrin
                result = self.db[collection].insert_one(doc)
                print("Result: "+str(result.acknowledged))
                if not result.acknowledged:
                     print("Failed to insert data")
                     return False
                print("NEW ID:"+str(result.inserted_id))
                doc["_id"] = str(result.inserted_id)
                
            except:
                print("insert exception for "+str(doc))
                return False

       return doc


def test(uri, testDB = "adbTestDB" ):

    print("Unit test")
    testData = ({
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
                   {"value":{"key":[{"key1":1},{"key2":2},{"key3":3}]}, "schema":{"key": {"bsonType":"array", "items":{"bsonType":"object","items":{"bsonType":"int"}}}}}
         ],
         "objects":[
                    {"value":{"key":{"k1":1,"k2":2,"k3":3}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"int"}}}}},
                    {"value":{"key":{"k1":"S1","k2":"s2","k3":"s3"}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"string"}}}}},
#                    {"value":{"key":{"k1":1.2,"k2":2,"k3":True}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":"double"}}}}},
                    {"value":{"key":{"k1":1.2,"k2":2,"k3":True}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"double"}}}}},
                    {"value":{"key":{"k1":False,"k2":True,"k3":True}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"bool"}}}}},
##                    {"value":{"key":{"k1":False,"k2":"test","k3":2.0}}, "schema":{"key":{"bsonType":"object", "items":{"bsonType":"mixed"}}}},
##                    {"value":{"key":{"k1":False,"k2":"test","k3":2.0}}, "schema":{"key":{"bsonType":"object", "items":{"bsonType":"mixed"}}}},
##                    {"value":{"key":{"k1":False,"k2":"test","k3":2.0}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":"mixed"}}},
                    {"value":{"key":{"k1":[1,2,3],"k2":[4,5,6]}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"array","items":{"bsonType":"int"}}}}}},
                    {"value":{"key":{"k1":{"k11":1,"k12":2,"k13":3}},"k2":{"k21":4,"k22":5,"k23":6}}, "schema":{"key":{"bsonType":"object", "properties":{"k1":{"bsonType":"object","properties":{"k11":{"bsonType":"int"}}}}}}}
         ]
    })

     
    #Create database
    #check if database exists. If so, print message and bail
    #create database object
    adb = ADB(uri)

    
    #print list of databases
    print("Database List:"+str(adb.getDatabaseList()))   

    
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
            schema = item["schema"]

            #Set the schema to the specified item schema
            print("Setting schema to "+str(schema))
            adb.setSchema( collection1, schema )

            #Loop through all testData values and try to set. Should only
            #success if schemas match
            for key2 in keys:
                count = 0
                for item2 in testData[key2]:
#                   print("Creating collection: "+str(collection1)) 
#                   adb.createCollection( collection1 )

                   doc = item2["value"]
                   print("New Doc: "+str(doc))
                   doc2 = adb.insertDocument( collection1, doc)
                   print("Post Insert: "+str(doc))
                   if (doc2 != False ) and item2["schema"] != item["schema"]:
                       print("Error: Succeeded with schema mismatch for "+str(key)+"["+str(count)+"]:")
                       print("schema:"+str(item["schema"]))
                       print("schema2:"+str(item2["schema"]))
                       return False
                   elif (doc2 == False) and item2["schema"] == item["schema"]:
                       print("Error: Failed with schema match "+str(key))
                       print("schema:"+str(item["schema"]))
                       print("schema2:"+str(item2["schema"]))
                       return False
 
                   #It looks like we failed for a good reason. Continue to the next iter                  
                   elif doc2 == False:
                       continue

                   #We were successful. We need to query inserted value to make sure it 
                   #matches
                   #We should have a valid schema. Let's compare values
                   query = {"_id":doc["_id"]}
                   docs = adb.getDocuments( collection1, query, 10 )

                   #We should have only one answer
                   if len(docs) != 1:
                       print("Get documents returned "+str(len(docs))+" instead of 1 document")
                       return False
                   
                   if doc != docs[0]:
                       print("Document mismatch")
                       print("Doc1:"+str(doc))
                       print("Doc2:"+str(docs[0]))
                       return False

                   count = count +1
  
    
#        print("Removing collection: "+str(collection1)) 
#        adb.removeCollection( collection1 )


    #remove test1 collection
#    adb.removeCollection( collection1 )

    #remove test database
#    adb.removeDatabase(testDB)

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
