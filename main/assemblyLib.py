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
        self.methodName = str(source["functionName"])
        self.assemblyInstructions.append(self.methodName + ":")

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
            if item["codeType"] == "declaration":
                tmpCode = self.genDeclaration(item)
            elif item["codeType"] == "if":
                tmpCode = self.genCondition(item)
            elif item["codeType"] == "for":
                tmpCode = self.genForLoop(item)
            elif item["codeType"] == "logicOperation":
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

        if source["dataValue"] == None:
            return
        else:
            if source["dataType"] == "int":
                return ["mov DWORD PTR [rbp" + str(source["address"]) + "], " + str(source["dataValue"])]

    #helper function for genCondition and genForLoop (they are similar, so avoid repeating code)
    def genConditionOrForLoop(self, flag, source):
        assemblyCode = []
        #generate condition labels
        topLabel = "L" + str(self.genLabelCount())
        bottomLabel = "L" + str(self.genLabelCount())

        #only do this for the for loop, not for the if statement
        if flag == "for":
            #add index to varTable (does not test if index exists)
            self.varTable.addVar(source["initialization"]["dataName"], source["initialization"]["dataType"], source["initialization"]["address"], self.genVarCount())
            #first initialize for loop conditional value in memory with value in source
            for x in self.genDeclaration(source["initialization"]):
                assemblyCode.append(x)

        #add the label name
        assemblyCode.append(topLabel + ":")
        #make comparison
        operators = ["<=", ">=", "<", ">", "==", "!="]
        curr_op = ""
        op_ctr = 0
        while curr_op == "":
            (operand1, operator, operand2) = source["termination"].partition(operators[op_ctr])
            curr_op = operator
            op_ctr += 1

        assemblyCode.append("cmp DWORD PTR [rbp" + str(self.varTable.address(operand1)) + "], DWORD PTR [rbp" + str(self.varTable.address(operand2)) + "]")
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

        #Body
        for x in source["statement"]:
            if x["codeType"] == "logicOperation":
                tmpCode = self.genLogical(x)
            elif x["codeType"] == "if":
                tmpCode = self.genCondition(x)
            elif x["codeType"] == "for":
                tmpCode = self.genForLoop(x)
            elif x["codeType"] == "declaration":
                tmpCode = self.genDeclaration(x["dataType"], x["address"], x["dataValue"])
            for x in tmpCode:
                assemblyCode.append(x)

        if flag == "for":
            #incrememnt conditional variable
            tmpCode = self.genLogical(source["increment"])
            for x in tmpCode:
                assemblyCode.append(x)

            assemblyCode.append("jmp " + topLabel)

        assemblyCode.append(bottomLabel + ":")
        return assemblyCode


    #recursive function that will return a list of assembly instructions for the if statement
    def genCondition(self, source):
        assemblyCode = self.genConditionOrForLoop("if", source)
        return assemblyCode

    #recursive function that will return a list of assembly instructions for the for loop
    def genForLoop(self, source):
        assemblyCode = self.genConditionOrForLoop("for", source)
        return assemblyCode

    def genLogical(self, source):
        code = []

        try:
            op1 = int(source["operand1"])
        except:
            op1 = source["operand1"]

        try:
            op2 = int(source["operand2"])
        except:
            op2 = source["operand2"]

        # first load operand 1
        if type(op1) == int:
            code.append("mov " + REG1 + ", 0")
            code.append("add " + REG1 + ", " + str(op1))
        else:
            code.append("mov " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(op1)) + "]")

        #find operator
        if source["operator"] == "+":
            command = "add "
        elif source["operator"] == "-":
            command = "sub "
        elif source["operator"] == "*":
            command = "mul "
        elif source["operator"] == "/":
            command = "div "

        # now load operand 2
        if type(op2) == int:
            code.append("mov " + REG2 + ", 0")
            code.append("add " + REG2 + ", " + str(op2))
        else:
            code.append("mov " + REG2 + ", DWORD PTR [rbp" + str(self.varTable.address(op2)) + "]")

        #store operand1 <operation> operand2 into REG1
        code.append(command + REG1 + ", " + REG2)
        #move result to destination
        code.append("mov " + "DWORD PTR [rbp" + str(self.varTable.address(source["destination"]))+ "], " + REG1)
        return code

    def genReturn(self, source):
        returnName = source['return'].split("return ")[1][:-1]
        if returnName.isdigit():
            return ["mov " + REG1 + ", " + returnName]
        else:
            return ["mov " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(returnName)) + "]"]


#####Utility

    #return the list of assembly instructions
    def getObject(self):
        return self.assemblyInstructions

    #return variable count and then increment
    def genVarCount(self):
        tmp = self.varCount
        self.varCount+=1
        return tmp

    def genLabelCount(self):
        tmp = self.labelCount
        self.labelCount+=1
        return tmp
