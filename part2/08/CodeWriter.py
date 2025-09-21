from Parser import *
import os


class CodeWriter:
    """
    Translates VM commands into Hack assembly code and writes to the output file.
    Supports arithmetic, memory access, branching, functions, calls, and returns.
    """

    def __init__(self, file_name):
        # Open the output .asm file for writing
        self.file = open(file_name, "w")
        self.label_counter = 0  # Used for generating unique labels in comparison commands
        self.file_name = file_name  # Used for static variable naming
        self.current_function = ""  # Track current function for label scoping

    def writeInit(self):
        """
        Writes bootstrap code that initializes the VM.
        Sets SP to 256 and calls Sys.init - required for Project 8.
        """
        bootstrap = """// Bootstrap code - initialize VM
@256
D=A
@SP
M=D
"""
        self.write(bootstrap)
        self.writeCall("Sys.init", 0)

    def writeArithmetic(self, command):
        """
        Writes assembly code for arithmetic and logical VM commands.
        Handles: add, sub, neg, and, or, not, eq, gt, lt
        """
        if command == "add":
            # Pop two values, add, push result
            self.write(
                "//add\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=D+M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "sub":
            # Pop two values, subtract, push result
            self.write(
                "//sub\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=M-D\n"
                "@SP\nM=M+1\n"
            )
        elif command == "neg":
            # Negate the top value on the stack
            self.write(
                "//neg\n"
                "@SP\nM=M-1\nA=M\nM=-M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "and":
            # Pop two values, bitwise AND, push result
            self.write(
                "//and\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=D&M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "or":
            # Pop two values, bitwise OR, push result
            self.write(
                "//or\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=D|M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "not":
            # Bitwise NOT of the top value on the stack
            self.write(
                "//not\n"
                "@SP\nM=M-1\nA=M\nM=!M\n"
                "@SP\nM=M+1\n"
            )
        elif command in ("eq", "gt", "lt"):
            # Comparison commands (eq, gt, lt)
            self._write_comparison(command)

    def writePushPop(self, command, segment, idx):
        """
        Writes assembly code for push and pop VM commands.
        Dispatches to the appropriate helper based on segment type.
        """
        asm = None
        if segment in ("constant", "temp"):
            asm = self._write_cons_temp(command, segment, idx)
        elif segment in ("static", "pointer"):
            asm = self._write_pointer_static(command, segment, idx)
        elif segment in ("local", "argument", "this", "that"):
            asm = self._write_lcl_arg(command, segment, idx)
        self.write(asm)

    def writeLabel(self, label):
        """
        Writes assembly code for VM label command.
        Uses function scoping for Project 8 compatibility.
        """
        if self.current_function:
            full_label = f"{self.current_function}${label}"
        else:
            full_label = label
        self.write(f"({full_label})\n")
    
    def writeGoto(self, label):
        """
        Writes assembly code for VM goto command.
        """
        if label.count('.') > 0:  # If it's a function name (has dots)
            full_label = label
        elif self.current_function:
            full_label = f"{self.current_function}${label}"
        else:
            full_label = label
        self.write(f"//goto {label}\n@{full_label}\n0;JMP\n")
    
    def writeIf(self, label):
        """
        Writes assembly code for VM if-goto command.
        Pops stack and jumps if value is not zero.
        """
        if self.current_function:
            full_label = f"{self.current_function}${label}"
        else:
            full_label = label
        self.write(f"//if-goto {label}\n@SP\nAM=M-1\nD=M\n@{full_label}\nD;JNE\n")

    def writeFunction(self, funName, nVars):
        """
        Writes assembly code for VM function command.
        Sets up function label and initializes local variables to 0.
        """
        self.current_function = funName  # Track current function for label scoping
        self.write(f"// function {funName} {nVars}\n")
        self.write(f"({funName})\n")
        
        # Initialize all local variables to 0
        for _ in range(nVars):
            push0 = self._write_cons_temp("push", "constant", 0)
            self.write(push0)
    
    def writeCall(self, funName, nArgs):
        """
        Writes assembly code for VM call command.
        Implements the full calling convention: save caller frame,
        set up new frame, transfer control.
        """
        return_addr_label = f"RETURN_{funName}_{self.label_counter}"
        self.label_counter += 1
        
        self.write(f"// call {funName} {nArgs}\n")
        
        # Push return address
        retAddr = self._writeReturnAddr(return_addr_label)
        self.write(retAddr)
        
        # Save caller's frame (LCL, ARG, THIS, THAT)
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            savedSegment = self._savedCallerFrame(segment)
            self.write(savedSegment)
        
        # Reposition ARG and LCL for the called function
        repositioningARG = self._repositiningARG(nArgs)
        repositioningLCL = self._repositiningLCL()
        self.write(repositioningARG)
        self.write(repositioningLCL)
        
        # Transfer control to the called function
        self.writeGoto(funName)
        
        # Declare return address label
        self.write(f"({return_addr_label})\n")

    def writeReturn(self):
        """
        Writes assembly code for VM return command.
        Implements the full return convention: restore caller frame,
        position return value, transfer control back.
        """
        asm = """// return
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
"""
        # Restore caller's frame (THAT, THIS, ARG, LCL)
        segments = ["THAT", "THIS", "ARG", "LCL"]
        for segment in segments:
            asm += self._reconnectSavedCallerFrame(segment)
        
        # Jump to return address
        gotoReturnAddr = "@R14\nA=M\n0;JMP\n"
        asm += gotoReturnAddr
        
        self.write(asm)

    def setFileName(self, file_path):
        """
        Sets the current file name for static variable naming.
        Used when processing multiple .vm files in Project 8.
        """
        self.filename = os.path.splitext(os.path.basename(file_path))[0]
        self.write(f"// File: {self.filename}\n")

# ====== Helper functions below ======

    def _write_comparison(self, command):
        """
        Writes assembly code for comparison commands: eq, gt, lt.
        Uses unique labels for branching to avoid conflicts.
        """
        jump = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
        label_true = f"{command.upper()}_TRUE_{self.label_counter}"  
        label_end = f"{command.upper()}_END_{self.label_counter}"    
        self.label_counter += 1

        asm = f"""//{command}
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@{label_true}
D;{jump}
//false case
@SP
A=M
M=0
@{label_end}
0;JMP
//true case
({label_true})
@SP
A=M
M=-1
({label_end})
@SP
M=M+1
"""
        self.write(asm)

    def _write_cons_temp(self, command, segment, idx):
        """
        Handles push/pop for constant and temp segments.
        - constant: push only (pushes a literal value)
        - temp: push/pop to RAM[5-12] (temp registers)
        """
        original_idx = idx  # Store original index for comment
        if segment == "temp":
            idx += 5  # temp segment starts at RAM[5]
        
        if command == "push":
            if segment == "temp":
                # Push value from temp segment
                return (
                    f"//{command} {segment} {original_idx}\n"  
                    f"@{idx}\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            else:
                # Push constant value
                return (
                    f"//{command} {segment} {idx}\n"
                    f"@{idx}\n"
                    "D=A\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
        else:
            if segment == "temp":
                # Pop value to temp segment
                return (
                    f"//{command} {segment} {original_idx}\n"  
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    f"@{idx}\n"
                    "M=D\n"
                )
            else:
                # pop constant is invalid, return empty string
                return ""

    def _write_lcl_arg(self, command, segment, idx):
        """
        Handles push/pop for local, argument, this, and that segments.
        These use base pointers (LCL, ARG, THIS, THAT) + offset.
        """
        memory = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
        
        if command == "pop":
            # Pop value from stack to segment[idx]
            return (
                f"//{command} {segment} {idx}\n"
                f"@{idx}\n"
                "D=A\n"
                f"@{memory}\n"
                "D=D+M\n"
                "@R13\n"
                "M=D\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                "@R13\n"
                "A=M\n"
                "M=D\n"
            )
        else:
            # Push value from segment[idx] to stack
            return (
                f"//{command} {segment} {idx}\n"
                f"@{idx}\n"
                "D=A\n"
                f"@{memory}\n"
                "D=D+M\n"   
                "A=D\n"     
                "D=M\n"     
                "@SP\n"
                "A=M\n"
                "M=D\n"     
                "@SP\n"
                "M=M+1\n"   
            )

    def _write_pointer_static(self, command, segment, idx):
        """
        Handles push/pop for pointer and static segments.
        - pointer 0/1: THIS/THAT registers
        - static: fileName.idx (global variables)
        """
        if segment == "static":
            # Static variable: use fileName.idx format
            file_base = self.filename
            pointer_static = f"{file_base}.{idx}"
        else:
            # Pointer: 0 -> THIS, 1 -> THAT
            pointer_static = "THIS" if idx == 0 else "THAT"
        
        if command == "push":
            # Push value from static or pointer
            return (
                f"//{command} {segment} {idx}\n"
                f"@{pointer_static}\n"
                "D=M\n"
                "@SP\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n"
            )
        else:
            # Pop value to static or pointer
            return (
                f"//{command} {segment} {idx}\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "D=M\n"
                f"@{pointer_static}\n"
                "M=D\n"
            )

    def _writeReturnAddr(self, label):
        """
        Helper to push return address onto stack.
        """
        return (
            f"// push return address\n"
            f"@{label}\n"
            "D=A\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )
    
    def _savedCallerFrame(self, segment):
        """
        Helper to save caller's frame segment onto stack.
        """
        return (
            f"// push {segment}\n"
            f"@{segment}\n"
            "D=M\n"
            "@SP\n"
            "A=M\n"
            "M=D\n"
            "@SP\n"
            "M=M+1\n"
        )

    def _repositiningARG(self, nArgs):
        """
        Helper to reposition ARG pointer for called function.
        ARG = SP - nArgs - 5
        """
        return (
            f"// ARG = SP - {nArgs} - 5\n"
            "@SP\n"
            "D=M\n"
            f"@{nArgs+5}\n"
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
        )
    
    def _repositiningLCL(self):
        """
        Helper to reposition LCL pointer for called function.
        LCL = SP
        """
        return (
            "// LCL = SP\n"
            "@SP\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
        )

    def _reconnectSavedCallerFrame(self, segment):
        """
        Helper to restore caller's frame segment from endFrame.
        """
        return (
            f"// restore {segment}\n"
            "@R13\n"
            "AM=M-1\n"
            "D=M\n"
            f"@{segment}\n"
            "M=D\n"
        )
        
    def write(self, str):
        """
        Writes the given string to the output file.
        """
        self.file.write(str)
    
    def close(self):
        """
        Writes an infinite loop at the end of the file and closes it.
        This prevents the program from executing random memory after completion.
        """
        self.file.write(
            "\n(INFINITE_LOOP)\n"
            "@INFINITE_LOOP\n"
            "0;JMP\n"
        )
        self.file.close()