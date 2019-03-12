import json
from components import *
from assemblyLib import *
from pprint import pprint

declaration = 1

# int total(int num){
def read_head(line):
    words = ['', '', '', '']
    i = 0
    for char in line:
        if char != ' ' and char != '(' and char != ')':
            words[i] = words[i] + str(char)
        else:
            i = i + 1
            if char == ')':
                break
    return words


# int sum=0;
def read_declaration(line):
    global declaration
    words = ['', '', '']
    i = 0
    for char in line:
        if char != ' ' and char != '=' and char != ';':
            words[i] = words[i] + str(char)
        else:
            i = i + 1
    declaration = declaration + 1
    obj = Declaration(words[0], words[1], words[2], -(declaration*4))
    return obj.get_object()


# sum=sum+num;
def read_logic(line):
    words = ['', '', '','']
    i = 0
    for char in line:
        if char == '+' or char == '-' or char == '*' or char == '/':
            i = i + 1
            words[i] = str(char)
            i = i + 1
        elif char != '=' and char != ';':
            words[i] = words[i] + str(char)
        else:
            i = i + 1
    obj = LogicOperation(words[0], words[1], words[2], words[3])
    return obj.get_object()


# for(int i=0;i<num;i=i+1){
def read_for_loop(i, segment):
    line = segment[i]
    header = line[4:-2].split(';')
    initialization = read_declaration(header[0]+';')
    termination = header[1]
    increment = read_logic(header[2]+';')
    i = i + 1
    result = read_instruction(i, segment)
    statement = result['statement']
    obj = ForLoop(initialization, termination, increment, statement)
    return {'i': result['i'], 'for': obj.get_object()}


# read instructions recursively
def read_instruction(i, segment):
    instruction = []
    while i < len(segment):
        line = segment[i]
        if line == '}':
            break
        if line.startswith('int'):
            instruction.append(read_declaration(line))
            i = i + 1
        elif line.startswith('for'):
            result = read_for_loop(i, segment)
            instruction.append(result['for'])
            i = result['i']
        elif line.startswith('return'):
            instruction.append(line)
            i = i + 1
        else:
            instruction.append(read_logic(line))
            i = i + 1
    return {'i': i+1, 'statement': instruction}


source = [
    'int total(int num){',
    'int sum=0;',
    'for(int i=0;i<num;i=i+1){',
    'sum=sum+a;',
    '}',
    'return sum;',
    '}'
]
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
result = json.dumps(obj, indent=4)

with open('data.json', 'w') as outfile:
    json.dump(obj, outfile)
#######################################################################################################################
with open('data.json') as infile:
    data = json.load(infile)

assembly = MethodGenerator(data)


