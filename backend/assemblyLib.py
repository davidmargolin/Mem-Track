from vartable import *

REG1 = "eax"
REG2 = "ebx"
PARAM_REG1 = "edi"

INDENT = "~~"

class MethodGenerator:
    def __init__(self, source):
        self.varCount = 0 #for variable table
        self.labelCount = 0 #for loop labelling
        self.varTable = VarTable()
        self.assemblyInstructions = []
        self.returnType = source["returnType"]
        self.methodName = source["functionName"]
        self.returnLabel = "EXIT_" + self.methodName + ":"

        #put function name and parameter label
        self.assemblyInstructions.append(self.methodName + "(" + source["parameter"]["type"] + "):")
        #read parameters
        self.parameterRead(source["parameter"])
        #read instructions
        self.instructionRead(source["instruction"])


    #puts function prologue and fills variable table with parameters
    def parameterRead(self, source):
        self.assemblyInstructions.append("push rbp")
        self.assemblyInstructions.append("mov rbp, rsp")
        if source["name"] and source["type"]:
            self.varTable.addVar(source["name"], source["type"], source["address"], self.genVarCount())
            self.assemblyInstructions.append("mov DWORD PTR [rbp" + str(source["address"]) + "], " + PARAM_REG1)

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
            elif codeType == "functionCall":
                tmpCode = self.genFunctionCall(item)
            else:
                tmpCode = self.genReturn(item)
            for x in tmpCode:
                self.assemblyInstructions.append(x)

        #function cleanup
        if "jmp " + self.returnLabel in self.assemblyInstructions[-1]: #genReturn does this sometimes
            del self.assemblyInstructions[-1]

        self.assemblyInstructions.append(self.returnLabel)
        self.assemblyInstructions.append("pop rbp")
        self.assemblyInstructions.append("ret")
        self.assemblyInstructions.append("") #acts as new line
        return

#####Code Generation

    #returns a list of assembly instructions for logical operations (add, subtract, multiply, divide) and assignment w/o declaration (e.g. "x=1;")
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

        if not op2: #"x=1;" -> source["destination"] = "x" and op1 = "1", while others are empty
            comment = " # " + source["destination"] + "=" + str(op1)
            if type(op1) == int:
                assemblyCode.append("mov DWORD PTR [rbp" + str(self.varTable.address(source["destination"])) + "], " + str(op1) + comment)
            else:
                assemblyCode.append("mov DWORD PTR [rbp" + str(self.varTable.address(source["destination"])) + "], DWORD PTR [rbp" +
                                    str(self.varTable.address(op1)) + "]" + comment)
            return assemblyCode

        #first load operand 1
        comment = " # " + REG1 + " holds " + str(op1)
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

        #store op1 <operation> op2 into REG1
        comment = " # " + REG1 + " holds " + str(op1) + operator + str(op2)
        if type(op2) == int:
            assemblyCode.append(command + REG1 + ", " + str(op2) + comment)
        else:
            assemblyCode.append(command + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(op2)) + "]" + comment)

        #move result to destination
        if source["destination"]:
            comment = " # " + source["destination"] + "=" + str(op1) + operator + str(op2)
            assemblyCode.append("mov DWORD PTR [rbp" + str(self.varTable.address(source["destination"])) + "], " + REG1 + comment)
        return assemblyCode


    #tests an expression for a logical statement (e.g. "return x;" testing "x" fails, but "return x+y;" testing "x+y" succeeds); if successful, returns a list
    #of assembly instructions that stores the result of the expression in REG1 (in this case, the value of x+y will be stored in REG1), else returns []
    def genLogicalExpression(self, expression):
        for op in ["+", "-", "*", "/"]:
            if op in expression: #e.g. "return x+y;" -> expression is "x+y" here
                (op1, op, op2) = expression.partition(op)
                assemblyCode = self.genLogical({"destination": "", "operand1": op1, "operator": op, "operand2": op2})
                return assemblyCode
        return []

    #returns a list of assembly instructions for variable declaration/assignment (both "int x;" and "int x=1;" work)
    def genDeclaration(self, source):
        self.varTable.addVar(source["dataName"], source["dataType"], source["address"], self.genVarCount())

        dataValue = source["dataValue"]
        assemblyCode = self.genLogicalExpression(dataValue)
        comment = " # int " + source["dataName"] + "=" + dataValue
        if assemblyCode:
            assemblyCode.append("mov DWORD PTR [rbp" + str(source["address"]) + "], " + REG1 + comment)
            return assemblyCode

        if dataValue.isdigit():
            return ["mov DWORD PTR [rbp" + str(source["address"]) + "], " + dataValue + comment]
        else:
            return ["mov DWORD PTR [rbp" + str(source["address"]) + "], DWORD PTR [rbp" + str(self.varTable.address(dataValue)) + "]" + comment]

    #helper function for genCondition and genForLoop (they are similar, so avoid repeating code)
    def genConditionOrForLoop(self, flag, source):
        assemblyCode = []
        #generate condition labels
        topLabel = "L" + str(self.genLabelCount())
        bottomLabel = "L" + str(self.genLabelCount())

        if flag == "for":
            initialization = "int " + source["initialization"]["dataName"] + "=" + source["initialization"]["dataValue"] + "; "
            termination = source["termination"] + "; "
            increment = (source["increment"]["destination"] + "=" + source["increment"]["operand1"] +
                         source["increment"]["operator"] + source["increment"]["operand2"])
            og_comment = " # for(" + initialization + termination + increment + ")"
            #for loop initialization is a declaration
            for x in self.genDeclaration(source["initialization"]):
                assemblyCode.append(INDENT + x)
        else:
            og_comment = " # if(" + source["termination"] + ")"

        #add the label name
        assemblyCode.append(INDENT + topLabel + ":" + og_comment)
        #parse condition
        for op in ["<=", ">=", "<", ">", "==", "!="]:
            if op in source["termination"]:
                (operand1, operator, operand2) = source["termination"].partition(op)
                break

        exp1 = self.genLogicalExpression(operand1)
        exp2 = self.genLogicalExpression(operand2)
        comment = " # " + operand1 + operator + operand2

        if exp1:
            if exp2:
                #exp1 is stored in REG1 and exp2 is also stored in REG1
                #since both are in REG1, move one of them to REG2
                exp1.append("mov " + REG2 + ", " + REG1)
                for x in exp1: assemblyCode.append(INDENT + x) #exp1 stored in REG2
                for x in exp2: assemblyCode.append(INDENT + x) #exp2 stored in REG1
                assemblyCode.append(INDENT + "cmp " + REG2 + ", " + REG1 + comment)
            elif operand2.isdigit():
                for x in exp1: assemblyCode.append(INDENT + x) #exp1 stored in REG1
                assemblyCode.append(INDENT + "cmp " + REG1 + ", " + operand2 + comment)
            else: #operand2 is a variable
                for x in exp1: assemblyCode.append(INDENT + x) #exp1 stored in REG1
                assemblyCode.append(INDENT + "cmp " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(operand2)) + "]" + comment)
        elif operand1.isdigit():
            if exp2:
                for x in exp2: assemblyCode.append(INDENT + x) #exp2 stored in REG1
                assemblyCode.append(INDENT + "cmp " + operand1 + ", " + REG1 + comment)
            elif operand2.isdigit():
                assemblyCode.append(INDENT + "cmp " + operand1 + ", " + operand2 + comment)
            else: #operand2 is a variable
                assemblyCode.append(INDENT + "cmp " + operand1 + ", DWORD PTR [rbp" + str(self.varTable.address(operand2)) + "]" + comment)
        else: #operand1 is a variable
            if exp2:
                for x in exp2: assemblyCode.append(INDENT + x) #exp2 stored in REG1
                assemblyCode.append(INDENT + "cmp DWORD PTR [rbp" + str(self.varTable.address(operand1)) + "], " + REG1 + comment)
            elif operand2.isdigit():
                assemblyCode.append(INDENT + "cmp DWORD PTR [rbp" + str(self.varTable.address(operand1)) + "], " + operand2 + comment)
            else: #operand2 is a variable
                assemblyCode.append(INDENT + "cmp DWORD PTR [rbp" + str(self.varTable.address(operand1)) + "], DWORD PTR [rbp" +
                                    str(self.varTable.address(operand2)) + "]" + comment)

        #jump on opposite condition (e.g. opposite of < is >=, so do jge)
        if operator == "<=":
            assemblyCode.append(INDENT + "jg " + bottomLabel)
        elif operator == ">=":
            assemblyCode.append(INDENT + "jl " + bottomLabel)
        elif operator == "<":
            assemblyCode.append(INDENT + "jge " + bottomLabel)
        elif operator == ">":
            assemblyCode.append(INDENT + "jle " + bottomLabel)
        elif operator == "==":
            assemblyCode.append(INDENT + "jne " + bottomLabel)
        elif operator == "!=":
            assemblyCode.append(INDENT + "je " + bottomLabel)

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
            elif codeType == "functionCall":
                tmpCode = self.genFunctionCall(item)
            else:
                tmpCode = self.genReturn(item)
            for x in tmpCode:
                assemblyCode.append(INDENT + x)

        if flag == "for":
            #for loop increment is a logical operation
            tmpCode = self.genLogical(source["increment"])
            for x in tmpCode:
                assemblyCode.append(INDENT + x)

            assemblyCode.append(INDENT + "jmp " + topLabel)

        comment = " # end of " + topLabel + ":" + og_comment.split("#")[1]
        assemblyCode.append(INDENT + bottomLabel + ":" + comment)
        return assemblyCode


    #returns a list of assembly instructions for the if statement
    def genCondition(self, source):
        assemblyCode = self.genConditionOrForLoop("if", source)
        return assemblyCode

    #returns a list of assembly instructions for the for loop
    def genForLoop(self, source):
        assemblyCode = self.genConditionOrForLoop("for", source)
        return assemblyCode

    #returns a list of assembly instructions for the function call
    def genFunctionCall(self, source):
        name = source["functionName"]
        argument = source["argument"]
        #see if argument is a logical operation (e.g. "sum(x+y);" where argument is "x+y")
        assemblyCode = self.genLogicalExpression(argument)
        if not argument:
            pass
        elif assemblyCode:
            assemblyCode.append("mov " + PARAM_REG1 + ", " + REG1)
        elif argument.isdigit():
            assemblyCode.append("mov " + PARAM_REG1 + ", " + argument)
        else:
            assemblyCode.append("mov " + PARAM_REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(argument)) + "]")

        if argument:
            comment = " # " + name + "(" + argument + ")"
            assemblyCode.append("call " + name + "(int)" + comment)
        else:
            assemblyCode.append("call " + name + "()")
        return assemblyCode

    #returns a list of assembly instructions for the return statement
    def genReturn(self, source):
        returnName = source["dataName"]
        comment = " # return " + returnName
        jmpCode = "jmp " + self.returnLabel + comment
        #see if returnName is a logical operation (e.g. "return x+y;" where returnName is "x+y")
        assemblyCode = self.genLogicalExpression(returnName)
        if assemblyCode:
            assemblyCode.append(jmpCode)
            return assemblyCode

        if returnName.isdigit():
            return ["mov " + REG1 + ", " + returnName, jmpCode]
        else:
            return ["mov " + REG1 + ", DWORD PTR [rbp" + str(self.varTable.address(returnName)) + "]", jmpCode]

#####Utility

    #return the list of assembly instructions
    def getObject(self):
        return self.assemblyInstructions

    #return the list of dicts containing info about the variables
    def getVarTable(self):
        return self.varTable.getTable()

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
