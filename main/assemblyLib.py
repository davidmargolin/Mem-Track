from vartable import *

DEF_REG = "eax"

class MethodGenerator:
    def __init__(self, source):
        self.varCount = 0 #for variable table
        self.labelCount = 0 #for loop labelling
        self.varTable = VarTable()
        self.assemblyInstructions = []
        self.methodName = source["functionName"]
        self.returnType = source["returnType"]
        self.parameterRead(source["parameter"])
        self.instructionRead(source["instruction"])

    #fills variable table with parameters
    def parameterRead(self, source):
        self.varTable.addVar(source["name"], source["type"], source["address"], self.genVarCount())

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
                return ["mov DWORD PTR [rbp" + str(source["address"]) + "], " + str(source["dataValue"])]

    #recursive function that will return a list of assembly instructions
    def genForLoop(self, source):
        assemblyCode = []
        tmpTable = self.varTable

        #add index to tmpTable (does not test if index exists)
        tmpTable.addVar(source["initialization"]["dataName"], source["initialization"]["dataType"], source["initialization"]["address"], self.genVarCount())

        #first initialize for loop conditional value in memory with value in source
        assemblyCode.append(self.genDeclaration(source["initialization"]))
        #add the Loop name
        topLabel = "L"+ str(self.genLabelCount())
        bottomLabel = "L"+ str(self.genLabelCount())

        assemblyCode.append(topLabel)

        #Looping code section
        #load conditional variable into register
        assemblyCode.append("mov " + DEF_REG + " DWORD PTR [rbp" + str(source["initialization"]["address"]))

        #make comparison (admittedly hard coded for example source code, need to be able to read termination string)
        assemblyCode.append("cmp " + DEF_REG + "DWORD PTR [rbp" + str(self.varTable.address("num")))
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

        return assemblyCode


    def genLogical(self, source):
        code = []
        #first load operand 1
        code.append("mov " + DEF_REG + " DWORD PTR [rbp" + str(self.varTable.address(source["operand1"])) + "]")
        if source["operator"] == "+":
            # Add the second operand to the register containing operand1
            code.append("add " + DEF_REG + " DWORD PTR [rbp" + str(self.varTable.address(source["operand2"]))+ "]")
            #now move to destination
            code.append("mov " + "DWORD PTR [rbp" + str(self.varTable.address(source["destination"]))+ "]" + DEF_REG)

        return code


    def genReturn(self, source):
        #again, hard coded
        return ["move " + DEF_REG + " DWORD PTR [rbp" + str(self.varTable.address("sum")) + "]"]


####utility


    #return variable count and then increment
    def genVarCount(self):
        tmp = self.varCount
        self.varCount+=1
        return tmp

    def genLabelCount(self):
        tmp = self.labelCount
        self.labelCount+=1
        return tmp