"""CPU functionality."""

import sys
# Instructions
## ALU
ADD  = 0b10100000
SUB  = 0b10100001
MUL  = 0b10100010
DIV  = 0b10100011
INC  = 0b01100101
DEC  = 0b01100110
CMP  = 0b10100111

## PC
CALL = 0b01010000
RET  = 0b00010001
INT  = 0b01010010
IRET = 0b00010011
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
JGT  = 0b01010111
JLT  = 0b01011000
JLE  = 0b01011001
JGE  = 0b01011010

## GENERAL
NOP  = 0b00000000
LDI  = 0b10000010
LD   = 0b10000011
ST   = 0b10000100
PUSH = 0b01000101
POP  = 0b01000110
PRN  = 0b01000111
PRA  = 0b01001000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0 # Program Counter
        self.fl = 0b00000000 # 00000LGE
        self.ram = [0] * 256 # bytes of memory
        self.reg = [0] * 8 # 8 general purpose registers
        self.reg[7] = 0xF4 # default value
        self.ops = {}
        self.set_ops()

    def set_ops(self):

        self.ops[LDI] = self.ldi
        self.ops[PRN] = self.prn
        self.ops[MUL] = "MUL"
        self.ops[ADD] = "ADD"
        self.ops[CMP] = "CMP"
        self.ops[PUSH] = self.push
        self.ops[POP] = self.pop
        self.ops[CALL] = self.call
        self.ops[RET] = self.ret
        self.ops[ST] = self.st
        self.ops[JMP] = self.jmp
        self.ops[JEQ] = self.jeq
        self.ops[JNE] = self.jne


    def load(self, file_name):
        """Load a program into memory."""
        address = 0
        with open(file_name) as f:
            for line in f:
                line = line.split('#')
                line = line[0].strip()

                if line == '':
                    continue

                self.ram[address] = (int(line, 2))
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

    def ldi(self, reg_num, value):
        self.reg[reg_num] = value

    def prn(self, reg_num, y):
        print(self.reg[reg_num])

    def call(self, reg_num):
        # Get next instruction after CALL
        next_inst_pointer = self.pc + 2
        # Push the next instruction to stack
        self.push(None, next_inst_pointer)
        # Set PC to register value
        self.pc = self.reg[reg_num]

    def ret(self, x):
        # Save reg_0 value
        reg_0 = self.reg[0]
        # Store popped item to reg_0
        self.pop(0, None)
        # Set PC to value of reg_0
        self.pc = self.reg[0]
        # Restore reg_0 value
        self.ldi(0, reg_0)

    def st(self, reg_b, reg_a):
        """Store value in registerB in the address stored in registerA"""
        value = self.reg[reg_b]
        address = self.reg[reg_a]
        self.ram_write(address,value)

    def jmp(self, reg_num):
        self.pc = self.reg[reg_num]

    def jeq(self, reg_num):
        equal = self.fl & 0b00000001
        if equal:
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def jne(self, reg_num):
        equal = self.fl & 0b00000001
        if not equal:
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def push(self, reg_num, inst):
        """Copy the value in the given register to the address pointed to by SP"""
        if self.reg[7] > 0:
            self.reg[7] -= 1
            if reg_num and not inst:
                value = self.reg[reg_num]
                self.ram_write(self.reg[7], value)
            else:
                self.ram_write(self.reg[7], inst)


    def pop(self, reg_num, y):
        """Copy the value from the address pointed to by SP to the given register"""
        if self.reg[7] < 0xF4:
            value = self.ram_read(self.reg[7])
            self.reg[reg_num] = value
            self.reg[7] += 1

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        """accept the address to read and return the value stored there"""
        return self.ram[address]

    def ram_write(self, address, value):
        """accept a value to write, and the address to write it to"""
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        HLT  = 0b00000001
        running = True
        while running:

            ir = self.ram_read(self.pc)
            inst_len = (ir >> 6) + 0b1
            is_ALU = (ir & 0b00100000) >> 5
            is_PC_mutator = (ir & 0b00010000) >> 4

            x = None
            y = None

            if inst_len > 1:
                x = self.ram_read(self.pc + 1)
            if inst_len > 2:
                y = self.ram_read(self.pc + 2)

            if is_ALU:
                self.alu(self.ops[ir], x, y)
                self.pc += inst_len
            elif is_PC_mutator:
                self.ops[ir](x)
            elif ir in self.ops:
                self.ops[ir](x, y)
                self.pc += inst_len
            elif ir == HLT:
                running = False
            else:
                print("Invalid Instruction. Exiting LS8.")
                break
