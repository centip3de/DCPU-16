import os
import subprocess
import assembler

def main():
    # Walk through the entire test directory
    for root, dirs, files in os.walk("test/"):

        # For the individual files
        for f in files:

            # If it's an actual dasm file
            if f.endswith("dasm"):
                
                # Make pretty output
                print("Working with test, " + f)
                print("\tAssembling... ", end="")

                # Try to assemble
                filepath = os.path.splitext(root + f)[0]
                assembler.main(filepath + ".dasm")

                # If the obj exists, the assembling was correct
                if(os.path.exists(filepath +  ".obj")):
                    print("PASS")     

                    # Open the expected output file (filename.out) and read in the text
                    fi = open(filepath + ".out")
                    text = fi.read()
                    fi.close()

                    # Pretty-ness
                    print("\tEmulating... ", end="") 

                    # Open a subprocess and run a new python instance on the emulator, capturing it's output
                    output = subprocess.check_output(["python3", "emulator.py", (filepath + ".obj")], universal_newlines = True)
                    print(output)
                    print(text)

                    # If the output matches the expected output, it passed. 
                    if output == text:
                        print("PASS\n")
                    else:
                        print("FAIL\n")
                else:
                    print("FAIL")

if __name__ == "__main__":
    main()
