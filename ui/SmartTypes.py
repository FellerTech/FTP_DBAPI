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
   types = ["string", "integer", "float", "list", "dict"]

   def __init__(self):
       return 
   ##
   # \brief Default initializer
   # \param [in] key name of the item
   # \param [in] value value to set the item to
   # \param [in] template Json object that defines what the object may contain
   def init(self, key, value, template):
       self.key      = key

       self.setTemplate( template)
       self.setvalue(value)

   ##
   # \brief sets the template for the Type
   # \param [in] template Json object that specifies information about the object
   # \return true on success, false on failure
   #
   def setTemplate( self, template ):

       # Check required fields
       # Make sure we have the required fields
       try:
           value = self.types.index(template["type"])
       except:
           print("SmartType::Error - Invalid template type of "+str(template["type"]))
           return False

       #Make sure we have a key
       try:
           value = template["key"]
       except:
           print("SmartType::Error - template missing key")
           return False


       #Make sure array and dict types have sub templates
       if template["type"] == "dict" or template["type"] == "list":
           try: 
               subTemplate = template["template"]
           except:
               print("SmartType::Error - dict and list types must have sub template fields")
               return False

           self.subType = SmartType()
           if not self.subType.setTemplate(subTemplate):
               print("Invalid subTemplate for "+template["key"])

       # Make sure optional fields have reasonable values


       #Make sure required required data is needed
       self.template = template

       return True

   ##
   # \brief specifies the value that the device should have
   # \param [in] Value to set. 
   # \return true on success, false on failure
   #
   def setValue(self, value ):
       #make sure we have a template
       try:
           self.template 
       except:
           print("SmartType::Error - trying to set value without template")
           return False

       #check template type
       if self.template["type"] == "string":
           if isinstance( value, str):
               self.value = value
           else:
               print("SmartType::Error - Value type does not match template type of \"string\"")
               return False

       if self.template["type"] == "integer":
           if isinstance( value, int ):
               self.value = value
           else:
               print("SmartType::Error - Value type does not match template type of \"integer\"")
               return False

       if self.template["type"] == "float":
           if isinstance( value, float ):
               self.value = value
           else:
               print("SmartType::Error - Value type does not match template type of \"float\"")
               return False

       if self.template["type"] == "dict":
           if isinstance( value, dict ):
               self.value = value
           else:
               print("SmartType::Error - Value type does not match template type of \"dict\"")
               return False

       if self.template["type"] == "list":
           if isinstance( value, list ):
               self.value = value
           else:
               print("SmartType::Error - Value type does not match template type of \"list\"")
               return False

       return True

   ##
   # \brief Test function
   def unitTest(self):
      tplate={} 
      tplate["key"] = "test"

      ###############
      #Test strings
      ###############
      tplate["type"]="string"

      rc = self.setTemplate( tplate )
      if( rc == False ):
         print("Failed to set template type to string")
         return rc

         if self.template["type"] != tplate["type"]:
            print("Failed to template type not set to string")
            return False

      #Check setting values
      if not self.setValue("value1"):
          print("Unable to set string value")
          return False

      if self.value != "value1":
          print("Value not set to value1")
          return False

      #try non-string values
      if self.setValue(15):
          print("FAILURE set string to an integer")
          return False

      ###############
      #Test Integers
      ###############
      tplate["type"]="integer"

      rc = self.setTemplate( tplate )
      if( rc == False ):
         print("Failed to set template type to integer")
         return rc

         if self.template["type"] != tplate["type"]:
            print("Failed to template type not set to integer")
            return False

      #Check setting values
      if not self.setValue(1):
          print("Unable to set integer value")
          return False

      if self.value != 1:
          print("Failure: Value not set to 1")
          return False

      #try non-string values
      if self.setValue("test"):
          print("FAILURE set integer to a string")
          return False

      ###############
      # Test Floats
      ###############
      tplate["type"]="float"

      rc = self.setTemplate( tplate )
      if( rc == False ):
         print("Failed to set template type to float")
         return rc

         if self.template["type"] != tplate["type"]:
            print("Failed to template type not set to float")
            return False

      #Check setting values
      if not self.setValue(1.1):
          print("Unable to set float value")
          return False

      if self.value != 1.1:
          print("Failure: Float value not set to 1.1")
          return False

      #try non-string values
      if self.setValue(99):
          print("FAILURE set float to a string")
          return False

      ###############
      # Test Lists
      ###############
      tplate["type"]="list"
      subtemp = {}
      subtemp["type"] = "string"
      subtemp["key"] = "subtemp"

      tplate["template"]=subtemp
      data = [1,2,3,4]

      rc = self.setTemplate( tplate )
      if( rc == False ):
         print("Failed to set template type to list")
         return rc

         if self.template["type"] != tplate["type"]:
            print("Failed to template type not set to list")
            return False

      #Check setting values
      if not self.setValue(data):
          print("Unable to set list value to "+str(data))
          return False

      if self.value != data:
          print("Failure: list value not set to "+str(data))
          return False

      #try non-string values
      if self.setValue(99):
          print("FAILURE set list to a string")
          return False

      ###############
      # Test Dicts
      ###############
      tplate["type"]="dict"
      subtemp = {}
      subtemp["type"] = "string"
      subtemp["key"] = "subtemp"

      tplate["template"]=subtemp
      data = {}
      data["key"]="value"

      rc = self.setTemplate( tplate )
      if( rc == False ):
         print("Failed to set template type to dict")
         return rc

         if self.template["type"] != tplate["type"]:
            print("Failed to template type not set to dict")
            return False

      #Check setting values
      if not self.setValue(data):
          print("Unable to set dict value to "+str(subtemp))
          return False

      if self.value != data:
          print("Failure: dict value not set to "+str(data))
          return False

      #try non-string values
      if self.setValue(99):
          print("FAILURE set dict to a string")
          return False
     
      ###############
      # Test Error States
      ###############
      print("---------- Testing Error Conditions ----------")
      #Test non-specified types
      tplate = {}
      tplate["key"] = "test"
      tplate["type"]="asdf"
      rc = self.setTemplate( tplate )
      if( rc ):
          print("ERROR: Invalid tempate type accepted.")
          return False

      #Make sure we fail when there is no key
      tplate = {}
      tplate["type"]="string"
      rc = self.setTemplate( tplate )
      if( rc ):
          print("ERROR: template without key accepted.")
          return False
      print("---------- Done Testing Error Conditions ----------")
      return True



if __name__ == '__main__':
    result = SmartType().unitTest()

    if result == True:
        print( "Unit test passed")
        exit(1)
    else:
        print( "Unit test FAILED")
