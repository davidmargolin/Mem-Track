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

    def __init__(self, source):
        self.assemblyInstructions = source
        self.machineInstructions = []
        self.translate()

    def translate(self):
        pass

    # return the list of machine instructions
    def getObject(self):
        return self.machineInstructions
