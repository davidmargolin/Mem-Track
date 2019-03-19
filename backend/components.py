class Function:
    def __init__(self, returnType, functionName, parameter, instruction):
        self.returnType_ = returnType
        self.functionName_ = functionName
        self.parameter_ = parameter
        self.instruction_ = instruction

    def get_object(self):
        obj = {
            'returnType': self.returnType_,
            'functionName': self.functionName_,
            'parameter': self.parameter_,
            'instruction': self.instruction_
        }
        return obj


class Declaration:
    def __init__(self, dataType, dataName, dataValue, address):
        self.dataType_ = dataType
        self.dataName_ = dataName
        self.dataValue_ = dataValue
        self.address_ = address

    def get_object(self):
        obj = {
            'dataType': self.dataType_,
            'dataName': self.dataName_,
            'dataValue': self.dataValue_,
            'address': self.address_,
            'codeType': 'declaration'
        }
        return obj


class LogicOperation:
    def __init__(self, destination, operand1, operator, operand2):
        self.destination_ = destination
        self.operand1_ = operand1
        self.operator_ = operator
        self.operand2_ = operand2

    def get_object(self):
        obj = {
            'destination': self.destination_,
            'operand1': self.operand1_,
            'operator': self.operator_,
            'operand2': self.operand2_,
            'codeType': 'logicOperation'
        }
        return obj


class Condition:
    def __init__(self, termination, statement):
        self.termination_ = termination
        self.statement_ = statement

    def get_object(self):
        obj = {
            'termination': self.termination_,
            'statement': self.statement_,
            'codeType': 'if'
        }
        return obj


class ForLoop:
    def __init__(self, initialization, termination, increment, statement):
        self.initialization_ = initialization
        self.termination_ = termination
        self.increment_ = increment
        self.statement_ = statement

    def get_object(self):
        obj = {
            'initialization': self.initialization_,
            'termination': self.termination_,
            'increment': self.increment_,
            'statement': self.statement_,
            'codeType': 'for'
        }
        return obj


class ReturnLine:
    def __init__(self, line):
        self.dataName = line.split('return ')[1][:-1]

    def get_object(self):
        obj = {
            'dataName': self.dataName,
            'codeType': 'return'
        }
        return obj
