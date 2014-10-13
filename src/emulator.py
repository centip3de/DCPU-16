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

    def SET(self, dest, src):

        """
        Sets the given location to the src.
        Args:
                dest - The destination to set.
                src  - The thing to set the destination to.
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                pass
                #self.PC = src
            else:
                self.regs[dest] = src

        else:
            self.mem[dest] = src

        self.cycle(1)

    def XOR(self, dest, src):
        
        """
        Sets the given destination to destination^src
        Args:
                dest - The destination to set
                src  - The thing to xor the desintation by
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC ^= src
            else:
                self.regs[dest] ^= src
        else:
            self.mem[dest] ^= src

        self.cycle(1)

    def BOR(self, dest, src):
        
        """
        Sets the given destination to destination|src.
        Args:
                dest - The destination to set
                src  - The thing to or the destination by
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC |= src
            else:
                self.regs[dest] |= src

        else:
            self.mem[dest] |= src

        self.cycle(1)

    def AND(self, dest, src):

        """
        Sets the given destination to destination^src.
        Args:
                dest - The destination to set
                src  - The thing to and the destination by
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC &= src
            else:
                self.regs[dest] &= src
        else:
            self.mem[dest] &= src

        self.cycle(1)

    def SHR(self, dest, src):

        """
        Sets the given destination to destination >> src, and O to ((dest<<16)>>src)&0xFFFF
        Args:
                dest - The destination to set
                src  - The thing to shift the desination by
        Returns:
                None
        """
        
        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC = self.PC >> src

            else:
                self.regs[dest] = self.regs[dest] >> src

        else:
            self.mem[dest] = self.mem[dest] >> src

        self.O = ((dest<<16)>>src)&0xFFFF

        self.cycle(2)

    def SHL(self, dest, src):

        """
        Sets the given destination to destination << src, and O to ((dest<>16)&0xFFFF)
        Args:
                dest - The destination to set
                src  - The thing to shift the destination by
        Returns:
                None
        """


        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC = self.PC << src
            else:
                self.regs[dest] = self.regs[dest] << src

        else:
            self.mem[dest] = self.mem[dest] << src

        # What the hell is the '<>' operator?!
        #self.O = ((dest<>16)&0xFFFF)

        self.cycle(2)

    def MOD(self, dest, src):

        """
        Sets the given destination to destination%src. If src == 0, sets the destination to 0. 
        Args:
                dest - The destination to set
                src  - The thing to mod the destination to.
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                if src == 0:
                    self.PC = 0
                else:
                    self.PC %= src

            else:
                if src == 0:
                    self.regs[dest] = 0
                else:
                    self.regs[dest] %= src

        else:
            if src == 0:
                self.mem[dest] = 0
            else:
                self.mem[dest] %= src

        self.cycle(3)

    def SUB(self, dest, src):

        """
        Sets dest to dest - src
        Args:
                dest - The destination to set.
                src  - The thing to subtract from the destination.
        Returns:
                None
        """

        # FIXME: Underflows are not detected. 

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC -= src

            else:
                self.regs[dest] -= src
        else:
            self.mem[dest] -= src

        self.cycle(2)

    def ADD(self, dest, src):

        """
        Sets dest to dest + src
        Args:
                dest - The destination to set.
                src  - The thing to add to the destination.
        Returns:
                None
        """

        # FIXME: Overflows are not detected.

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC += src

            else:
                self.regs[dest] += src

        else:
            self.mem[dest] += src

        self.cycle(2)

    def MUL(self, dest, src):
        
        """
        Sets dest to dest * src, and O to ((dest*src)>>16)&0xFFFF.
        Args:
                dest - The destination.
                src  - The thing to multiply the destination to.
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                self.PC *= src

            else:
                self.regs[dest] *= src

        else:
            self.mem[dest] *= src

        # Magic
        self.O = ((dest*src)>>16)&0xFFFF

        self.cycle(2)

    def DIV(self, dest, src):

        """
        Sets dest to dest/src, and O to ((dest/src)<<16)&0xFFFF if src != 0. If src == 0, then O = 0, and dest = 0.
        Args:
                dest - The destination 
                src  - The thing to divide the destination by.
        Returns:
                None
        """

        if self.is_reg(dest):
            if dest == 0x1C:
                if src == 0:
                    self.PC = 0
                else:
                    self.PC /= src

            else:
                if src == 0:
                    self.regs[dest] = 0 
                else:
                    self.regs[dest] /= src

        else:
            if src == 0:
                self.mem[dest] = 0
            else:
                self.mem[dest] /= src

        if src == 0:
            self.O = 0
        else:
            # Magic
            self.O = ((dest<<16)/src)&0xFFFF

        self.cycle(3)

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
        
        # Handle basic opcodes
        if op in REV_BASIC:

            # Handle literal bitpacking in the source
            if src >= 0x20 and src <= 0x3f:
                src -= 32

            # Handle literal bitpacking in the destination
            if dest >= 0x20 and dest <= 0x3f:
                dest -= 32

            # Handle accessing register memory 
            if src in REV_VALUES and (src >= 0x08 and src <=0x0F):
                src = self.regs[src - 0x08] 

            # Handle accesssing register memory
            if dest in REV_VALUES and (dest >= 0x08 and dest <=0x0F):
                dest = self.regs[dest - 0x08]

            # Handle literals in the destination
            if dest == 0x1f:
                dest = self.get_next()

            # Handle accessing memory
            if dest == 0x1e:
                dest = self.mem[self.get_next()]

            # Handle literals in the source
            if src == 0x1f:
                src = self.get_next()

            # Handle accessing memory
            if src == 0x1e:
                src = self.mem[self.get_next()]

            # Handle opcodes
            if REV_BASIC[op] == "SET":
                self.SET(dest, src)

            elif REV_BASIC[op] == "ADD":
                self.ADD(dest, src)

            elif REV_BASIC[op] == "SUB":
                self.SUB(dest, src)

            elif REV_BASIC[op] == "MUL":
                self.MUL(dest, src)

            elif REV_BASIC[op] == "DIV":
                self.DIV(dest, src)

            elif REV_BASIC[op] == "MOD":
                self.MOD(dest, src)

            elif REV_BASIC[op] == "SHL":
                self.SHL(dest, src)

            elif REV_BASIC[op] == "SHR":
                self.SHR(dest, src)

            elif REV_BASIC[op] == "BOR":
                self.BOR(dest, src)

            elif REV_BASIC[op] == "XOR":
                self.XOR(dest, src)

            elif REV_BASIC[op] == "AND":
                self.AND(dest, src)

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
