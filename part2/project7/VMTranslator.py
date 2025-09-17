import sys
import os
from Parser import *
from CodeWriter import *
from CommandType import *

def main():
    """
    Main entry point for the VM Translator.
    Expects a single .vm file as input, translates it to Hack assembly (.asm).
    """
    # Check for correct usage
    if len(sys.argv) != 2:
        print("Usage: python3 VMTranslator.py file_name.vm")
        return

    input_file = sys.argv[1]
    # Generate output file name in the current directory, replacing .vm with .asm
    output_file = os.path.splitext(os.path.basename(input_file).replace('.vm', ''))[0] + ".asm"

    # Initialize parser and code writer
    parser = Parser(input_file)
    codewriter = CodeWriter(output_file)

    # Process each VM command in the input file
    while parser.hasMoreLines():
        parser.advance()  # Move to the next command
        ctype = parser.commandType()  # Determine the command type
        if ctype == C_ARITHMETIC:
            # Handle arithmetic/logical commands
            codewriter.writeArithmetic(parser.arg1())
        else:
            # Handle push/pop commands
            segment = parser.arg1()
            idx = parser.arg2()
            codewriter.writePushPop(ctype, segment, idx)

    # Close the output file
    codewriter.close()

if __name__ == "__main__":
    main()