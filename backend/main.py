import copy
from compiler import *
from machineLib import *
from assemblyLib import *
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import math

# Sample Input
# ["00000000000000000000000000000000",
# "10100000000000000000000000010000",
# "10100000000001000000000001000011",
# "10100000000010000000000000000101",
# "10100000000011000000000000000101",
# "10110000000011000000000001000100",
# "01100000000111000000000000000000",
# "10100000000000100000000010000001",
# "11000000000000100000000001010010",
# "10100000000010000000000000100011",
# "10100000000000100000000011000001",
# "11000000000000100000000000010010",
# "10100000000011000000000000100011",
# "00110000000110000000000000000000",
# "10100000000000100000000010000001",
# "00010000000000000000000000000000",
# "00100000000000000000000000000000",
# "00000000000000000000000000000000",
# "10100000000000000000000000010000",
# "10100000000001000000000001010010",
# "10100000000100000000000000100011",
# "10100000000000100000000100000001",
# "00010000000000000000000000000000",
# "00100000000000000000000000000000"]

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

## global hit, miss, replace counters
hit = 0
miss = 0
replace = 0

## physical memory grows as big as necessary
class PhysMem:
    entries = ["" for count in xrange(1000)]
    def writeBlock(self, page, offset, block):
        for lineIndex in range(len(block)):
            if (len(self.entries) <= page * 16 * 8 + offset * 8 + lineIndex):
                self.entries.append(block[lineIndex])
            else:
                self.entries[page * 16 * 8 + offset * 8 + lineIndex] = block[lineIndex]
    def getBlock(self, page, offset):
        return self.entries[page*16*8 + offset*8:page*16*8 + offset*8 + 8]


            
physMem = PhysMem()

## ram size is 128bytes (4 pages, 4 blocks)
class RAM:
    blocks = [["","","","","","","",""] for count in xrange(16)]
    def writeBlock(self, page, offset, block):
        self.blocks[page*2 + offset] = list(block)
    def getBlock(self, page, offset):
        return self.blocks[page*2 + offset]
    def prettyPrint(self):
        return '\n'.join(map(lambda x: str(x), self.blocks) )
ram = RAM()


class PageTable:
    entries = []
    ramPages = 2
    def getPhysPage(self, virtualPage):
        print str(virtualPage)
        for entry in self.entries:
            if (entry['index'] == virtualPage):
                return entry['page']

        assignedPage = len(self.entries)
        self.entries.append({'index': virtualPage, 'page': assignedPage })
        return assignedPage

pageTable = PageTable()

class TLB:
    ref = []
    lastIndexEdited = -1

    def __init__(self, tlbEntries):
        self.maxEntries = tlbEntries
    def prettyPrint(self):
        return  '\n'.join(map(lambda x: str(x), self.ref) )
    def load(self, address):
        virtualpage = int(address[0:14], 2)
        index = int(address[14:16], 2)
        for line in self.ref:
            if line['vPage'] == virtualpage:
                print "tlb hit!"
                if (line['physPage'] < 4):
                    return ram.getBlock(line['physPage'] , index)
                else:
                    return physMem.getBlock(line['physPage'] , index)

        print "tlb miss!"
        if (len(self.ref) > self.maxEntries):
            print "tlb replace!"
            if self.lastIndexEdited == self.maxEntries:
                self.lastIndexEdited = 0
            else:
                self.lastIndexEdited += 1
                del self.ref[self.lastIndexEdited]
                self.ref[self.lastIndexEdited] = {'physPage': pageTable.getPhysPage(virtualpage), 'vPage': virtualpage}
                if (self.ref[self.lastIndexEdited]['physPage'] < 4):
                    return ram.getBlock(self.ref[self.lastIndexEdited]['physPage'] , index)
                else:
                    return physMem.getBlock(self.ref[self.lastIndexEdited]['physPage'] , index)

        else:
            self.ref.append({'physPage': pageTable.getPhysPage(virtualpage), 'vPage': virtualpage})
            if (self.ref[len(self.ref) -1]['physPage'] < 4):
                return ram.getBlock(self.ref[len(self.ref) -1 ]['physPage'] , index)
            else:
                return physMem.getBlock(self.ref[len(self.ref) -1 ]['physPage'] , index)

    def save(self, address, data):
        virtualpage = int(address[0:14], 2)
        index = int(address[14:16], 2)
        for line in self.ref:
            if line['vPage'] == virtualpage:
                if (line['physPage'] < 4):
                    ram.writeBlock(line['physPage'] , index, data)
                else:
                    physMem.writeBlock(line['physPage']  , index, data)
                return

        if (len(self.ref) >= self.maxEntries):
            # TODO
            print 'reached max size of the tlb' 
            if self.lastIndexEdited == self.maxEntries:
                self.lastIndexEdited = 0
            else:
                self.lastIndexEdited += 1
                del self.ref[self.lastIndexEdited]
                self.ref[self.lastIndexEdited] = {'physPage': pageTable.getPhysPage(virtualpage), 'vPage': virtualpage}
                if (self.ref[self.lastIndexEdited]['physPage'] < 4):
                    ram.writeBlock(self.ref[self.lastIndexEdited]['physPage'], index, data)
                else:
                    physMem.writeBlock(self.ref[self.lastIndexEdited]['physPage'], index, data)
                return

        else:
            self.ref.append({'physPage': pageTable.getPhysPage(virtualpage), 'vPage': virtualpage})
            if (self.ref[len(self.ref) - 1]['physPage'] < 4):
                ram.writeBlock(self.ref[len(self.ref) - 1]['physPage'], index, data)
            else:
                physMem.writeBlock(self.ref[len(self.ref) - 1]['physPage'], index, data)

tlb = TLB(10)


class Block:
    valid = False
    counter = 0
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data
    def prettyPrint(self):
        return "\ntag: " + self.tag + "\nvalid: " + str(self.valid) + "\ndata: " + '\n' + '\n'.join(map(lambda x: x.replace(" ",""), self.data) )
    def getData(self, index):
        returnData = self.data[int(index, 2)]
        return returnData
    def writeData(self, data, index):
        self.data[int(index, 2)] = str(data)
        self.valid = True
        return
    def loadDataFromVMem(self, tag, offset, index, counter):
        global tlb
        if (self.valid):
            print('cache replace')
            tlb.save(self.tag + self.offset + self.index, list(self.data))
        self.tag = tag
        self.offset = offset
        self.index = index
        self.data = list(tlb.load(tag + offset + index))
        self.counter = counter
        self.valid = True
        return
    def empty(self):
        if (self.valid):
            tlb.save(self.tag + self.offset + self.index, self.data)
            self.valid = False
            self.data = []
            self.tag = ""

class Set:
    counter = 0

    def __init__(self, blocks):
        self.blocks = [Block("", []) for count in xrange(blocks)]

    def prettyPrint(self):
        return '\n' + "Set: " + '\n' + '\n'.join(map(lambda x:x.prettyPrint(), self.blocks))

    def empty(self):
        for block in self.blocks:
            block.empty()

    def getData(self, tag, offset, index):
        # look for hit
        for block in self.blocks:
            print("block")
            if ((block.tag == tag) & block.valid):
                global hit
                print("cache hit")
                hit+=1
                return block.getData(offset)

        # look for miss
        print("cache miss")
        for count in range(0, len(self.blocks)):
            if (not self.blocks[count].valid):
                global miss
                miss += 1
                self.blocks[count].loadDataFromVMem(tag, offset, index, self.counter)
                self.counter += 1
                return self.blocks[count].getData(offset)

        # replace oldestmiss
        oldestBlockIndex = 0
        for count in range(0, len(self.blocks)):
            if (self.blocks[count].counter < self.blocks[oldestBlockIndex].counter):
                oldestBlockIndex = count
        global replace
        miss += 1
        replace += 1
        self.blocks[oldestBlockIndex].loadDataFromVMem(tag,offset,index, self.counter)
        self.counter += 1
        return self.blocks[oldestBlockIndex].getData(offset)

    def writeData(self, data, index, offset, tag):

        # look for hit
        for block in self.blocks:
            if ((block.tag == tag) & block.valid):
                global hit
                print("cache hit")
                hit+=1
                return block.writeData(data, offset)

        # look for miss
        print("cache miss")
        for count in range(0, len(self.blocks)):
            if (not self.blocks[count].valid):
                global miss
                miss += 1
                self.blocks[count].loadDataFromVMem(tag, offset, index, self.counter)
                self.counter += 1
                self.blocks[count].writeData(data, offset)
                return

        # replace oldestmiss
        oldestBlockIndex = 0
        for count in range(0, len(self.blocks)):
            if (self.blocks[count].counter < self.blocks[oldestBlockIndex].counter):
                oldestBlockIndex = count
        global replace
        miss += 1
        replace += 1
        self.blocks[oldestBlockIndex].loadDataFromVMem(tag, offset, index, self.counter)
        self.counter += 1
        self.blocks[oldestBlockIndex].writeData(data, offset)
        return

            



class Cache:
    def __init__(self, wordsPerBlock, setsInCache, L):
        self.sets = [Set(L) for count in xrange(setsInCache)]
        self.offsetSize = math.log(wordsPerBlock, 2.0)
        self.indexSize = math.log(setsInCache, 2.0)
        self.tagSize = 16 - self.offsetSize - self.indexSize

    def load(self, location):
        location = bin(location)[2:]
        if (len(location)<16):
            location = ((16-len(location)) * '0') + location
        tag = location[:0-int(self.indexSize)-int(self.offsetSize)]
        offset = location[0-int(self.offsetSize):]
        index = location[0-int(self.indexSize)-int(self.offsetSize):0-int(self.offsetSize)]
        # print "tag: " + tag 
        # print "index: " + index
        # print "offset: " + offset
        return self.sets[int(index,2)].getData(tag, offset, index)

    def write(self, data, location):
        location = bin(location)[2:]
        if (len(location)<16):
            location = ((16-len(location)) * '0') + location
        tag = location[:0-int(self.indexSize)-int(self.offsetSize)]
        offset = location[0-int(self.offsetSize):]
        index = location[0-int(self.indexSize)-int(self.offsetSize):0-int(self.offsetSize)]
        return self.sets[int(index, 2)].writeData(data, index, offset, tag)

    def empty(self):
        for set in self.sets:
            set.empty()

    def prettyPrint(self):
        return '\n'.join(map(lambda x:x.prettyPrint(), self.sets))

cache = Cache(8, 2, 2)

class CPU:

    def __init__(self, programArray, stackSize, pcStart, labels):
        # write program to memory
        # reset pc

        for index in range(len(programArray)):
            cache.write(programArray[index][0:16], index*2)
            cache.write(programArray[index][16:32], index*2+1)
        cache.empty()
        self.labels = labels
        self.cpuRegister = {
            'rbp': 127,
            'rsp': 127,
            'eax': 0,
            'edi': 5,
            'cmp': 0,
            'pc': pcStart
        }

    def resolveArgument(self, argument):
        if (argument) in self.cpuRegister.keys():
            # it's in a register
            return bin(self.cpuRegister[argument])[2:]
        elif('DWORD' in str(argument)):
            # it's on the stack
            print "looking for stack - " + str(self.cpuRegister['rbp'] - int(argument.split('-')[1][:-1])/2)
            return cache.load(self.cpuRegister['rbp'] - int(argument.split('-')[1][:-1])/2)
        else:
            # it's an integer
            return bin(int(argument))[2:]

    def runLine(self):
        sourceRaw = cache.load(self.cpuRegister['pc']*2) + cache.load(self.cpuRegister['pc']*2+1)
        print "pc: " + str(self.cpuRegister['pc'])
        print "instructon: " + sourceRaw
        action = revCode[sourceRaw[0:4]].upper()
        twoparams = ["ADD", "MOV", "CMP", "DIV", "MUL", "SUB"]
        jump = ["JGE", "JLE", "JMP", "JL", "JG", "JE", "JNE"]
        stack = ["PUSH", "POP"]
        if action in twoparams:
            data = resolveData(sourceRaw[28:32], sourceRaw[4:16], sourceRaw[16:28])
        elif action in jump:
            data = [int(sourceRaw[4:18],2), ""]
        elif action in stack:
            data = [int(sourceRaw[4:18],2), ""]
        else:
            data = ["", ""]
        line = {
            "action": action,
            "r1": data[0],
            "r2": data[1]
        }
        print(line['action'])
        print(line['r1'])
        print(line['r2'])
        if (line['action']=="MOV"):
            print ram.prettyPrint()
            dataToMove = self.resolveArgument(line['r2'])

            if (line['r1']) in self.cpuRegister.keys():
                # it's in a register
                self.cpuRegister[line['r1']] = int(dataToMove, 2)
            else:
                # it's on the stack
                cache.write(((16-len(dataToMove)) * '0') + dataToMove, self.cpuRegister['rbp'] - int(line['r1'].split('-')[1][:-1])/2)

            self.cpuRegister['pc'] += 1

        elif (line['action']=="ADD"):
            a = self.resolveArgument(line['r1'])
            b = self.resolveArgument(line['r2'])
            if (line['r1']) in self.cpuRegister.keys():
                # it's in a register
                self.cpuRegister[line['r1']] = int(a,2)+int(b,2)
            else:
                # it's on the stack
                dataToWrite = bin(int(a,2)+int(b,2))[2:]
                cache.write(((16-len(dataToWrite)) * '0') + dataToWrite, self.cpuRegister['rbp'] - int(line['r1'].split('-')[1][:-1])/2)

            self.cpuRegister['pc'] += 1

        elif (line['action']=="CMP"):
            b = int(self.resolveArgument(line['r1']),2)
            a = int(self.resolveArgument(line['r2']),2)
            self.cpuRegister['cmp'] = a-b
            self.cpuRegister['pc'] += 1

        elif (line['action']=="JGE"):
            if (self.cpuRegister['cmp'] <= 0):
                self.cpuRegister['pc'] = int(self.resolveArgument(line['r1']), 2)/4 - 9
            else:
                self.cpuRegister['pc'] += 1
            # return pc location
        elif (line['action']=="JLE"):
            if (self.cpuRegister['cmp'] >= 0):
                self.cpuRegister['pc'] = int(self.resolveArgument(line['r1']), 2)/4 -12
            else:
                self.cpuRegister['pc'] +=1
            # return pc location

        elif (line['action']=="JMP"):
            self.cpuRegister['pc'] = int(self.resolveArgument(line['r1']), 2)/4 - 14
            # return pc location
        elif (line['action']=='PUSH'):
            self.cpuRegister['pc'] += 1
        else:
            self.cpuRegister['pc'] += 1

        return line['action'] + " " + str(line['r1']) + " " + str(line['r2'])
        #     "cpu registers": self.cpuRegister, 
        # }

 
revCode = {'0110': 'jge', '0111': 'jle', '0000': 'push', '0001': 'pop', '0011': 'jmp', '0010': 'ret', '0101': 'jl', '0100': 'jg', '1111': 'div', '1110': 'mul', '1100': 'add', '1101': 'sub', '1010': 'mov', '1011': 'cmp', '1001': 'je', '1000': 'jne'}
regCode = {
    '000000000000': 'rbp',
    '000000000001': 'rsp',
    '000000000010': 'eax',
    '000000000011': 'ebx',
    '000000000100': 'edi'
}

def resolveData(funcCode, a, b):
    if (funcCode == '0000'):
        return [regCode[a], regCode[b]]
    elif (funcCode == '0001'):
        return [regCode[a], "DWORD PTR [rbp-"+str(int(b, 2))+"]"]
    elif (funcCode == '0010'):
        return [regCode[a], str(int(b, 2))]
    elif (funcCode == '0011'):
        return ["DWORD PTR [rbp-"+str(int(a, 2))+"]", regCode[b]]
    elif (funcCode == '0100'):
        return ["DWORD PTR [rbp-"+str(int(a, 2))+"]", "DWORD PTR [rbp-"+str(int(b, 2))+"]"]
    elif (funcCode == '0101'):
        return ["DWORD PTR [rbp-"+str(int(a, 2))+"]", str(int(b, 2))]
    elif (funcCode == '0110'):
        return [str(int(a, 2)), regCode[b]]
    elif (funcCode == '0111'):
        return [str(int(a, 2)), "DWORD PTR [rbp-"+str(int(b, 2))+"]"]
    elif (funcCode == '1000'):
        return [str(int(a, 2)), str(int(b, 2))]


@app.route('/')
def health_check():
    return "Application is running"

@app.route('/loadSource', methods = ['POST'])
@cross_origin()
def load():
    global hit, miss, replace, cpu, ram, cache, tlb
    cpu = CPU(request.json, 16, 0, {})
    hit = 0
    miss = 0
    replace = 0
    return "Executed: "+ "Save instructions" + "\n\nregisters:" + "\nrbp: " + str(cpu.cpuRegister['rbp']) + "\npc: " + str(cpu.cpuRegister['pc']) + "\ncmp: " + str(cpu.cpuRegister['cmp']) +"\n\nhit:" + str(hit) + "\nmiss:" + str(miss) + "\nreplace:" + str(replace) + '\n' + cache.prettyPrint() + '\n\n' + ram.prettyPrint() + '\n\n' + tlb.prettyPrint()
    

@app.route('/runLine', methods = ['POST'])
@cross_origin()
def run():
    global cpu, hit, miss, replace
    return "Executed: "+ str(cpu.runLine()) + "\n\nregisters:" + "\nrbp: " + str(cpu.cpuRegister['rbp']) + "\npc: " + str(cpu.cpuRegister['pc']) + "\ncmp: " + str(cpu.cpuRegister['cmp']) +"\n\nhit:" + str(hit) + "\nmiss:" + str(miss) + "\nreplace:" + str(replace) + '\n' + cache.prettyPrint() + '\n' + ram.prettyPrint()


@app.route('/compile', methods = ['POST'])
@cross_origin()
def compile():
    source = request.json
    compiler = Compiler()
    function_indices = []
    for i, line in enumerate(source):
        if re.match(compiler.function_pattern, line):
            function_indices.append(i)

    functions = []
    for i, index in enumerate(function_indices):
        if i == len(function_indices)-1:
            functions.append(source[index:])
        else:
            functions.append(source[index:function_indices[i+1]])

    try:
        assembly = []
        function_names = []
        if not functions:
            raise Exception('no valid function(s) found')

        for function in functions:
            num_parens = 0
            num_bracks = 0
            for line in function:
                for char in line: # match parentheses and brackets
                    if char == '(':   num_parens += 1
                    elif char == ')': num_parens -= 1
                    elif char == '{': num_bracks += 1
                    elif char == '}': num_bracks -= 1
            if num_parens != 0 or num_bracks != 0:
                raise Exception('mismatched parentheses or brackets')

            head = compiler.read_head(function[0])
            returnType = head[0]
            functionName = head[1]
            if head[2] and head[3]:
                compiler.declaration += 1
                parameter = {
                    'type': head[2],
                    'name': head[3],
                    'address': -(compiler.declaration*4),
                    'codeType': 'declaration'
                }
                function_names.append((functionName, 'function', 1))
            else:
                parameter = {
                    'type': '',
                    'name': ''
                }
                function_names.append((functionName, 'function', 0))

            instruction = compiler.read_instruction(1, function)['statement'] # ignore the first line
            functionClass = Function(returnType, functionName, parameter, instruction)
            obj = functionClass.get_object()
            assembly += MethodGenerator(obj).getObject()
            compiler.identifiers = copy.deepcopy(function_names) # clear local variables, keep global variables (function names)

        machineCode = MachineCode(assembly, (compiler.declaration+1)*-4).getObject()
        print machineCode
        return jsonify({'assembly': assembly, 'machineCode': machineCode})
    except Exception as e:
        return jsonify(str(e)), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)
