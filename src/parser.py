def num(n):

    """
    Take in a string, and return (number, rest_of_string) if the first character
    in the string is a number.
    """
    if len(n) != 0:
        rest = n[1:]
        n = n[0]
        if n.isdigit():
            return (n, rest)
    return None

def char(c):

    """
    Take in a character and return a parser that compares the initial character
    to a string, returning the initial character + the rest of the string (char, rest)
    if the initial character is at the front of the string.
    """

    def foo(x):
        if len(x) != 0 and c == x[0]:
            rest = x[1:]
            return (c, rest)
        return None

    return foo

def both(p, q):
    
    """
    Take in two parsers and return a parser that returns
    (first_parser(x), second_parser(x)) if both do not evalutate to None.
    """

    def foo(x):
        p_output = p(x)
        if p_output != None:
            q_output = q(p_output[1])
            if q_output != None:
                return ((p_output[0], q_output[0]), q_output[1])
        return None

    return foo

def either(p, q):

    """
    Take in two parsers and return a parser that returns the first parser
    if the output isn't None, else it returns the second parser.
    """

    def foo(x):
        p_output = p(x)
        if p_output != None:
            return p_output
        return q(x)

    return foo

def pmap(f, p):
    
    """
    Take in a function and a parser, apply the parser, and if the output is not None, 
    return the function applied to the output of the parser.
    """

    def foo(x):
        apply_p = p(x)
        if apply_p != None:
            return (f(apply_p[0]), apply_p[1])
        return None
    return foo
    
def many(p):

    """
    Take in a parser and return a parser that applies the inital parser
    as many times as possible (until it the output is None) while appending 
    the output to a list, returning the list.
    """

    def foo(x):
        li = []
        p_output = p(x)
        out = ""

        while(p_output != None):
            li.append(p_output[0])
            out = p_output[1]
            p_output = p(out)
            
        return (li, out)

    return foo

def string(x):
    
    """
    Take in a string, and return a parser that takes in a string and returns
    as many characters as it can of the initial strings matching.
    """

    def foo(y):
        partition = y.partition(x)
        if partition[0] != "" or y == "":
            return None 
        return (partition[1], partition[2])

    return foo

def _or(*args):
    def foo(x):
        i = len(args) - 1
        output = either(args[i], args[i - 1])
        i -= 2

        while(i > 0):
            output = either(args[i], output)
            i -= 1

        return output(x)
    return foo
        


def main():

    foo = _or(char('a'), char('b'), char('c'), char('d'), char('e'), char('f'))('abcdefc')
    print(foo)
    quit()
    
    a_parser = char('a')
    digits = num

    # Hex parser
    hex_char = either(char('A'), either(char('B'), either(char('C'), either(char('D'), either(char('E'), char('F'))))))
    hex_digit = either(digits, hex_char) 
    hex_digits = many(hex_digit)
    hex_parser = pmap(lambda x: "".join(x[1]), both(string("0x"), hex_digits))

    # Basic opcode parser
    op = either(char(' '), either(string("SET"), either(hex_parser, either(char("A"), either(string("SUB"), either(char('['), either(char(']'), either(string("PC"), 
         either(char('A'), string("IFN"))))))))))
    ops = many(op)
    op_parser = pmap(lambda x: "".join(x), ops)

    sample_ops = "SET A 0x30 SET [0x1000] 0x30 SUB A [0x1000] IFN A 0x10 SET PC 0x001A"

    print("Num: ", num("8abc"))
    print("Char (func): ", a_parser)
    print("Char (applied -- True): ", a_parser('abc'))
    print("Char (applied -- False): ", a_parser('bcd'))

    print("\n*******************************************\n")
    
    print("Either: ", either(num, char)("8"))
    print("Both: ", both(num, char("a"))("abc"))
    print("Either: ", either(num, char('a'))('a'))
    print("Both: ", both(char('a'), char('b'))('abc'))
    print("Apple parse: ", many(either(char('a'), either(char('p'), either(char('l'), either(char('e'), char('s'))))))("apples"))
    print("String parse (True): ", string("apple")("apple"))
    print("String parse (False): ", string("car")("apple"))
    print("String parse (Partial): ", string("car")("cars"))
    print("Test pmap: ", pmap(ord, char("a"))("a"))

    print("\n*******************************************\n")

    print("Test digit: ", digits("1234"))
    print("Test hex_char: ", hex_char("ABCDEF"))
    print("Test hex_digit: ", hex_digit("1234ABCDEF"))
    print("Test hex_digits: ", hex_digits("1234ABCDF"))
    print("Test hex (Pass): ", hex_parser("0x12348484ABCDEFFFFF"))
    print("Test hex (Fail): ", hex_parser("1234"))

    print("\n*******************************************\n")

    print("Test op: ", op(sample_ops))
    print("Test ops: ", ops(sample_ops))
    print("Test op_parser: (True) ", op_parser(sample_ops))
    print("test op_parser: (False) ", op_parser("Hi, my name is Frank."))


if __name__ == "__main__":
    main()
