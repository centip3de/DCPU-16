import sys
import emulator 
import assembler
import gui
import argparse

def main():

    """ 
    Entry point of the program. Takes in the arguments, parses them, 
    and calls the assembler/emulator/gui as appropriate.

    Args:
        None
    Returns:
        None
    """

    parser = argparse.ArgumentParser(description = "Automate the assembling and emulation of the given file.")
    parser.add_argument("filepath", help="The path to the .dasm file to run.")
    parser.add_argument("-g", action="store_true", help="Enable the GUI") 
    parser.add_argument("-a", action="store_true", help="Mark that the code is already assembled")

    args = parser.parse_args()
    
    filepath = args.filepath
    guiFlag = args.g
    assembledFlag = args.a

    fi = open(filepath, "r")
    text = fi.read()
    fi.close()

    if(assembledFlag):
        cpu = emulator.CPU(text)
    else:
        p = assembler.Parser(text).assemble()
        cpu = emulator.CPU(p)


    if not guiFlag:
        cpu.run()
    else:
        if(assembledFlag):
            gui.main(text)
        else:
            gui.main(p)

if __name__ == "__main__":
    main()
