import sys
from opcodes import *

class Memory():

    mem = [0]*0x10000

    def get_mem(addr):
        return Memory.mem[addr]

    def set_mem(addr, foo):
        Memory.mem[addr] = foo

class CPU():
    def __init__(self, text):
        self.text = text.splitlines()

    def run(self):
        for line in self.text:
            self.step(line.split())

    def decode(self, line):
        word = int(line[0], 0)
        op = word & 0xF
        dest = word & 0x3F0
        src = word >> 10

        if (len(line) >= 2):
            return [op, dest, src, line[1:]]

        return [op, dest, src]

    def step(self, line):
        print(self.decode(line))

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
