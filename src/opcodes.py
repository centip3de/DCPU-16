# Upper 11 bits
VALUES = {
    "A" : 0x00, 
    "B" : 0x01, 
    "C" : 0x02, 
    "X" : 0x03, 
    "Y" : 0x04, 
    "Z" : 0x05, 
    "I" : 0x06, 
    "J" : 0x07,
    "[A]" : 0x08, 
    "[B]" : 0x09, 
    "[C]" : 0x0A, 
    "[X]" : 0x0B,  
    "[Y]" : 0x0C, 
    "[Z]" : 0x0D, 
    "[I]" : 0x0E, 
    "[J]" : 0x0F, 
    "POP" : 0x18, 
    "PEEK" : 0x19, 
    "PUSH" : 0x1A, 
    "SP" : 0x1B, 
    "PC" : 0x1C, 
    "O" : 0x1D }

BASIC_OPCODES = {
    "SET" : 0x01 , 
    "ADD" : 0x02, 
    "SUB" : 0x03, 
    "MUL" : 0x04, 
    "DIV" : 0x05, 
    "MOD" : 0x06, 
    "SHL" : 0x07, 
    "SHR" : 0x08,
    "AND" : 0x09, 
    "BOR" : 0x0A,
    "XOR" : 0x0B,
    "IFE" : 0x0C, 
    "IFN" : 0x0D, 
    "IFG" : 0x0E,
    "IFB" : 0x0F}

NON_BASIC_OPCODES = {
    "JSR" : 0x01} 

# Reverse lookups
REV_VALUES = {value : key for (key, value) in VALUES.items()}
REV_BASIC = {value : key for (key, value) in BASIC_OPCODES.items()}
REV_NON_BASIC = {value : key for (key, value) in NON_BASIC_OPCODES.items()}
