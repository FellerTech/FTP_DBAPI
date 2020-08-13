#!/usr/bin/python3
import argparse
import json

##
# \brief Function to generate a schema from an existing json file
#
# This output of this function needs to be validated to ensure that the generated schema is correct
def generateSchema( value, initial = True ):
    schema = {}
    inputType = str(type(value).__name__)


    if inputType == "str":
        inputType = "string"
    if inputType == "float":
        inputType = "double"
    if inputType == "dict":
        inputType = "object"
    if inputType == "list":
        inputType = "array"


    #If we are an object, then build up the schema through recursion
    if inputType == "object":

        if initial == False:
            schema["bsonType"] = inputType
            schema["properties"] = {}

        for key in value.keys():
            subSchema = generateSchema(value[key], initial = False)

            if initial == False:
                schema["properties"][key] = subSchema
            else:
                schema[key] = subSchema



        #If we are an array, verify all items are compatible. If not, assign type to mixed
     
    elif inputType == "array":
        myType=None
        items = {}

        
        for item in value:
            itemType = type(item).__name__
      
            if myType == None:
                myType = itemType
 
            elif myType != itemType and myType != "mixed":
                myType = "mixed"

        schema["bsonType" ] = inputType
        schema["items"] = {}
        schema["items"]["bsonType"] = myType
        
         

    #We are a standard type. Just return type 
    else:
        #Try types
        schema["bsonType"] = inputType
    
    return schema


def test():
    success = True
    passed = 0
    total = 0
    values = []
    values.append({"value":{"string":"name"}, "schema":{"string":{"bsonType":"string"}}})
    values.append({"value":{"bool":True}, "schema":{"bool":{"bsonType":"bool"}}})
    values.append({"value":{"double":2.0}, "schema":{"double":{"bsonType":"double"}}})
    values.append({"value":{"int":-2}, "schema":{"int":{"bsonType":"int"}}})
    values.append({"value":{"array":[1, 2, 3]}, "schema":{"array":{"bsonType":"array","items":{"bsonType":"int"}}}})
    values.append({"value":{"object":{"item1":"string", "item2":2}}, "schema":{"object":{"bsonType":"object","properties":{"item1":{"bsonType":"string"},"item2":{"bsonType":"int"}}}}})
    values.append({"value":{"object":{"item1":{"s1":"string"}, "item2":2}}, "schema":{"object":{"bsonType":"object","properties":{"item1":{"bsonType":"object","properties":{"s1":{"bsonType":"string"}}},"item2":{"bsonType":"int"}}}}})

    #test all items in the values array
    for item in values:
        total = total+1

        result = generateSchema(item["value"])
        if result != item["schema"]:
            print("Failed test "+str(total))
            print("Result:"+json.dumps(result))
            print("Schema:"+json.dumps(item["schema"]))
            success = False
        else:
            passed = passed + 1

    print("Passed "+str(passed)+" of "+str(total)+" test cases")

    if success:
        print("All tests passed")

    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aqueti Schema Generator")
    parser.add_argument("-test", action='store_const', dest='test', const="True", help="Run unit test")
    parser.add_argument("-input", action='store', dest="input", help="input file for value")

    args = parser.parse_args()

    if args.test:
        print("Testing")
        test()


    if args.input:
        #Load file into memory
        with open( args.input ) as json_file:
                value = json.load(json_file)

        result = generateSchema(value)

        print(json.dumps(result, indent=4))



