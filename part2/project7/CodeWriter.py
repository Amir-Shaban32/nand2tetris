from Parser import *
import os
class CodeWriter:
    """
    Translates VM commands into Hack assembly code and writes to the output file.
    """

    def __init__(self, file_name):
        # Open the output .asm file for writing
        self.file = open(file_name, "w")
        self.label_counter = 0  # Used for generating unique labels in comparison commands
        self.file_name = file_name  # Used for static variable naming

    def writeArithmetic(self, command):
        """
        Writes assembly code for arithmetic and logical VM commands.
        """
        if command == "add":
            # Pop two values, add, push result
            self.file.write(
                "//add\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=D+M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "sub":
            # Pop two values, subtract, push result
            self.file.write(
                "//sub\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=M-D\n"
                "@SP\nM=M+1\n"
            )
        elif command == "neg":
            # Negate the top value on the stack
            self.file.write(
                "//neg\n"
                "@SP\nM=M-1\nA=M\nM=-M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "and":
            # Pop two values, bitwise AND, push result
            self.file.write(
                "//and\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=D&M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "or":
            # Pop two values, bitwise OR, push result
            self.file.write(
                "//or\n"
                "@SP\nM=M-1\nA=M\nD=M\n"
                "@SP\nM=M-1\nA=M\nM=D|M\n"
                "@SP\nM=M+1\n"
            )
        elif command == "not":
            # Bitwise NOT of the top value on the stack
            self.file.write(
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
        Dispatches to the appropriate helper based on segment.
        """
        asm = None
        if segment in ("constant", "temp"):
            asm = self._write_cons_temp(command, segment, idx)
        elif segment in ("static", "pointer"):
            asm = self._write_pointer_static(command, segment, idx)
        elif segment in ("local", "argument", "this", "that"):
            asm = self._write_lcl_arg(command, segment, idx)
        self.file.write(asm)

    # ====== __helper__ functions below ======

    def _write_comparison(self, command):
        """
        Writes assembly code for comparison commands: eq, gt, lt.
        Uses unique labels for branching.
        """
        jump = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
        lable_true = f"{command.upper()}_TRUE_{self.label_counter}"  
        lable_end = f"{command.upper()}_END_{self.label_counter}"    
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
@{lable_true}
D;{jump}
//false case
@SP
A=M
M=0
@{lable_end}
0;JMP
//true case
({lable_true})
@SP
A=M
M=-1
({lable_end})
@SP
M=M+1
"""
        self.file.write(asm)

    def _write_cons_temp(self, command, segment, idx):
        """
        Handles push/pop for constant and temp segments.
        - constant: push only (pushes a value)
        - temp: push/pop to RAM[5-12]
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
        These use base pointers (LCL, ARG, THIS, THAT).
        """
        memory = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
        if command == "pop":
            # pop value from segment base + idx
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
            # FIXED: push value from segment base + idx to stack
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
        - pointer 0/1: THIS/THAT
        - static: fileName.idx
        """
        if segment == "static":
            # Static variable: use fileName.idx
            file_base = os.path.basename(self.file_name).replace('.asm', '')
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

    def close(self):
        """
        Writes an infinite loop at the end of the file and closes it.
        """
        self.file.write(
            "\n(END)\n"
            "@END\n"
            "0;JMP\n"
        )
        self.file.close()