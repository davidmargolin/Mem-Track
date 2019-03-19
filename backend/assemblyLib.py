from vartable import *

REG1 = "eax"
REG2 = "ebx"

class MethodGenerator:
    def __init__(self, source):
        self.varCount = 0 #for variable table
        self.labelCount = 0 #for loop labelling
        self.varTable = VarTable()
        self.assemblyInstructions = []
        self.returnType = source["returnType"]

        #get function name and head instruction line with it
        self.methodName = source["functionName"]
        self.assemblyInstructions.append(self.methodName + "(" + source["parameter"]["type"] + "):")

        #read parameters
        self.parameterRead(source["parameter"])

        #read instructions
        self.instructionRead(source["instruction"])


    #fills variable table with parameters
    def parameterRead(self, source):
        self.varTable.addVar(source["name"], source["type"], source["address"], self.genVarCount())
        self.assemblyInstructions.append("push rbp")
        self.assemblyInstructions.append("mov rbp, rsp")
        self.assemblyInstructions.append("mov DWORD PTR [rbp" + str(source["address"]) + "], edi")

    #reads the "instruction" portion of source code
    def instructionRead(self, source):
        for item in source:
            codeType = item["codeType"]
            if codeType == "declaration":
                tmpCode = self.genDeclaration(item)
            elif codeType == "if":
                tmpCode = self.genCondition(item)
            elif codeType == "for":
                tmpCode = self.genForLoop(item)
            elif codeType == "logicOperation":
                tmpCode = self.genLogical(item)
            else:
                tmpCode = self.genReturn(item)
            for x in tmpCode:
                self.assemblyInstructions.append(x)

        #pop
        self.assemblyInstructions.append("pop rbp")
        self.assemblyInstructions.append("ret")
        return

#####Code Generation

    #return a list of assembly instructions for variable declaration/assignment
    def genDeclaration(self, source):
        self.varTable.addVar(source["dataName"], source["dataType"], source["address"], self.genVarCount())

        if source["dataType"] == "int":
            comment = "   # int " + source["dataName"] + "=" + source["dataValue"]
            if source["dataValue"].isdigit():
                return ["mov DWORD PTR [rbp" + str(source["address"]) + "], " + source["dataValue"] + comment]
            else:
                return ["mov DWORD PTR [rbp" + str(source["address"]) + "], DWORD PTR [rbp" + str(self.varTable.address(source["dataValue"])) + "]" + comment]
        else:
            return ["ERROR: dataType must be int"]

    #helper function for genCondition and genForLoop (they are similar, so avoid repeating code)
    def genConditionOrForLoop(self, flag, source):
        assemblyCode = []
        #generate condition labels
        topLabel = "L" + str(self.genLabelCount())
        bottomLabel = "L" + str(self.genLabelCount())

        if flag == "for":
            initialization = "int " + source["initialization"]["dataName"] + "=" + source["initialization"]["dataValue"] + ";"
            termination = source["termination"] + ";"
            increment = (source["increment"]["destination"] + "=" + source["increment"]["operand1"] +
                         source["increment"]["operator"] + source["increment"]["operand2"])
            og_comment = "   # for(" + initialization + termination + increment + ")"
            #initialize for loop conditional value in memory with value in source
            for x in self.genDeclaration(source["initialization"]):
                assemblyCode.append(x)
        else:
            og_comment = "   # if(" + source["termination"] + ")"

        #add the label name
        assemblyCode.append(topLabel + ":" + og_comment)
        #make comparison
        operators = ["<=", ">=", "<", ">", "==", "!="]
        invalid = False
        curr_op = ""
        op_ctr = 0
        while curr_op == "":
            if op_ctr == len(operators):
                invalid = True
                break
            (operand1, operator, operand2) = source["termination"].partition(operators[op_ctr])
            curr_op = operator
            op_ctr += 1

        if invalid:
            return ["ERROR: invalid conditional statement"]

        comment = "   # " + operand1 + operator + operand2
        if operand1.isdigit():
            if operand2.isdigit(): #both op1 and op2 are numbers
                assemblyCode.append("mov " + REG1 + ", " + operand1)
                assemblyCode.append("mov " + REG2 + ", " + operand2)
                assemblyCode.append("cmp " + REG1 + ", " + REG2 + comment)
            else: #op1 is a number but op2 is a variable
                assemblyCode.append("mov " + REG1 + ", " + operand1)
                assemblyCode.append("cmp " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(operand2)) + "]" + comment)
        else:
            if operand2.isdigit(): #op2 is a number but op1 is a variable
                assemblyCode.append("mov " + REG1 + ", " + operand2)
                assemblyCode.append("cmp DWORD PTR [rbp" + str(self.varTable.address(operand1)) + "], " + REG1 + comment)
            else: #both op1 and op2 are variables
                assemblyCode.append("cmp DWORD PTR [rbp" + str(self.varTable.address(operand1)) + "], DWORD PTR [rbp" + str(self.varTable.address(operand2)) + "]" + comment)

        #jump on opposite condition (e.g. opposite of < is >=, so do jge)
        if operator == "<=":
            assemblyCode.append("jg " + bottomLabel)
        elif operator == ">=":
            assemblyCode.append("jl " + bottomLabel)
        elif operator == "<":
            assemblyCode.append("jge " + bottomLabel)
        elif operator == ">":
            assemblyCode.append("jle " + bottomLabel)
        elif operator == "==":
            assemblyCode.append("jne " + bottomLabel)
        elif operator == "!=":
            assemblyCode.append("je " + bottomLabel)

        #body
        for item in source["statement"]:
            codeType = item["codeType"]
            if codeType == "declaration":
                tmpCode = self.genDeclaration(item)
            elif codeType == "if":
                tmpCode = self.genCondition(item)
            elif codeType == "for":
                tmpCode = self.genForLoop(item)
            elif codeType == "logicOperation":
                tmpCode = self.genLogical(item)
            else:
                tmpCode = self.genReturn(item)
            for x in tmpCode:
                assemblyCode.append(x)

        if flag == "for":
            #incrememnt conditional variable
            tmpCode = self.genLogical(source["increment"])
            for x in tmpCode:
                assemblyCode.append(x)

            assemblyCode.append("jmp " + topLabel)

        comment = "   # end of " + topLabel + ":" + og_comment.split("#")[1]
        assemblyCode.append(bottomLabel + ":" + comment)
        return assemblyCode


    #recursive function that will return a list of assembly instructions for the if statement
    def genCondition(self, source):
        assemblyCode = self.genConditionOrForLoop("if", source)
        return assemblyCode

    #recursive function that will return a list of assembly instructions for the for loop
    def genForLoop(self, source):
        assemblyCode = self.genConditionOrForLoop("for", source)
        return assemblyCode

    #return a list of assembly instructions for logical operations (add, subtract, multiply, divide)
    def genLogical(self, source):
        assemblyCode = []

        try:
            op1 = int(source["operand1"])
        except:
            op1 = source["operand1"]

        try:
            op2 = int(source["operand2"])
        except:
            op2 = source["operand2"]

        # first load operand 1
        comment = "   # " + REG1 + " holds " + str(op1)
        if type(op1) == int:
            assemblyCode.append("mov " + REG1 + ", " + str(op1) + comment)
        else:
            assemblyCode.append("mov " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(op1)) + "]" + comment)

        #find operator
        operator = source["operator"]
        if operator == "+":
            command = "add "
        elif operator == "-":
            command = "sub "
        elif operator == "*":
            command = "mul "
        elif operator == "/":
            command = "div "

        # now load operand 2
        comment = "   # " + REG2 + " holds " + str(op2)
        if type(op2) == int:
            assemblyCode.append("mov " + REG2 + ", " + str(op2) + comment)
        else:
            assemblyCode.append("mov " + REG2 + ", DWORD PTR [rbp" + str(self.varTable.address(op2)) + "]" + comment)

        #store op1 <operation> op2 into REG1
        comment = "   # " + REG1 + " holds " + str(op1) + operator + str(op2)
        assemblyCode.append(command + REG1 + ", " + REG2 + comment)
        #move result to destination
        comment = "   # " + source["destination"] + "=" + str(op1) + operator + str(op2)
        assemblyCode.append("mov " + "DWORD PTR [rbp" + str(self.varTable.address(source["destination"])) + "], " + REG1 + comment)
        return assemblyCode


    #return a list of assembly instructions for the return statement
    def genReturn(self, source):
        returnName = source["dataName"]
        comment = "   # return " + returnName
        if returnName.isdigit():
            return ["mov " + REG1 + ", " + returnName + comment]
        else:
            return ["mov " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(returnName)) + "]" + comment]

#####Utility

    #return the list of assembly instructions
    def getObject(self):
        return self.assemblyInstructions

    #return variable count and then increment
    def genVarCount(self):
        tmp = self.varCount
        self.varCount+=1
        return tmp

    #return label count and then increment
    def genLabelCount(self):
        tmp = self.labelCount
        self.labelCount+=1
        return tmp
