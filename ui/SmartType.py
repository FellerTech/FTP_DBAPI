#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Types

Arrays and objects require new layouts?

object.key
object.value
object.schema

schema:
- type: type of value 
   "type": int, string, float, list, dict, undefined

an undefined type can be anything, but it will not be included in the interface (although it may be displayed as a string)


#example for list
{
   "value":<value>,
   "schema":{
      "type":"list",
      "schema:"{
         "key":<name>
         "type":<type>
      }
   }

}

"""

class SmartType:
   types = ["string", "int", "float", "bool", "list", "object"]

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] schema Json object that defines what the object may contain
   def __init__(self, key, value, schema=None):
       self.key = key
       self.type = "Unknown"

       self.schema= None
       if schema != None:
          self.setSchema( schema)

          try:
             self.type = schema["bsonType"]
          except: 
              pass

       print(str(key)+" Setting value to "+str(value)+" with schema: "+str(self.schema))
       self.value = value

       #If a schema is undefined, the value is converted to a reado-only string
       if self.schema == None:
           print("No schema for key "+str(self.key))
           self.value = str( value )
           self.readOnly = True


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
   def setValue(self, value ):
       #If a schema is undefined, the value is converted to a reado-only string
       if self.schema == None:
           print("No schema for key "+str(self.key))
#           self.value = str( value )
           self.value = value
           self.readOnly = True
           return True

       print(str(self.key)+" value:"+str(self.value)+", schema:"+str(self.schema))

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

       elif self.schema["bsonType"] == "float":
           if isinstance( value, float ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match schema type of \"float\"")
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
               print( "Value:"+str(self.value))
               print("SmartType::Error - Value type does not match schema type of \"object\"")
               return False
           print(str(self.key)+" set object value:"+str(self.value)+", schema:"+str(self.schema))


       elif self.schema["bsonType"] == "list":
           if isinstance( value, list ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match schema type of \"list\"")
               return False

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
       if self.schema["bsonType"] == "int":
          try: 
              self.setValue( int(text))
          except:
              return False

       #Set to string
       if self.schema["bsonType"] == "float":
          try: 
              self.setValue( float(text))
          except:
              return False

       #Set to string
       if self.schema["bsonType"] == "bool":
          #Convert string to boolean type
          if text == "True":
              bval = True
          elif text == "False":
              bval = False
          else:
              return False;

          try: 
              self.setValue( bval )
          except:
              return False

       #Set to string
       if self.schema["bsonType"] == "object":
           print("SmartType::setStringAsValue Unable to convert string to object.")
           return False

       #Set to string
       if self.schema["bsonType"] == "list":
           print("SmartType::setStringAsValue Unable to convert string to list.")
           return False

       return True




##
# \brief Test function
def unitTest():
      ###############
      #Test strings
      ###############

      type1 = SmartType( "string", "value1", {"bsonType":"string"})
      if type1.value != "value1":
          print("key 1 Unable to set string value")
          return False

      if not type1.setStringAsValue("test2"):
          print("Unable to set string value for string")
          return False

      #try non-string values
      if type1.setValue(15):
          print("FAILURE set string to an int")
          return False

      ###############
      #Test Integers
      ###############
      type1 = SmartType( "int", 1, {"bsonType":"int"})
      if type1.value != 1:
          print("Failure: Value not set to 1")
          return False

      if not type1.setStringAsValue("2"):
          print("Unable to set string value for int")
          return False

      if type1.value != 2:
          print("Failure: Value not set to 1")
          return False

      #try non-string values
      if type1.setValue("test"):
          print("FAILURE set int to a string")
          return False

      ###############
      # Test Floats
      ###############
      type1 = SmartType( "float", 1.1, {"bsonType":"float"})
      if type1.value != 1.1:
          print("Failure: Float value not set to 1.1")
          return False

      if not type1.setStringAsValue("1.2"):
          print("Unable to set string value for float")
          return False

      if type1.value != 1.2:
          print("Failure: Float value not set to 1.1")
          return False

      #try non-string values
      if type1.setValue(99):
          print("FAILURE set float to a string")
          return False
      
      ###############
      # Test Bools
      ###############
      type1 = SmartType( "bool", True, {"bsonType":"bool"})
      if type1.value != True:
          print("Failure: Bool value not set to True")
          return False

      if not type1.setStringAsValue("False"):
          print("Unable to set string value for bool")
          return False

      if type1.value != False:
          print("Failure: Bool value not set to False")
          return False

      #try non-string values
      if type1.setValue(99):
          print("FAILURE set bool to an int")
          return False

      ###############
      # Test Lists
      ###############
      data = [1,2,3,4]
      type1 = SmartType( "list", data, {"bsonType":"list"})

      if type1.value != data:
          print("Failure: list value not set to "+str(data))
          return False

      #try non-string values
      if type1.setValue(99):
          print("FAILURE set list to a string")
          return False

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



if __name__ == '__main__':
    result = unitTest()

    if result == True:
        print( "Unit test passed")
        exit(1)
    else:
        print( "Unit test FAILED")
