import sys
from opcodes import *

"""
Todo:
    - Decrapify the code, i.e., let's not have 100 functions that do the same thing except 1 action. 
    - Handle overflows/underflows
    - Possibly get registers to work when called in the src
"""

class CPU():

    def __init__(self, text):
        self.text = text.split()
        self.skip = False
        self.mem = [0]*0x10000
        self.regs = [0] * 8
        self.PC = 0
        self.O = 0
        self.SP = 0xFFFF

    def run(self):

        """
        Loads the program into memory and steps through it. 
        Args:
                None
        Returns:
                None
        """

        self.load(self.text)

        while(self.PC != len(self.text)):
            self.step()

        self.reg_dump()

    def reg_dump(self):

        """
        Prints out every register excluding O and SP.
        Args:
                None
        Returns:
                None
        """

        print("********* REG DUMP *********")
        for i in range(len(self.regs)):
            print(REV_VALUES[i] + ": " + str(hex(self.regs[i])))

        print("PC: " + str(hex(self.PC)))
        print("O: " + str(hex(self.O)))

    def cycle(self, amount):
        
        """
        Cycles until there are no more cycles to cycle.
        Args:
                Amount - An int containing how many cycles to cycle.
        Returns:
                None
        """

        while amount > 0:
            amount -= 1

    def decode(self, word):

        """
        Decodes the packed opcode into it's seperate parts. 
        Args:
                word - The word to decode.
        Returns:
                A list of the unpacked opcodes. [op, dest, src]
        """

        op = word & 0xF
        dest = (word & 0x3F0) >> 4
        src = word >> 10

        return [op, dest, src]

    def JSR(self, dest):
        self.SP -= 1
        self.mem[self.SP] = self.PC
        self.PC = dest

    def handle_math(self, dest, src, func, cycle, overflow):

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC = func(self.PC, src)

            else:
                self.regs[dest] = func(self.regs[dest], src)

        else:
            self.mem[dest] = func(self.mem[dest], src)

        self.cycle(cycle)

        if overflow != None:
            self.O = overflow

    def handle_if(self, dest, src, func, cycle):
        
        if self.is_reg(dest):
            if dest == 0x1C:
                if func(self.PC, src):
                    pass
                else:
                    self.skip = True

            else:
                if func(self.regs[dest], src):
                    pass
                else:
                    self.skip = True

        else:
            if func(self.mem[dest], src):
                pass
            else:
                self.skip = True

        self.cycle(cycle)

    def handle_div_mod(self, dest, src, func, cycle, overflow):

        if self.is_reg(dest):
            if dest == 0x1C:
                if src == 0:
                    self.PC = 0
                else:
                    self.PC = func(self.PC, src)

            else:
                if src == 0:
                    self.regs[dest] = 0
                else:
                    self.regs[dest] = func(self.regs[dest], src)

        else:
            if src == 0:
                self.mem[dest] = 0
            else:
                self.mem[dest] = func(self.mem[dest], src)

        if overflow != None:
            if src == 0:
                self.O = 0
            else:
                self.O = overflow
            
        self.cycle(cycle)
        
    def step(self):

        """
        Does a single step of execution (single opcode)
        Args:
                None
        Returns:
                None
        """

        word = self.decode(self.get_next())
        op = word[0]
        dest = word[1]
        src  = word[2]

        # Handle literal bitpacking in the source
        if (src >= 0x20 and src <= 0x3f) or (dest >= 0x20 and dest <= 0x3f):
            if src >= 0x20 and src <= 0x3f:
                src -= 32

            # Handle literal bitpacking in the destination
            if dest >= 0x20 and dest <= 0x3f:
               dest -= 32

        else:

            if src >= 0x10 and src <= 0x17:
                src = self.regs[src - 0x10] + self.get_next()

            if dest >= 0x10 and dest <= 0x17:
                dest = self.regs[dest - 0x10] + self.get_next()

            # Handle accessing register memory 
            if src in REV_VALUES and (src >= 0x08 and src <=0x0F):
                src = self.regs[src - 0x08] 

            # Handle accesssing register memory
            if dest in REV_VALUES and (dest >= 0x08 and dest <=0x0F):
                dest = self.regs[dest - 0x08]

            # Handle poping 
            if src == 0x18:
                src = self.mem[self.SP]
                self.SP += 1

            # Handle peeking
            if src == 0x19:
                src = self.mem[self.SP]

            # Handle pushing 
            if dest == 0x1A:
                self.SP -= 1
                dest = self.SP

            # Handle literals in the destination
            if dest == 0x1f:
                dest = self.get_next()

            # Handle accessing memory
            if dest == 0x1e:
                dest = self.get_next()

            # Handle literals in the source
            if src == 0x1f:
                src = self.get_next()

            # Handle accessing memory
            if src == 0x1e:
                src = self.mem[self.get_next()]

        # Handle a failed conditional
        if self.skip:
            self.skip = False
            return

        # Handle basic opcodes
        if op in REV_BASIC:

            # Handle opcodes
            if REV_BASIC[op] == "SET":
                self.handle_math(dest, src, (lambda x, y: y), 1, None)

            elif REV_BASIC[op] == "ADD":
                self.handle_math(dest, src, (lambda x, y: x + y), 2, None)

            elif REV_BASIC[op] == "SUB":
                self.handle_math(dest, src, (lambda x, y: x - y), 2, None)

            elif REV_BASIC[op] == "MUL":
                self.handle_math(dest, src, (lambda x, y: x * y), 2, ((dest*src)>>16)&0xFFFF)

            elif REV_BASIC[op] == "DIV":
                self.handle_div_mod(dest, src, (lambda x, y: x/y), 3, ((dest<<16)/src)&0xFFFF)

            elif REV_BASIC[op] == "MOD":
                self.handle_div_mod(dest, src, (lambda x, y: x%y), 3, None)

            elif REV_BASIC[op] == "SHL":
                self.handle_math(dest, src, (lambda x, y: x << y), 2, ((dest<<src)>>16)&0xFFFF)

            elif REV_BASIC[op] == "SHR":
                self.handle_math(dest, src, (lambda x, y: x >> y), 2, ((dest<<16)>>src)&0xFFFF)

            elif REV_BASIC[op] == "BOR":
                self.handle_math(dest, src, (lambda x, y: x|y), 1, None)

            elif REV_BASIC[op] == "XOR":
                self.handle_math(dest, src, (lambda x, y: x^y), 1, None)

            elif REV_BASIC[op] == "AND":
                self.handle_math(dest, src, (lambda x, y: x&y), 1, None)

            elif REV_BASIC[op] == "IFE":
                self.handle_if(dest, src, (lambda x, y: x == y), 2)

            elif REV_BASIC[op] == "IFN":
                self.handle_if(dest, src, (lambda x, y: x != y), 2)

            elif REV_BASIC[op] == "IFG":
                self.handle_if(dest, src, (lambda x, y: x > y), 2)

            elif REV_BASIC[op] == "IFB":
                self.handle_if(dest, src, (lambda x, y: (x&y) != 0), 2)

        # Non-basic OPCODES. Note, because of the way we decode opcodes, dest will be the opcode, and src will be the dest, in the case of a non-basic-opcode.
        elif dest in REV_NON_BASIC and op == 0x0: 

            if REV_NON_BASIC[dest] == "JSR":
                self.JSR(src)

    def load(self, program):

        """
        Loads the given program into memory, starting at 0x0.
        Args:
                Program - A list of opcodes to load. 
        Returns:
                None
        """

        for i in range(len(program)):
            self.mem[i] = int(program[i], 0)

    def get_next(self):

        """
        Get's the word at PC and then adds one to PC
        Args:
                None
        Returns:
                None
        """

        mem = self.mem[self.PC]
        self.PC += 1
        self.cycle(1)
        return mem

    def is_reg(self, reg):

        """
        Checks if the given word is a register
        Args:
                reg - A hex value of the reg to check
        Returns:
                A boolean value. True if it is a register, False if it isn't.
        """

        return (reg in REV_VALUES) and ((reg >= 0x0 and reg <= 0x07) or (reg >= 0x1B and reg <= 0x1D))

def main():

    """
    Entry point of the program.
    Args:
            None
    Returns:
            None
    """

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
