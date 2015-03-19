DCPU-16:
=======
A DCPU-16 implementation written in Python. Supports basic compilation of C files, (compiler credit to https://github.com/0x-omicron/py-dcpu-c-compiler), basic text rendering, basic graphics, and all opcodes from version 1.0. Also has a GUI which allows you to watch registers, step through code on word at a time, and watch memory change. Further, this emulator has a regression testing suite, allowing tracking down bugs easier. 

All code is fully documented with docstrings for each method/class, with the occasional in-line comment, and most features of the emulator is shown in example files in either /example/, or /src/tests/.


Dependencies:
-------------
* Python 2.x for the compiler
* Python 3.x for everything else

Running:
--------
Given a DCPU-16 assembly file, you can run it with;
    $python3 main.py <my_file>.dasm

If you'd like to run it with the GUI, use the GUI flag (-g);
    $python3 main.py -g <my_file>.dasm

And lastly, if you already have an assembled DCPU-16 program, use the assembled flag (-a);
    $python3 main.py -a <my_file>.dasm

Tests:
------
If you'd like to run regression tests, put the DCPU-16 assembly file in the src/tests/ directory, along with the expected output of the test in filename.out, then run the following command;
    $python3 test.py 

The script will automatically assemble and run all tests in the src/tests/ directory, testing to see if their output matches the expected output.



