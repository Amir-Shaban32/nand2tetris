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
    if len(sys.argv) != 2:
        print("Usage: python3 VMTranslator.py file_name.vm")
        return

    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + ".asm"

    parser = Parser(input_file)
    codewriter = CodeWriter(output_file)

    while parser.hasMoreLines():
        parser.advance()
        ctype = parser.commandType()
        
        if ctype == C_ARITHMETIC:
            codewriter.writeArithmetic(parser.arg1())
        else:
            codewriter.writePushPop(ctype, parser.arg1(), parser.arg2())

    codewriter.close()

if __name__ == "__main__":
    main()