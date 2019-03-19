from components import *

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


# if(i<num){
def read_condition(i, segment):
    line = segment[i]
    termination = line[3:-2]
    i = i + 1
    result = read_instruction(i, segment)
    statement = result['statement']
    obj = Condition(termination, statement)
    return {'i': result['i'], 'if': obj.get_object()}


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


# return sum;
def read_return_line(line):
    obj = ReturnLine(line)
    return obj.get_object()


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
        elif line.startswith('if'):
            result = read_condition(i, segment)
            instruction.append(result['if'])
            i = result['i']
        elif line.startswith('for'):
            result = read_for_loop(i, segment)
            instruction.append(result['for'])
            i = result['i']
        elif line.startswith('return'):
            instruction.append(read_return_line(line))
            i = i + 1
        else:
            instruction.append(read_logic(line))
            i = i + 1
    return {'i': i+1, 'statement': instruction}
