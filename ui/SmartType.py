#!/usr/bin/python3
# -*- coding: utf-8 -*-

class SmartType:
   types = ["string", "int", "float", "bool", "array", "object"]

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] schema Json object that defines what the object may contain
   def __init__(self, key, value, schema=None):
       self.key = key
       self.type = "Unknown"
       self.value = None

       self.schema= None
       if schema != None:
          self.setSchema( schema)

          try:
             self.type = schema["bsonType"]
          except: 
              pass

             

#       print(str(key)+" setting value to "+str(value)+" with schema: "+str(self.schema))
       
#       self.value = value

       #If a schema is undefined, the value is converted to a reado-only string
       if self.schema == None:
           print("No schema for key "+str(self.key))
           self.value = str( value )
           self.readOnly = True
       else:
           self.setValue(value)


   ##
   # \brief sets the schema for the Type
   # \param [in] schema Json object that specifies information about the object
   # \return true on success, false on failure
   #
   def setSchema( self, schema ):
       #If not specified, read only. 
       if schema == None:
           self.schema =schema 
           return True

       #Make sure we are a dictionary
       elif not isinstance( schema, dict ):
           print("Error: schema is not a object "+str(schema))
           return False

       self.schema = schema 

       return True

   ##
   # \brief specifies the value that the device should have
   # \param [in] Value to set. 
   # \return true on success, false on failure
   #
   # This function is used to set a new value to  item
   def setValue(self, value ):
       self.value = None
#       print("Setting value to "+str(value))

       #If a schema is undefined, the value is converted to a reado-only string
       if self.schema == None:
           print("No schema for key "+str(self.key))
           self.value = value
           self.readOnly = True
           return True

       #check schema type
       if self.schema["bsonType"] == "string":
           if isinstance( value, str):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type "+str(self.value)+" does not match schema type of \"string\"")
               return False

       elif self.schema["bsonType"] == "int":
           if isinstance( value, int ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match schema type of \"int\"")
               return False

       elif self.schema["bsonType"] == "double":
           if isinstance( value, float ) or isinstance( value, int ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match schema type of \"double\"")
               return False

       elif self.schema["bsonType"] == "bool":
           if isinstance( value, bool ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match schema type of \"bool\"")
               return False

       elif self.schema["bsonType"] == "object":
           print(str(self.key)+" object value:"+str(value)+", schema:"+str(self.schema ))
         
           if isinstance( value, dict ):
               self.value = value
           elif self.value != None:
               print( "---- Value:"+str(self.value))
               print( "SmartType::Error - Value type does not match schema type of \"object\"")
               return False

       #We are an array type
       elif self.schema["bsonType"] == "array":
           #if the value is not a list, return false. 
           if not isinstance( value, list ):
               print("SmartType::Error - unable to set an array type to a non-array value")
               return False

           #If any items are not of the correct type print an error and set valiu to False
           valid=True

           #Try/catch for unspecified schema. If the schema is not specified, treat it as mixed
           #Mixed type not validated since anything goes
           try:
               for item in value:
                   if self.schema["items"]["bsonType"] == "string":
                       if not isinstance( item, str):
                           print("SmartType::Error array schema mismatch -"+ str(item)+" is not a string")
                           valid = False
                   elif self.schema["items"]["bsonType"] == "int":
                       if not isinstance( item, int):
                           print("SmartType::Error array schema mismatch -"+ str(item)+" is not an integer")
                           valid = False
                   elif self.schema["items"]["bsonType"] == "double":
                       if not isinstance( item, float) and not isinstance( item, int):
                           print("SmartType::Error array schema mismatch -"+ str(item)+" is not a double")
                           valid = False
                   elif self.schema["items"]["bsonType"] == "bool":
                       if not isinstance( item, bool):
                           print("SmartType::Error array schema mismatch -"+ str(item)+" is not a bool")
                           valid = False
                   elif self.schema["items"]["bsonType"] == "array":
                       if not isinstance( item, list):
                           print("SmartType::Error array schema mismatch -"+ str(item)+" is not an array")
                           valid = False
                   elif self.schema["items"]["bsonType"] == "object":
                       if not isinstance( item, dict):
                           print("SmartType::Error object schema mismatch -"+ str(item)+" is not an object")
                           valid = False
                   elif self.schema["items"]["bsonType"] != "mixed":
#                   else:
                       print("SmartType::Error unknown type: "+str(self.schema["items"]["bsonType"]))
                       valid = False
           except:
               #SDF: Need a NOP....`
               print("SmartType::Warning Using mixed type as a default")

           #If any item fails, return false
           if not valid:
               print("SmartType::Error Failed to set value:" + str(value))
               return False

           else:
               self.value = value
               return True

       return True
   ##
   # \brief Append a vlue to an array
   # \param in value the new value to append to the array
   def appendValue( self, value ):
       #If we're not an array type, print ann erro and return false
       if self.type != "array":
           print("SmartType::error: Non-array types cannot append values") 
           return False

       #See if we have a schema. If not, add value by default and exit 
       if self.schema == None:
           self.value.append(value)
           return True
            
       #We should have a schema. Let's figure out if its a match
       valid = True
       try:
           #If the schema doesn't specify a type
           if isinstance(self.schema["items"]["bsonType"], str):
               if self.schema["items"]["bsonType"] == "string":
                   if not isinstance( value, str):
                       valid = False
               elif self.schema["items"]["bsonType"] == "int":
                   if not isinstance( value, int):
                       valid = False
               elif self.schema["items"]["bsonType"] == "double":
                   if not isinstance( value, float) and not isinstance( value, int):
                       print(str(value)+" is not a double")
                       valid = False
               elif self.schema["items"]["bsonType"] == "bool":
                   if not isinstance( value, bool):
                       valid = False
               elif self.schema["items"]["bsonType"] == "object":
                   if not isinstance( value, dict):
                       valid = False
               elif self.schema["items"]["bsonType"] == "array":
                   if not isinstance( value, list):
                       valid = False
               elif self.schema["items"]["bsonType"] != "mixed":
                   valid = False


               if not valid:
                   print( str(item)+" is not of type "+str(self.schema["items"]["bsonType"])) 
               else:
                   self.value.append( value  )
                   prnt("Appending value "+str(value))
                   return True
           else:
              print("SmartType::Error: Schema type is not a string")
              return False
       except:
           print("SmartType::Error: Invalid schema "+str(self.schema))
           return False

       print("Appending True")
       return True

   ##
   # \brief Tries to set the string to the given type
   def setStringAsValue( self, text ):
       #make sure the input is a string
       if not isinstance( text, str ):
           print("SmartType::setStringAsValue input not string")
           return False

       #Set to string
       if self.schema["bsonType"] == "string":
          try: 
              self.setValue( str(text))
          except:
              return False

       #Set to string
       elif self.schema["bsonType"] == "int":
          try: 
              self.setValue( int(text))
          except:
              return False

       #Set to string
       elif self.schema["bsonType"] == "double":
          try: 
              self.setValue( float(text))
          except:
              return False

       #Set to string
       elif self.schema["bsonType"] == "bool":
          #Convert string to boolean type
          if text == "True":
              bval = True
          elif text == "False":
              bval = False
          else:
              return False;

          try: 
              self.setValue(bval)
          except:
              return False

       #Set to string
       elif self.schema["bsonType"] == "object":
           print("SmartType::setStringAsValue Unable to convert string to object.")
           return False

       #Set to string
       elif self.schema["bsonType"] == "array":
           print("SmartType::setStringAsValue Unable to convert string to array.")
           return False
       else:
           print("SmartType::Error Invalid bsonType of "+self.schema["bsonType"])

       return True
   ##
   #\brief returns the software version
   def getVersion(self):
       return "2.0.1"
##
# \brief Test function
def unitTest():
      ###############
      # Test data
      ###############
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
                   {"value":[[11,12,13],[4,5,6],[7,8,9]], "schema": {"bsonType":"array", "items":{"bsonType":"array", "items":{"bsonType":"int"}}}},
                   {"value":[{"key1":1},{"key2":2},{"key3":3}], "schema": {"bsonType":"array", "items":{"bsonType":"object","items":{"bsonType":"int"}}}}
         ],
         "objects":[
                    {"value":{"k1":1,"k2":2,"k3":3}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"int"}}}},
                    {"value":{"k1":"S1","k2":"s2","k3":"s3"}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"string"}}}},
##                    {"value":{"k1":1.2,"k2":2,"k3":True}, "schema":{"bsonType":"object", "properties":{"k1":"double"}}},
                    {"value":{"k1":1.2,"k2":2,"k3":True}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"double"}}}},
                    {"value":{"k1":False,"k2":True,"k3":True}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"bool"}}}},
##                    {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
##                    {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "items":{"bsonType":"mixed"}}},
##                    {"value":{"k1":False,"k2":"test","k3":2.0}, "schema":{"bsonType":"object", "properties":{"k1":"mixed"}}},
                    {"value":{"k1":[1,2,3],"k2":[4,5,6]}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"array","items":{"bsonType":"int"}}}}},
                    {"value":{"k1":{"k11":1,"k12":2,"k13":3},"k2":{"k21":4,"k22":5,"k23":6}}, "schema":{"bsonType":"object", "properties":{"k1":{"bsonType":"object","properties":{"k11":{"bsonType":"int"}}}}}}
         ]
    })
      
      #Get a list of all keys in the test array. This will be used for comparison
      #keys = testData["arrays"].keys()
      keys = testData.keys()

      #Loop through each entry in testData
      for key in keys:
          for item in testData[key]:
              schema = item["schema"]
          
              #Loop through all entries and try to set values
              for key2 in keys:
                   for item2 in testData[key2]:
                       value = item2["value"]

                       smartType = SmartType(key, value, schema )
                       result = smartType.setValue(value)

                       #sdf need to make to check the correct values
                       if result == False:
                           if ( item["schema"] == item2["schema"] or
                                (item["schema"]["bsonType"] == "int" and item2["schema"]["bsonType"] == "bool") or
                                (item["schema"]["bsonType"] == "double" and item2["schema"]["bsonType"] == "bool") or
                                (item["schema"]["bsonType"] == "double" and item2["schema"]["bsonType"] == "int")
                              ):
                               print("Invalid result with result with valid schema")
                               print("key1:"+str(key))
                               print("key2:"+str(key2))
                               print("schema:"+str(schema))
                               print("value:"+str(value))
                           
                               return False
                 
                              
                               
                           """
                           if ( key == key2 or
                                key == "mixed" or
                                (key == "int" and key2 == "bool") or
                                (key == "double" and key2 == "bool") or
                                (key == "double" and key2 == "int")
                           ):
                               print("Valid result with mismatched keys")
                               print("key1:"+str(key))
                               print("key2:"+str(key2))
                               print("schema:"+str(schema))
                               print("value:"+str(value))
                           
                               return False
                           """
                       elif result == False and key == key2:
                           print("InValid result with matched keys")
                           return False

      return True

      ###############
      # Test Dicts
      ###############
      data = {"key":"value"}
      type1 = SmartType( "object", data, {"bsonType":"object"})
      if type1.value != data:
          print("Failure: object value not set to "+str(data))
          return False

      #try non-string values
      if type1.setValue(99):
          print("FAILURE set object to a string")
          return False
     
      ###############
      # Test Error States
      ###############
      return True

##
# \brief Main function
if __name__ == '__main__':
    result = unitTest()

    if result == True:
        print( "Unit test passed")
        exit(1)
    else:
        print( "Unit test FAILED")
