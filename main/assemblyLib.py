from vartable import *

DEF_REG = "eax"
DEF_PARAM_REG = "edi"

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
        self.assemblyInstructions.append("mov rbp rsp")
        self.assemblyInstructions.append("mov QWORD PTR [rbp" + str(source["address"]) + "], edi")

    #reads the "instruction" portion of source code
    def instructionRead(self, source):
        for item in source:
            if item["codeType"] == "declaration":
                tmpCode = self.genDeclaration(item)
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

#######Code Generation

    #return a list of assembly instructions for variable declaration/assignment
    def genDeclaration(self, source):
        self.varTable.addVar(source["dataName"], source["dataType"], source["address"], self.varCount)

        if source["dataValue"] == None:
            return
        else:
            if source["dataType"] == "int":
                return ["mov QWORD PTR [rbp" + str(source["address"]) + "], " + str(source["dataValue"])]

    #recursive function that will return a list of assembly instructions
    def genForLoop(self, source):
        assemblyCode = []
        #generate loop labels
        topLabel = "L" + str(self.genLabelCount())
        bottomLabel = "L" + str(self.genLabelCount())

        #add index to varTable (does not test if index exists)
        self.varTable.addVar(source["initialization"]["dataName"], source["initialization"]["dataType"], source["initialization"]["address"], self.genVarCount())

        #first initialize for loop conditional value in memory with value in source
        for x in self.genDeclaration(source["initialization"]):
            assemblyCode.append(x)
        #add the Loop name
        assemblyCode.append(topLabel + ":")

        #Looping code section
        #load conditional variable into register
        assemblyCode.append("mov " + DEF_REG + " QWORD PTR [rbp" + str(source["initialization"]["address"]) + "]")

        #make comparison (admittedly hard coded for example source code, need to be able to read termination string)
        assemblyCode.append("cmp " + DEF_REG + ", QWORD PTR [rbp" + str(self.varTable.address("num")) + "]")
        assemblyCode.append("jge " + bottomLabel)

        #Body
        for x in source["statement"]:
            if x["codeType"] == "logicOperation":
                tmpCode = self.genLogical(x)
            elif x["codeType"] == "for":
                tmpCode = self.genForLoop(x)
            elif x["codeType"] == "declaration":
                tmpCode = self.genDeclaration(x["dataType"], x["address"], x["dataValue"])

            for x in tmpCode:
                assemblyCode.append(x)

        #incrememnt conditional variable
        tmpCode = self.genLogical(source["increment"])
        for x in tmpCode:
            assemblyCode.append(x)
        assemblyCode.append("jmp " + topLabel)
        assemblyCode.append(bottomLabel + ":")

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
            code.append("add " + DEF_REG + ", " + str(op1))
        else:
            code.append("mov " + DEF_REG + ", QWORD PTR [rbp" + str(self.varTable.address(op1)) + "]")

        #find operator and generate assembly to add op2 (by address) to op1 (in register)
        if source["operator"] == "+":
            # Add the second operand to the register containing operand1
            if type(op2) == int:
                code.append("add " + DEF_REG + ", " + str(op2))
            else:
                code.append("add " + DEF_REG + ", QWORD PTR [rbp" + str(self.varTable.address(op2))+ "]")
            #move result to destination
            code.append("mov " + "QWORD PTR [rbp" + str(self.varTable.address(source["destination"]))+ "], " + DEF_REG)

        return code

    def genReturn(self, source):
        #again, hard coded
        return ["mov " + DEF_REG + ", QWORD PTR [rbp" + str(self.varTable.address("sum")) + "]"]


####utility
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
