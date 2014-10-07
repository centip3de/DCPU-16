import sys
from opcodes import *

class CPU():

    def __init__(self, text):
        self.text = text.split()
        self.mem = [0]*0x10000
        self.regs = [0] * 8
        self.PC = 0
        self.O = 0
        self.SP = 0

    def run(self):
        self.load(self.text)

        while(self.PC != len(self.text)):
            self.step()

        self.reg_dump()

    def reg_dump(self):
        print("********* REG DUMP *********")
        for i in range(len(self.regs)):
            print(REV_VALUES[i] + ": " + str(hex(self.regs[i])))

        print("PC: " + str(hex(self.PC)))

    def cycle(self, amount):
        while amount > 0:
            amount -= 1

    def decode(self, word):
        op = word & 0xF
        dest = (word & 0x3F0) >> 4
        src = word >> 10

        return [op, dest, src]

    def SET(self, dest, src):
        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC = src
            else:
                self.regs[dest] = src

        else:
            self.mem[dest] = src

        self.cycle(1)

    def step(self):
        word = self.decode(self.get_next())
        op = word[0]
        dest = word[1]
        src  = word[2]

        
        if op in REV_BASIC:

            if src >= 0x20 and src <= 0x3f:
                src -= 32

            if dest >= 0x20 and dest <= 0x3f:
                dest -= 32

            if dest == 0x1e:
                dest = self.get_next()

            if src == 0x1f:
                src = self.get_next()

            if src == 0x1e:
                src = self.get_next()

            
            if REV_BASIC[op] == "SET":
                self.SET(dest, src)

    def load(self, program):
        for i in range(len(program)):
            self.mem[i] = int(program[i], 0)

    def get_next(self):
        mem = self.mem[self.PC]
        self.PC += 1
        return mem

    def is_reg(self, reg):
        return (reg in REV_VALUES) and ((reg >= 0x0 and reg <= 0x07) or (reg >= 0x1B and reg <= 0x1D))

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 emulator.py file.obj")
        exit(1)
    
    filepath = sys.argv[1]
    fi = open(filepath, "r")
    text = fi.read()

    cpu = CPU(text)
    cpu.run()

if __name__ == "__main__":
    main()
