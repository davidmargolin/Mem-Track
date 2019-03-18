import json
#from pprint import pprint
from compiler import *
from assemblyLib import *

with open('test.txt') as test_file:
    source = test_file.read().splitlines()

head = read_head(source[0])
returnType = head[0]
functionName = head[1]
parameter = {
    'type': head[2],
    'name': head[3],
    'address': -(declaration*4),
    'codeType': 'declaration'
}

instruction = read_instruction(1, source)['statement']   # ignore the first line
functionClass = Function(returnType, functionName, parameter, instruction)
obj = functionClass.get_object()

with open('data.json', 'w') as outfile:
    json.dump(obj, outfile)

with open('data.json') as infile:
    data = json.load(infile)
    #pprint(data)

assembly = MethodGenerator(data).getObject()
result = json.dumps(assembly, indent=4)
print(result)
