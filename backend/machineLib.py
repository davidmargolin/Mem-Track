#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#               Instruction Set (32 bits)              #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#           For instructions with 2 operands:          #
#           e.g. mov, cmp, add, sub, mul, div          #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#  4 bits  |  12 bits   |  12 bits   |  4 bits         #
#  opcode  |  operand1  |  operand2  |  function code  #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#           For instructions with 1 operand:           #
#           e.g. push, pop, jmp, jl, jg, je            #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#  4 bits  |  12 bits   |            16 0's            #
#  opcode  |  reg/addr  |                              #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#           For instructions with 0 operands:          #
#           e.g. ret                                   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#  4 bits  |                         28 0's            #
#  opcode  |                                           #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# NOTE: due to 12 bit operands, min. address is -4092 and
# max. integer value is 4095 (we don't deal with negative ints)

import re

class MachineCodeException(Exception):
    pass

class MachineCode:
    MIN_ADDRESS = -4092
    MAX_INTEGER = 4095

    opCode = {
        'push': '0000',
        'pop':  '0001',
        'ret':  '0010',
        'jmp':  '0011',
        'jg':   '0100',
        'jl':   '0101',
        'jge':  '0110',
        'jle':  '0111',
        'jne':  '1000',
        'je':   '1001',
        'mov':  '1010',
        'cmp':  '1011',
        'add':  '1100',
        'sub':  '1101',
        'mul':  '1110',
        'div':  '1111'
    }

    regCode = {
        'rbp': '000000000000',
        'rsp': '000000000001',
        'eax': '000000000010',
        'ebx': '000000000011',
        'edi': '000000000100'
    }

    functionCode = {
        ('reg', 'reg'): '0000',
        ('reg', 'add'): '0001',
        ('reg', 'imm'): '0010',
        ('add', 'reg'): '0011',
        ('add', 'add'): '0100',
        ('add', 'imm'): '0101',
        ('imm', 'reg'): '0110',
        ('imm', 'add'): '0111',
        ('imm', 'imm'): '1000'
    }

    def __init__(self, source, address): # address is the first available address unused by compiler
        self.assemblyInstructions = source # create a copy to avoid making changes to original source during translation
        self.machineInstructions = []
        self.labelAddress = address
        self.labelAddresses = {}
        self.translate()

    def translate(self):
        # first pass to assign addresses to labels and remove indentation/comments
        for i, line in enumerate(self.assemblyInstructions):
            # remove indentation and comments from line
            line = re.sub('~+', '', line)
            line = re.sub('[ ]*#.*', '', line)
            self.assemblyInstructions[i] = line
            if ':' in line: # line is a label (either function label, if/for label, or return label)
                label = line[:-1] # remove ':' from end of line
                if label not in self.labelAddresses:
                    self.labelAddresses[label] = '{0:012b}'.format(-1*self.genLabelAddress()) # convert positive int to 12 bits (zero padded on left)

        # second pass to convert assembly code to machine code
        for line in self.assemblyInstructions:
            if not line or ':' in line: # ignore empty line and label line
                pass
            elif line == 'ret':
                self.machineInstructions.append(self.opCode['ret'] + ' ' + ('0'*28))
            else:
                command, operands = line.split(' ', 1)
                # 1 operand commands with register as operand
                if command in ['push', 'pop']:
                    self.machineInstructions.append(self.opCode[command] + ' ' + self.regCode[operands] + ' ' + ('0'*16))

                # 1 operand commands with label address as operand
                elif command in ['jmp', 'jg', 'jl', 'jge', 'jle', 'jne', 'je']:
                    self.machineInstructions.append(self.opCode[command] + ' ' + self.labelAddresses[operands] + ' ' + ('0'*16))

                # 2 operand commands (either operand can be register, address, or immediate)
                elif command in ['mov', 'cmp', 'add', 'sub', 'mul', 'div']:
                    op1, op2 = operands.split(', ', 1)
                    if op1 in self.regCode: # op1 is a register (e.g. 'eax')
                        if op2 in self.regCode:
                            fc = self.functionCode[('reg', 'reg')]
                            self.machineInstructions.append(self.opCode[command] + ' ' + self.regCode[op1] + ' ' + self.regCode[op2] + ' ' + fc)
                        elif op2.isdigit():
                            fc = self.functionCode[('reg', 'imm')]
                            if int(op2) > self.MAX_INTEGER:
                                raise MachineCodeException('maximum integer value is ' + str(self.MAX_INTEGER))
                            self.machineInstructions.append(self.opCode[command] + ' ' + self.regCode[op1] + ' ' + '{0:012b}'.format(int(op2)) + ' ' + fc)
                        else:
                            fc = self.functionCode[('reg', 'add')]
                            address2 = '{0:012b}'.format(int(re.search('[0-9]+', op2).group(0)))
                            self.machineInstructions.append(self.opCode[command] + ' ' + self.regCode[op1] + ' ' + address2 + ' ' + fc)

                    elif op1.isdigit(): # op1 is an immediate (e.g. '12')
                        if int(op1) > self.MAX_INTEGER:
                            raise MachineCodeException('maximum integer value is ' + str(self.MAX_INTEGER))
                        if op2 in self.regCode:
                            fc = self.functionCode[('imm', 'reg')]
                            self.machineInstructions.append(self.opCode[command] + ' ' + '{0:012b}'.format(int(op1)) + ' ' + self.regCode[op2] + ' ' + fc)
                        elif op2.isdigit():
                            fc = self.functionCode[('imm', 'imm')]
                            if int(op2) > self.MAX_INTEGER:
                                raise MachineCodeException('maximum integer value is ' + str(self.MAX_INTEGER))
                            self.machineInstructions.append(self.opCode[command] + ' ' + '{0:012b}'.format(int(op1)) + ' ' + '{0:012b}'.format(int(op2)) + ' ' + fc)
                        else:
                            fc = self.functionCode[('imm', 'add')]
                            address2 = '{0:012b}'.format(int(re.search('[0-9]+', op2).group(0)))
                            self.machineInstructions.append(self.opCode[command] + ' ' + '{0:012b}'.format(int(op1)) + ' ' + address2 + ' ' + fc)

                    else: # op1 is an address (e.g. 'DWORD PTR [rbp-12]')
                        address1 = '{0:012b}'.format(int(re.search('[0-9]+', op1).group(0)))
                        if op2 in self.regCode:
                            fc = self.functionCode[('add', 'reg')]
                            self.machineInstructions.append(self.opCode[command] + ' ' + address1 + ' ' + self.regCode[op2] + ' ' + fc)
                        elif op2.isdigit():
                            fc = self.functionCode[('add', 'imm')]
                            if int(op2) > self.MAX_INTEGER:
                                raise MachineCodeException('maximum integer value is ' + str(self.MAX_INTEGER))
                            self.machineInstructions.append(self.opCode[command] + ' ' + address1 + ' ' + '{0:012b}'.format(int(op2)) + ' ' + fc)
                        else:
                            fc = self.functionCode[('add', 'add')]
                            address2 = '{0:012b}'.format(int(re.search('[0-9]+', op2).group(0)))
                            self.machineInstructions.append(self.opCode[command] + ' ' + address1 + ' ' + address2 + ' ' + fc)

    # return the list of machine instructions
    def getObject(self):
        return self.machineInstructions

    #return label address and then decrement by 4 (addresses are multiples of 4)
    def genLabelAddress(self):
        tmp = self.labelAddress
        self.labelAddress-=4
        if self.labelAddress < self.MIN_ADDRESS:
            raise MachineCodeException('not enough main memory')
        return tmp
