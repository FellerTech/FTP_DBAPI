#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Types

Arrays and objects require new layouts?

object.key
object.value
object.template

template:
- type: type of value 
   "type": int, string, float, list, dict, undefined

an undefined type can be anything, but it will not be included in the interface (although it may be displayed as a string)


#example for list
{
   "value":<value>,
   "template":{
      "type":"list",
      "template:"{
         "key":<name>
         "type":<type>
      }
   }

}

"""

class SmartType:
   types = ["string", "integer", "float", "bool", "list", "dict"]

   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] template Json object that defines what the object may contain
   def __init__(self, key, value, template=None):
       self.key = key
       self.type = "Unknown"

       print(str(key)+" template: "+str(template))

       self.template = None
       if template != None:
          self.setTemplate( template)

          try:
             self.type = template["type"]
          except: 
              pass

       print(str(key)+" Setting value to "+str(value)+" with template: "+str(self.template))
       self.value = value

       #If a template is undefined, the value is converted to a reado-only string
       if self.template == None:
           print("No template for key "+str(self.key))
           self.value = str( value )
           self.readOnly = True


   ##
   # \brief sets the template for the Type
   # \param [in] template Json object that specifies information about the object
   # \return true on success, false on failure
   #
   def setTemplate( self, template ):
       print("New template: "+str(template))
       #If not specified, read only. 
       if template == None:
           self.template = template
           return True

       #Make sure we are a dictionary
       elif not isinstance( template, dict ):
           print("Error: Template is not a dictionary"+str(template))
           return False

       self.template = template

       return True

   ##
   # \brief specifies the value that the device should have
   # \param [in] Value to set. 
   # \return true on success, false on failure
   #
   def setValue(self, value ):
       #If a template is undefined, the value is converted to a reado-only string
       if self.template == None:
           print("No template for key "+str(self.key))
#           self.value = str( value )
           self.value = value
           self.readOnly = True
           return True

       print(str(self.key)+" value:"+str(self.value)+", template:"+str(self.template))

       #check template type
       if self.template["type"] == "string":
           if isinstance( value, str):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type "+str(self.value)+" does not match template type of \"string\"")
               return False

       elif self.template["type"] == "integer":
           if isinstance( value, int ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match template type of \"integer\"")
               return False

       elif self.template["type"] == "float":
           if isinstance( value, float ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match template type of \"float\"")
               return False

       elif self.template["type"] == "bool":
           if isinstance( value, bool ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match template type of \"bool\"")
               return False

       elif self.template["type"] == "dict":
           print(str(self.key)+" dict value:"+str(value)+", template:"+str(self.template))
         
           if isinstance( value, dict ):
               self.value = value
           elif self.value != None:
               print( "Value:"+self.value)
               print("SmartType::Error - Value type does not match template type of \"dict\"")
               return False
           print(str(self.key)+" set dict value:"+str(self.value)+", template:"+str(self.template))


       elif self.template["type"] == "list":
           if isinstance( value, list ):
               self.value = value
           elif self.value != None:
               print("SmartType::Error - Value type does not match template type of \"list\"")
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
       if self.template["type"] == "string":
          try: 
              self.setValue( str(text))
          except:
              return False

       #Set to string
       if self.template["type"] == "integer":
          try: 
              self.setValue( int(text))
          except:
              return False

       #Set to string
       if self.template["type"] == "float":
          try: 
              self.setValue( float(text))
          except:
              return False

       #Set to string
       if self.template["type"] == "bool":
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
       if self.template["type"] == "dict":
           print("SmartType::setStringAsValue Unable to convert string to dict.")
           return False

       #Set to string
       if self.template["type"] == "list":
           print("SmartType::setStringAsValue Unable to convert string to list.")
           return False

       return True




##
# \brief Test function
def unitTest():
      ###############
      #Test strings
      ###############

      type1 = SmartType( "string", "value1", {"type":"string"})
      if type1.value != "value1":
          print("key 1 Unable to set string value")
          return False

      if not type1.setStringAsValue("test2"):
          print("Unable to set string value for string")
          return False

      #try non-string values
      if type1.setValue(15):
          print("FAILURE set string to an integer")
          return False

      ###############
      #Test Integers
      ###############
      type1 = SmartType( "integer", 1, {"type":"integer"})
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
          print("FAILURE set integer to a string")
          return False

      ###############
      # Test Floats
      ###############
      type1 = SmartType( "float", 1.1, {"type":"float"})
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
      type1 = SmartType( "bool", True, {"type":"bool"})
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
          print("FAILURE set bool to an integer")
          return False

      ###############
      # Test Lists
      ###############
      data = [1,2,3,4]
      type1 = SmartType( "list", data, {"type":"list"})

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
      type1 = SmartType( "dict", data, {"type":"dict"})
      if type1.value != data:
          print("Failure: dict value not set to "+str(data))
          return False

      #try non-string values
      if type1.setValue(99):
          print("FAILURE set dict to a string")
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
