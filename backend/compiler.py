import re
from components import *

class CompilerException(Exception):
    pass

class Compiler:
    reserved_keywords = ['asm', 'auto', 'bool', 'break', 'case', 'catch', 'char', 'class', 'const', 'const_cast',
                         'continue', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export',
                         'extern', 'false', 'float', 'for', 'friend', 'goto', 'if', 'inline', 'int', 'long',
                         'mutable', 'namespace', 'new', 'operator', 'private', 'protected', 'public', 'register', 'reinterpret_cast', 'return',
                         'short', 'signed', 'sizeof', 'static', 'static_cast', 'struct', 'switch', 'template', 'this', 'throw',
                         'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void',
                         'volatile', 'wchar_t', 'while']

    int_pattern = '(0|[1-9][0-9]*)'
    identifier_pattern = '[a-zA-Z_][a-zA-Z0-9_]*'
    expression_pattern = '(' + int_pattern + '|' + identifier_pattern + ')([+\-*/](' + int_pattern + '|' + identifier_pattern + '))?'

    # IMPORTANT: anchor these ('^' at start and '$' at end) to match the entire line
    function_pattern = '^int ' + identifier_pattern + '\((int ' + identifier_pattern + ')?\){$'
    function_call_pattern = '^' + identifier_pattern + '\((' + expression_pattern + ')?\);$'
    declaration_pattern = '^int ' + identifier_pattern + '(=' + expression_pattern + ')?;$'
    logic_pattern = '^' + identifier_pattern + '=' + expression_pattern + ';$'
    condition_pattern = '^if\(' + expression_pattern + '([<>]=?|(==|!=))' + expression_pattern + '\){$'
    for_loop_pattern = ('^for\(' + declaration_pattern[1:-1] + condition_pattern[5:-4] + ';(' + logic_pattern[1:-2] +
                        '|(' + identifier_pattern + '(\+\+|--)|(\+\+|--)' + identifier_pattern + '))\){$')
    return_pattern = '^return ' + expression_pattern + ';$'

    def __init__(self):
        self.identifiers = []
        self.declaration = 0

    # returns True if x is a valid C++ identifier, else returns False
    def valid_identifier(self, x):
        if re.match(self.identifier_pattern, x) and x not in self.reserved_keywords:
            return True
        else:
            return False

    # adds x to identifiers if it is valid and doesn't already exist, else raises a CompilerException
    # x is a tuple of the form (a, b[, c]) where a is the name, b is the type (either 'variable' or 'function'),
    # and c exists only when b == 'function', where c is the number of function parameters (either 0 or 1)
    def add_identifier(self, x):
        identifier = x[0]
        if self.valid_identifier(identifier):
            for element in self.identifiers:
                if element[0] == identifier:
                    raise CompilerException('existing identifier')

            self.identifiers.append(x)
        else:
            raise CompilerException('invalid identifier')

    # int total(int num){
    def read_head(self, line):
        if not re.match(self.function_pattern, line):
            raise CompilerException('invalid function syntax')
        words = ['', '', '', '']
        i = 0
        for char in line:
            if char != ' ' and char != '(' and char != ')':
                words[i] = words[i] + str(char)
            else:
                i = i + 1
                if char == ')':
                    break

        if words[2] == '' and words[3] == '': # empty parameter
            self.add_identifier((words[1], 'function', 0))
            return words
        self.add_identifier((words[1], 'function', 1))
        self.add_identifier((words[3], 'variable'))
        return words


    # total(x);
    def read_call(self, line):
        if not re.match(self.function_call_pattern, line):
            raise CompilerException('invalid function call syntax')
        words = ['', '']
        i = 0
        for char in line:
            if char != '(' and char != ')':
                words[i] = words[i] + str(char)
            else:
                i = i + 1
                if char == ')':
                    break

        name = words[0]
        num_args = 1 if words[1] else 0
        for element in self.identifiers:
            if element[0] == name:
                if element[1] != 'function':
                    raise CompilerException(name + ' is not a function')
                elif element[2] != num_args:
                    raise CompilerException(name + ' requires ' + str(element[2]) +
                                            (' argument' if element[2] == 1 else ' arguments'))
                else:
                    obj = FunctionCall(name, words[1])
                    return obj.get_object()
        raise CompilerException('function ' + name + ' not found')


    # int sum=0;
    def read_declaration(self, line):
        if not re.match(self.declaration_pattern, line):
            raise CompilerException('invalid declaration syntax')
        words = ['', '', '']
        i = 0
        for char in line:
            if char != ' ' and char != '=' and char != ';':
                words[i] = words[i] + str(char)
            else:
                i = i + 1

        self.add_identifier((words[1], 'variable'))
        if words[2] == '': words[2] = '0' # 'int x;' becomes 'int x=0;'
        self.declaration = self.declaration + 1
        obj = Declaration(words[0], words[1], words[2], -(self.declaration*4))
        return obj.get_object()


    # sum=sum+num;
    def read_logic(self, line):
        if not re.match(self.logic_pattern, line):
            raise CompilerException('invalid logic syntax')
        operators = ['+', '-', '*', '/']
        words = ['', '', '','']
        i = 0
        for char in line:
            if char in operators:
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
    def read_condition(self, i, segment):
        line = segment[i]
        if not re.match(self.condition_pattern, line):
            raise CompilerException('invalid condition syntax')
        termination = line[3:-2]
        i = i + 1
        result = self.read_instruction(i, segment)
        statement = result['statement']
        obj = Condition(termination, statement)
        return {'i': result['i'], 'if': obj.get_object()}


    # for(int i=0;i<num;i=i+1){
    def read_for_loop(self, i, segment):
        line = segment[i]
        if not re.match(self.for_loop_pattern, line):
            raise CompilerException('invalid for loop syntax')
        header = line[4:-2].split(';')
        initialization = self.read_declaration(header[0]+';')
        termination = header[1]

        if '++' in header[2]:
            var = header[2].replace('++', '')
            header[2] = var + '=' + var + '+1'
        elif '--' in header[2]:
            var = header[2].replace('--', '')
            header[2] = var + '=' + var + '-1'

        increment = self.read_logic(header[2]+';')
        i = i + 1
        result = self.read_instruction(i, segment)
        statement = result['statement']
        obj = ForLoop(initialization, termination, increment, statement)
        return {'i': result['i'], 'for': obj.get_object()}


    # return sum;
    def read_return_line(self, line):
        if not re.match(self.return_pattern, line):
            raise CompilerException('invalid return syntax')
        data_name = line.split('return ')[1][:-1]
        obj = ReturnLine(data_name)
        return obj.get_object()


    # read instructions recursively
    def read_instruction(self, i, segment):
        instruction = []
        while i < len(segment):
            line = segment[i]
            if line == '}':
                break
            if line.startswith('int'):
                instruction.append(self.read_declaration(line))
                i = i + 1
            elif line.startswith('if'):
                result = self.read_condition(i, segment)
                instruction.append(result['if'])
                i = result['i']
            elif line.startswith('for'):
                result = self.read_for_loop(i, segment)
                instruction.append(result['for'])
                i = result['i']
            elif line.startswith('return'):
                instruction.append(self.read_return_line(line))
                i = i + 1
            elif '(' in line:
                instruction.append(self.read_call(line))
                i = i + 1
            else:
                instruction.append(self.read_logic(line))
                i = i + 1
        return {'i': i+1, 'statement': instruction}
