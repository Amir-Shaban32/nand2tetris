import sys
import os
from Parser import *
from CodeWriter import *
from CommandType import *


def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python3 VMTranslator.py <file.vm|directory>")
        return

    input_path = sys.argv[1]
    
    # Check if input exists
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found!")
        return

    # Determine if single file or directory
    if os.path.isfile(input_path) and input_path.endswith('.vm'):
        # Single file mode
        vm_files = [input_path]
        input_basename = os.path.basename(input_path)
        output_file = os.path.splitext(input_basename)[0] + ".asm"
        
    elif os.path.isdir(input_path):
        # Directory mode
        vm_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.vm')]
        if not vm_files:
            print(f"No .vm files found in directory: {input_path}")
            return
        # Output file named after directory, saved in current directory
        dir_name = os.path.basename(input_path.rstrip('/\\'))
        output_file = dir_name + ".asm"
        
    else:
        print("Error: Input must be a .vm file or directory containing .vm files")
        return

    print(f"Output: {output_file}")

    # Initialize code writer
    codewriter = CodeWriter(output_file)
    
    # Add bootstrap code (always needed for Project 8)
    if any('Sys.vm' in file for file in vm_files):
        codewriter.writeInit()

    # Process all VM files
    for vm_file in sorted(vm_files):
        print(f"Processing: {vm_file}")
        
        parser = Parser(vm_file)
        codewriter.setFileName(vm_file)

        while parser.hasMoreLines():
            parser.advance()
            command_type = parser.commandType()

            if command_type == C_ARITHMETIC:
                codewriter.writeArithmetic(parser.arg1())
            
            elif command_type == C_PUSH or command_type == C_POP:
                codewriter.writePushPop(command_type, parser.arg1(), parser.arg2())
            
            elif command_type == C_LABEL:
                codewriter.writeLabel(parser.arg1())
            
            elif command_type == C_GOTO:
                codewriter.writeGoto(parser.arg1())
            
            elif command_type == C_IF:
                codewriter.writeIf(parser.arg1())
            
            elif command_type == C_FUNCTION:
                codewriter.writeFunction(parser.arg1(), parser.arg2())
            
            elif command_type == C_CALL:
                codewriter.writeCall(parser.arg1(), parser.arg2())
            
            elif command_type == C_RETURN:
                codewriter.writeReturn()

    # Close the output file
    codewriter.close()
    print("Translation complete!")

if __name__ == "__main__":
    main()