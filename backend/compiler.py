from components import *
class Compiler:
    declaration = 1

    # int total(int num){
    def read_head(self, line):
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
    def read_declaration(self, line):
        words = ['', '', '']
        i = 0
        for char in line:
            if char != ' ' and char != '=' and char != ';':
                words[i] = words[i] + str(char)
            else:
                i = i + 1

        self.declaration = self.declaration + 1
        obj = Declaration(words[0], words[1], words[2], -(self.declaration*4))
        return obj.get_object()


    # sum=sum+num;
    def read_logic(self, line):
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
    def read_condition(self, i, segment):
        line = segment[i]
        termination = line[3:-2]
        i = i + 1
        result = self.read_instruction(i, segment)
        statement = result['statement']
        obj = Condition(termination, statement)
        return {'i': result['i'], 'if': obj.get_object()}


    # for(int i=0;i<num;i=i+1){
    def read_for_loop(self, i, segment):
        line = segment[i]
        header = line[4:-2].split(';')
        initialization = self.read_declaration(header[0]+';')
        termination = header[1]
        increment = self.read_logic(header[2]+';')
        i = i + 1
        result = self.read_instruction(i, segment)
        statement = result['statement']
        obj = ForLoop(initialization, termination, increment, statement)
        return {'i': result['i'], 'for': obj.get_object()}


    # return sum;
    def read_return_line(self, line):
        obj = ReturnLine(line)
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
            else:
                instruction.append(self.read_logic(line))
                i = i + 1
        return {'i': i+1, 'statement': instruction}
