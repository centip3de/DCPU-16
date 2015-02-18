import sys
import os
from opcodes import *

class Parser():

        # Contains everything needed to parse and assemble the supplied text into machine code. 

    def __init__(self, text):

        # The constructor for the Parser class. 
        # Args:
        #       text - The text to be parsed
        # Returns:
        #       An instance of this class.

        self.text = text
        self.LABELS = {}
        self.count = 0

    #FIXME: The ASM shouldn't be forced to be whitespace delimited... But it is... For now. 
    def assemble(self):

        # Assembles the text supplied in the constructor into machine code to be read by the emulator.
        # Args:
        #       None
        # Returns:
        #       A string containing the compiled opcodes.

        compiled = []
        pretty = []

        for words in self.clean_text():

            if words[0][0] == ":":
                label = words.pop(0)
                name = label[1:]
                self.LABELS[name] = self.count 
                continue

            if words[0] in BASIC_OPCODES:
                compiled.append(self.handle_basic(words))

            elif words[0] in NON_BASIC_OPCODES:
                compiled.append(self.handle_non_basic(words))

            else:
                print("Unknown opcode, " + words[0])

        for i in range(len(compiled)):
            for j in range(len(compiled[i])):
                foo = compiled[i]
                if foo[j] in self.LABELS:
                    compiled[i][j] = hex(self.LABELS[foo[j]])
            pretty.append(" ".join(compiled[i]))

        return " ".join(pretty)

    def handle(self, word):

        # Handles each opcode, compiling, adding prefaces, or packing them as necessary.
        # Args:
        #       word - A single opcode in a string
        # Returns:
        #       A list containing the compiled/prefaced/packed version of said opcode. 

        # Handle  registers and the like
        if word in VALUES:
            return [VALUES[word]]

        # Handle basic opcodes
        elif word in BASIC_OPCODES:
            return [BASIC_OPCODES[word]]

        # Handle non-basic-opcodes
        elif word in NON_BASIC_OPCODES:
            return [NON_BASIC_OPCODES[word]]
        
        # Handle addressing scheme
        elif word[0] == "[":
            li = word[1:-1]
            foo = "".join(li)

            if self.is_num(foo):
                return [0x1E, hex(int(foo, 0))]

            elif foo.find("+") != -1:
                bar = foo.split("+")
                return [0x16, bar[0]]

        # Handle literals
        elif self.is_num(word):

            # If the literal is less than 1F, add 32 to it. Magic.
            if(int(word,0) <= 0x1F): 
                return [int(word, 0) + 32]

            else:
                return [0x1F, hex(int(word, 0))]

        # Handle labels
        elif word in self.LABELS:
            return [0x1F, word]

    def handle_basic(self, tokens):

        # Handles and compiles basic opcodes.
        # Args:
        #       tokens - A list containing the given line split on white spaces.
        # Returns:
        #       A list containing the assembled version of said line.

        # Handle the initial tokens
        op = BASIC_OPCODES[tokens[0]]
        src = self.handle(tokens[1])
        dest = self.handle(tokens[2])

        # Pack into 16 bits
        compiled = []
        compiled.append(hex(op + (src[0] << 4) + (dest[0] << 10)))

        # Catch trailing values
        if len(src) == 2:
            compiled.append(src[1])

        if len(dest) == 2:
            compiled.append(dest[1])

        self.count += len(compiled)

        # Return list of compiled-ness
        return compiled

    def handle_non_basic(self, tokens):

        # Handles and compiles non-basic opcodes. 
        # Args:
        #       tokens - A list containing the given line split on white spaces. 
        # Returns:
        #       A list containing the compiled version of said line 

        # Handle the initial tokens
        op = NON_BASIC_OPCODES[tokens[0]]
        src = self.handle(tokens[1])

        # Pack into 16 bits
        compiled = []
        compiled.append(hex((op << 4) + (src[0] << 10)))

        # Catch trailing values. 
        if len(src) == 2:
            compiled.append(src[1])

        self.count += len(compiled)

        # Return list of compiled-ness
        return compiled


    def is_num(self, num):

        # Checks if the given string is a number, hex or otherwise. 
        # Args:
        #       num - A string containing a number
        # Returns:
        #       A boolean value. True if it's a number, False if it isn't. 

        return all(x in "0123456789ABCDEFabcedfx" for x in num)

    def clean_text(self):

        # Cleans all the text by removing comments, blank lines, and adding the labels to the hash table.
        # Args:
        #       None
        # Returns:
        #       A list where every index is a cleaned line. 

        cleaned = []

        for line in self.text.splitlines():
            words = line.split()

            if line == "":
                continue
            elif words[0][0] == ";" : 
                continue
            elif words[0][0] == ":":
                label = words[0]
                name = label[1:]
                self.LABELS[name] = 0  
         
            cleaned.append(words)

        return cleaned
        
def main(filepath):

    # Entry point of the program. Takes the file as an arg, parses it, and outputs it in an object file matching the original file name.  
    # Args:
    #       None
    # Returns:
    #       None

    
    filename = os.path.splitext(filepath)[0]

    fi = open(filepath, "r")
    fo = open(filename + ".obj", "w")

    text = fi.read()
    p = Parser(text)
    fo.write(p.assemble())

    fi.close()
    fo.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 assemble.py file.dasm")
        exit(1)

    main(sys.argv[1])
